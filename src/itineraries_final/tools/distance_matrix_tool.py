from dotenv import load_dotenv
import os
import json
import re
import requests
from urllib.parse import quote
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

# Load environment variables
load_dotenv()


class LocationStatusDistanceToolInput(BaseModel):
    """Input schema for LocationStatusDistanceTool."""
    locations: str = Field(
        ...,
        description="A comma-separated list of locations in order, e.g.: 'Hotel Marriott Rome, Colosseum Rome, Trevi Fountain Rome, Vatican City'."
    )


class LocationStatusDistanceTool(BaseTool):
    name: str = "Location Status and Distance Tool"
    description: str = (
        "Retrieves detailed directions between consecutive locations using the Google Maps API. "
        "Input must be a comma-separated list of locations in order, e.g.: "
        "'Hotel Marriott Rome, Colosseum Rome, Trevi Fountain Rome, Vatican City'."
    )
    args_schema: type[BaseModel] = LocationStatusDistanceToolInput
    api_key: str = os.getenv('GOOGLE_MAPS_API_KEY')

    # Distance threshold in meters below which walking directions are preferred
    walking_threshold_m: int = 1500

    def _parse_locations(self, locations_input: str) -> list:
        """Parse locations from a string input (comma-separated or JSON list)."""
        text = locations_input.strip()

        # Try JSON list first
        try:
            parsed = json.loads(text)
            if isinstance(parsed, list):
                return [loc.strip() for loc in parsed if isinstance(loc, str) and loc.strip()]
        except (json.JSONDecodeError, TypeError):
            pass

        # Try comma-separated
        if ',' in text:
            return [loc.strip() for loc in text.split(',') if loc.strip()]

        # Try newline-separated
        if '\n' in text:
            return [loc.strip() for loc in text.split('\n') if loc.strip()]

        # Single location — not useful but avoid crashing
        return [text] if text else []

    def _get_directions(self, origin: str, destination: str, mode: str = "transit") -> dict:
        """Retrieve directions and detailed steps between two locations."""
        directions_url = "https://maps.googleapis.com/maps/api/directions/json"
        params = {
            "origin": origin,
            "destination": destination,
            "mode": mode,
            "key": self.api_key
        }
        response = requests.get(directions_url, params=params)
        response.raise_for_status()
        return response.json()

    def _parse_distance_meters(self, directions: dict) -> int | None:
        """Extract the total distance in meters from a directions response."""
        try:
            return directions['routes'][0]['legs'][0]['distance']['value']
        except (KeyError, IndexError):
            return None

    def _strip_html(self, text: str) -> str:
        """Remove HTML tags from a string."""
        return re.sub(r'<[^>]+>', '', text)

    def _format_transit_detail(self, step: dict) -> str:
        """Format a transit step with line name, vehicle type, and stop details."""
        details = step.get('transit_details', {})
        line = details.get('line', {})
        line_name = line.get('short_name') or line.get('name', '')
        vehicle_name = line.get('vehicle', {}).get('name', '')
        departure_stop = details.get('departure_stop', {}).get('name', '')
        arrival_stop = details.get('arrival_stop', {}).get('name', '')
        num_stops = details.get('num_stops', '')

        parts = []
        if vehicle_name and line_name:
            parts.append(f"Take {vehicle_name} {line_name}")
        elif vehicle_name:
            parts.append(f"Take {vehicle_name}")
        elif line_name:
            parts.append(f"Take line {line_name}")
        else:
            parts.append("Transit")

        if departure_stop and arrival_stop:
            parts.append(f"from {departure_stop} to {arrival_stop}")
        elif departure_stop:
            parts.append(f"from {departure_stop}")

        if num_stops:
            parts.append(f"({num_stops} stops)")

        distance = step.get('distance', {}).get('text', '')
        duration = step.get('duration', {}).get('text', '')
        if distance and duration:
            parts.append(f"— {distance}, {duration}")

        return " ".join(parts)

    def _format_directions(self, origin: str, destination: str, directions: dict, mode: str) -> str:
        """Format the directions into a detailed textual output."""
        steps_output = []
        if directions.get('routes'):
            route = directions['routes'][0]
            leg = route['legs'][0]
            mode_label = "🚶 Walking" if mode == "walking" else "🚌 Transit"
            steps_output.append(f"\n\nDirections from {origin} to {destination} ({mode_label})")
            steps_output.append(f"Distance: {leg['distance']['text']}, Duration: {leg['duration']['text']}")

            # Extract fare information for transit routes
            fare = route.get('fare')
            if fare:
                steps_output.append(f"Estimated fare: {fare.get('text', 'N/A')}")

            for step in leg['steps']:
                travel_mode = step.get('travel_mode', '')
                instruction = self._strip_html(step.get('html_instructions', ''))
                distance = step.get('distance', {}).get('text', 'N/A')
                duration = step.get('duration', {}).get('text', 'N/A')

                if travel_mode == 'TRANSIT':
                    transit_info = self._format_transit_detail(step)
                    steps_output.append(f"  🚇 {transit_info}")
                elif travel_mode == 'WALKING':
                    steps_output.append(f"  🚶 {instruction} ({distance}, {duration})")
                else:
                    steps_output.append(f"  {travel_mode}: {instruction} ({distance}, {duration})")

            # Add Google Maps link for the route
            origin_encoded = quote(origin, safe='')
            destination_encoded = quote(destination, safe='')
            steps_output.append(
                f"\nhttps://www.google.com/maps/dir/?api=1&origin={origin_encoded}&destination={destination_encoded}&travelmode={mode}"
            )
            steps_output.append("\n" + "_" * 60 + "\n")
        else:
            status = directions.get('status', 'UNKNOWN')
            steps_output.append(f"Route not found from {origin} to {destination} (API status: {status})")

        return "\n".join(steps_output)

    def _run(self, locations: str) -> str:
        """Generate detailed directions for each consecutive pair of locations.

        Args:
            locations: A comma-separated string or JSON list of locations in order.
        """
        if not self.api_key:
            return "Google Maps API key not set. Please set your API key in environment variables."

        parsed_locations = self._parse_locations(locations)

        if len(parsed_locations) < 2:
            return f"At least 2 locations are required to get directions. Received: {locations}"

        results = []
        for i in range(len(parsed_locations) - 1):
            origin = parsed_locations[i]
            destination = parsed_locations[i + 1]
            try:
                # First, get transit directions
                directions = self._get_directions(origin, destination, mode="transit")
                mode = "transit"

                # If distance is short, prefer walking directions
                distance_m = self._parse_distance_meters(directions)
                if distance_m is not None and distance_m <= self.walking_threshold_m:
                    walking_directions = self._get_directions(origin, destination, mode="walking")
                    if walking_directions.get('routes'):
                        directions = walking_directions
                        mode = "walking"

                formatted_directions = self._format_directions(origin, destination, directions, mode)
                results.append(formatted_directions)
            except requests.RequestException as e:
                results.append(f"Error getting directions from {origin} to {destination}: {str(e)}")
            except Exception as e:
                results.append(f"Unexpected error for {origin} -> {destination}: {str(e)}")

        return "\n".join(results)
