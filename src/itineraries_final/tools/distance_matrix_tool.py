from dotenv import load_dotenv
import os
import requests
from crewai_tools import BaseTool

# Load environment variables
load_dotenv()

class LocationStatusDistanceTool(BaseTool):
    name: str = "Location Status and Distance Tool"
    description: str = "Retrieves detailed directions between given locations using the Google Maps API."
    api_key: str = os.getenv('GOOGLE_MAPS_API_KEY')

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
        if geocode_data['results']:
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
        if directions['routes']:
            leg = directions['routes'][0]['legs'][0]
            steps_output.append(f"\n\nDirections from {origin} to {destination}")
            steps_output.append(f"\n\nDistance: {leg['distance']['text']}, Duration: {leg['duration']['text']}")

            for step in leg['steps']:
                travel_mode = step['travel_mode']
                instruction = step['html_instructions']
                distance = step['distance']['text']
                duration = step['duration']['text']
                steps_output.append(f"{travel_mode}: {instruction} ({distance}, {duration})")

            # Add Google Maps link for the route
            steps_output.append(
                f"\nhttps://www.google.com/maps/dir/?api=1&origin={origin.replace(' ', '%20')}&destination={destination.replace(' ', '%20')}&travelmode=transit"
            )
            steps_output.append("\n\n" + "_"*60 + "\n")
        else:
            steps_output.append(f"Route not found from {origin} to {destination}")

        return "\n".join(steps_output)

    def _run(self, locations: list) -> str:
        """Generate detailed directions for each pair of locations."""
        if not self.api_key:
            return "Google Maps API key not set. Please set your API key in environment variables."

        results = []
        for i, origin in enumerate(locations):
            for j, destination in enumerate(locations):
                if i != j:
                    directions = self._get_directions(origin, destination)
                    formatted_directions = self._format_directions(origin, destination, directions)
                    results.append(formatted_directions)

        return "\n".join(results)