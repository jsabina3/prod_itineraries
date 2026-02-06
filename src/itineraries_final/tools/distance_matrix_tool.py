from dotenv import load_dotenv
import os
import json
import re
import requests
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

    def _get_place_id(self, location: str) -> str:
        """Retrieve place ID for a location."""
        geocode_url = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {
            "address": location,
            "key": self.api_key
        }
        response = requests.get(geocode_url, params=params)
        response.raise_for_status()
        geocode_data = response.json()

        # Extract place_id if available
        if geocode_data.get('results'):
            return geocode_data['results'][0].get('place_id')
        return None

    def _get_directions(self, origin: str, destination: str) -> dict:
        """Retrieve directions and detailed steps between two locations."""
        directions_url = "https://maps.googleapis.com/maps/api/directions/json"
        params = {
            "origin": origin,
            "destination": destination,
            "mode": "transit",
            "key": self.api_key
        }
        response = requests.get(directions_url, params=params)
        response.raise_for_status()
        return response.json()

    def _format_directions(self, origin: str, destination: str, directions: dict) -> str:
        """Format the directions into a detailed textual output."""
        steps_output = []
        if directions.get('routes'):
            leg = directions['routes'][0]['legs'][0]
            steps_output.append(f"\n\nDirections from {origin} to {destination}")
            steps_output.append(f"\n\nDistance: {leg['distance']['text']}, Duration: {leg['duration']['text']}")

            for step in leg['steps']:
                travel_mode = step.get('travel_mode', '')
                instruction = step.get('html_instructions', '')
                distance = step.get('distance', {}).get('text', 'N/A')
                duration = step.get('duration', {}).get('text', 'N/A')
                steps_output.append(f"{travel_mode}: {instruction} ({distance}, {duration})")

            # Add Google Maps link for the route
            steps_output.append(
                f"\nhttps://www.google.com/maps/dir/?api=1&origin={origin.replace(' ', '%20')}&destination={destination.replace(' ', '%20')}&travelmode=transit"
            )
            steps_output.append("\n\n" + "_"*60 + "\n")
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
        # Only get directions between consecutive pairs (A->B, B->C, C->D, ...)
        for i in range(len(parsed_locations) - 1):
            origin = parsed_locations[i]
            destination = parsed_locations[i + 1]
            try:
                directions = self._get_directions(origin, destination)
                formatted_directions = self._format_directions(origin, destination, directions)
                results.append(formatted_directions)
            except requests.RequestException as e:
                results.append(f"Error getting directions from {origin} to {destination}: {str(e)}")
            except Exception as e:
                results.append(f"Unexpected error for {origin} -> {destination}: {str(e)}")

        return "\n".join(results)