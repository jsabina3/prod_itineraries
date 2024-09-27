from crewai_tools import BaseTool
import json
import requests
from dotenv import load_dotenv
import os

load_dotenv()

class CustomSerperDevTool(BaseTool):
    name: str = "CustomSerperDevTool"
    description: str = "A custom tool to Google stuff using Serper.dev."

    def _run(self, search_query: str) -> str:
        url = 'https://google.serper.dev/search'
        payload = json.dumps({
            "q": search_query
        })
        headers = {
            'X-API-KEY': os.getenv("SERPER_API_KEY"),
            'Content-Type': 'application/json'
        }

        try:
            response = requests.post(url, headers=headers, data=payload, verify=False)  # Disable SSL verification
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return str(e)