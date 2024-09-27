from crewai_tools import BaseTool
import json
import requests
from dotenv import load_dotenv
import os
load_dotenv()
from crewai_tools import BaseTool
import requests

from crewai_tools import BaseTool
import requests

class AccuWeatherTool(BaseTool):
    name: str = "AccuWeather Lookup"
    description: str = "Looks up current weather conditions and 5-day forecast for a given location using AccuWeather API"
    api_key: str = os.getenv('ACCUWEATHER_API_KEY')

    def _run(self, location: str) -> str:
        try:
            # Get location key
            location_url = f"http://dataservice.accuweather.com/locations/v1/cities/search"
            params = {
                "apikey": self.api_key,
                "q": location
            }
            response = requests.get(location_url, params=params)
            response.raise_for_status()
            location_data = response.json()

            if not location_data:
                return f"No location found for '{location}'"

            location_key = location_data[0]["Key"]

            # Get current conditions
            conditions_url = f"http://dataservice.accuweather.com/currentconditions/v1/{location_key}"
            params = {"apikey": self.api_key, "details": "true"}
            response = requests.get(conditions_url, params=params)
            response.raise_for_status()
            weather_data = response.json()

            if not weather_data:
                return f"No weather data available for '{location}'"

            current_weather = weather_data[0]
            temperature = current_weather["Temperature"]["Metric"]["Value"]
            weather_text = current_weather["WeatherText"]

            # Get 5-day forecast
            forecast_url = f"http://dataservice.accuweather.com/forecasts/v1/daily/5day/{location_key}"
            params = {"apikey": self.api_key, "metric": "true"}
            response = requests.get(forecast_url, params=params)
            response.raise_for_status()
            forecast_data = response.json()

            forecast_list = []
            for day in forecast_data["DailyForecasts"]:
                date = day["Date"]
                day_weather_text = day["Day"]["IconPhrase"]
                max_temp = day["Temperature"]["Maximum"]["Value"]
                min_temp = day["Temperature"]["Minimum"]["Value"]
                forecast_list.append(f"{date}: {day_weather_text}, Max Temp: {max_temp}°C, Min Temp: {min_temp}°C")

            forecast_summary = "\n".join(forecast_list)

            return (f"Current weather in {location}: {weather_text}, Temperature: {temperature}°C\n"
                    f"5-Day Forecast:\n{forecast_summary}")

        except requests.RequestException as e:
            return f"Error fetching weather data: {str(e)}"