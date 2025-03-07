from dotenv import load_dotenv
import os
import requests
from crewai_tools import BaseTool

load_dotenv()

class AccuWeatherTool(BaseTool):
    name: str = "OpenWeather Lookup"
    description: str = "Looks up current weather conditions and 5-day forecast for a given location using OpenWeather API"
    api_key: str = os.getenv('OPENWEATHER_API_KEY')

    def _run(self, location: str) -> str:
        try:
            # Get location coordinates
            geocoding_url = "http://api.openweathermap.org/geo/1.0/direct"
            params = {
                "q": location,
                "limit": 1,
                "appid": self.api_key
            }
            response = requests.get(geocoding_url, params=params)
            response.raise_for_status()
            location_data = response.json()

            if not location_data:
                return f"No location found for '{location}'"

            lat = location_data[0]["lat"]
            lon = location_data[0]["lon"]

            # Get current weather
            weather_url = "https://api.openweathermap.org/data/2.5/weather"
            params = {
                "lat": lat,
                "lon": lon,
                "units": "metric",
                "appid": self.api_key
            }
            response = requests.get(weather_url, params=params)
            response.raise_for_status()
            current_weather = response.json()

            temperature = current_weather["main"]["temp"]
            weather_description = current_weather["weather"][0]["description"]

            # Get 5-day forecast
            forecast_url = "https://api.openweathermap.org/data/2.5/forecast"
            params = {
                "lat": lat,
                "lon": lon,
                "units": "metric",
                "cnt": 40,  # OpenWeather provides data in 3-hour intervals; 40 intervals cover 5 days
                "appid": self.api_key
            }
            response = requests.get(forecast_url, params=params)
            response.raise_for_status()
            forecast_data = response.json()

            forecast_list = []
            for entry in forecast_data["list"]:
                date_time = entry["dt_txt"]
                temp = entry["main"]["temp"]
                description = entry["weather"][0]["description"]
                forecast_list.append(f"{date_time}: {description}, Temp: {temp}°C")

            forecast_summary = "\n".join(forecast_list)

            return (f"Current weather in {location}: {weather_description}, Temperature: {temperature}°C\n"
                    f"5-Day Forecast:\n{forecast_summary}")

        except requests.RequestException as e:
            return f"Error fetching weather data: {str(e)}"
