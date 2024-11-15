from dotenv import load_dotenv
import os
load_dotenv()
from crewai_tools import BaseTool
import requests

class RealTimeSearchTool(BaseTool):
    name: str = "Travel Information Lookup"
    description: str = "Fetches comprehensive travel information for any specified destination using the Perplexity API"
    api_key: str = os.getenv('PERPLEXITY_API_KEY')

    def _run(self, destination: str, names: str, num_travelers: int, start_date: str, end_date: str, flight_outward_arrival_time: str, flight_return_departure_time: str, hotel_name: str, breakfast_included: str, flight_data: str, traveler_age: int, ages: str, origin: str) -> str:
        try:
            url = "https://api.perplexity.ai/chat/completions"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            # Constructing a dynamic query based on the inputs
            query_content = f"""
            I need a comprehensive travel guide for {destination} taking into account the following indications:
            {num_travelers} people named {names} aged {ages} are Wayners from {origin} travelling to 
            {destination} between {start_date} arriving at {flight_outward_arrival_time} 
            and {end_date} departing at {flight_return_departure_time} from {destination}'s airport. 
            The travellers are staying at {hotel_name}, which is already booked for {names}. 
            Is breakfast included in the hotel? {breakfast_included}. The flights are also booked:
            {flight_data}. 

            Look up date-specific events, either cultural, entertainment or sports, such as:
            - Concerts.
            - Exhibitions.
            - Matches.
            - Theater plays.
            - Music shows.
            - Immersive experiences.

            Ensure they are a good fit for the travellers specifications.
            """

            data = {
                "model": "llama-3.1-sonar-huge-128k-online",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a senior travel agency research expert who excels at research and personalization."
                    },
                    {
                        "role": "user",
                        "content": query_content
                    }
                ],
                "max_tokens": 1000,
                "temperature": 0.2,
                "top_p": 0.9,
                "return_citations": 0,
                "search_domain_filter": [
                    "perplexity.ai"
                ],
                "return_images": 0,
                "return_related_questions": 0,
                "search_recency_filter": "month",
                "top_k": 0,
                "stream": 0,
                "presence_penalty": 0,
                "frequency_penalty": 1
            }

            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            response_data = response.json()

            if "choices" in response_data and response_data["choices"]:
                return response_data["choices"][0]["message"]["content"]
            else:
                return "No response available for the provided input."

        except requests.RequestException as e:
            return f"Error fetching data from Perplexity API: {str(e)}"