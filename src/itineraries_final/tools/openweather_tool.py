from dotenv import load_dotenv
import os
import requests
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

load_dotenv()


class OpenWeatherToolInput(BaseModel):
    """Input schema for OpenWeatherTool."""
    location: str = Field(
        ...,
        description="The city or location to get the weather forecast for, e.g. 'Paris' or 'Rome, Italy'."
    )


class OpenWeatherTool(BaseTool):
    name: str = "OpenWeather Forecast"
    description: str = (
        "Looks up current weather conditions and a 5-day forecast for a given location "
        "using the OpenWeather API. Returns daily summaries with high/low temperatures, "
        "humidity, wind speed, and dominant weather condition."
    )
    args_schema: type[BaseModel] = OpenWeatherToolInput
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
                "cnt": 40,  # 3-hour intervals covering 5 days
                "appid": self.api_key
            }
            response = requests.get(forecast_url, params=params)
            response.raise_for_status()
            forecast_data = response.json()

            # Aggregate 3-hour intervals into daily summaries
            daily_forecasts: dict = {}
            for entry in forecast_data["list"]:
                date = entry["dt_txt"].split(" ")[0]
                if date not in daily_forecasts:
                    daily_forecasts[date] = {
                        "temps": [],
                        "descriptions": [],
                        "humidity": [],
                        "wind_speed": [],
                    }
                daily_forecasts[date]["temps"].append(entry["main"]["temp"])
                daily_forecasts[date]["descriptions"].append(entry["weather"][0]["description"])
                daily_forecasts[date]["humidity"].append(entry["main"]["humidity"])
                daily_forecasts[date]["wind_speed"].append(entry["wind"].get("speed", 0))

            forecast_lines = []
            for date, data in daily_forecasts.items():
                min_temp = min(data["temps"])
                max_temp = max(data["temps"])
                avg_humidity = sum(data["humidity"]) / len(data["humidity"])
                avg_wind = sum(data["wind_speed"]) / len(data["wind_speed"])
                # Most frequent weather description for the day
                dominant_desc = max(set(data["descriptions"]), key=data["descriptions"].count)
                forecast_lines.append(
                    f"{date}: {dominant_desc}, Low: {min_temp:.1f}°C, High: {max_temp:.1f}°C, "
                    f"Humidity: {avg_humidity:.0f}%, Wind: {avg_wind:.1f} m/s"
                )

            forecast_summary = "\n".join(forecast_lines)

            return (
                f"Current weather in {location}: {weather_description}, Temperature: {temperature}°C\n"
                f"5-Day Forecast (daily summary):\n{forecast_summary}"
            )

        except requests.RequestException as e:
            return f"Error fetching weather data: {str(e)}"

