from crewai_tools import BaseTool
import json
import requests
from dotenv import load_dotenv
import os
load_dotenv()
from crewai_tools import BaseTool
import requests
from typing import Optional

class ExaSearchTool(BaseTool):
    name: str = "Exa Search"
    description: str = "Performs a general-purpose web search using the Exa API and gets a list of results"

    def _run(self, query: str) -> str:
        headers = {
            "x-api-key": os.getenv('EXA_API_KEY'),
            "Content-Type": "application/json"
        }

        payload = {
            "query": query,
            "numResults": 10,
            "useAutoprompt": True
        }

        try:
            response = requests.post("https://api.exa.ai/search", json=payload, headers=headers, verify = False)
            response.raise_for_status()
            results = response.json()

            if 'results' not in results or not results['results']:
                return f"No results found for query: {query}"

            formatted_results = ""
            for result in results['results']:
                formatted_results += f"- Title: {result['title']}\n"
                formatted_results += f"  URL: {result['url']}\n"
                if 'snippet' in result:
                    formatted_results += f"  Snippet: {result['snippet']}\n"
                formatted_results += "\n"

            return f"Top {10} results for '{query}':\n\n{formatted_results}"

        except requests.RequestException as e:
            return f"Error occurred while searching: {str(e)}"

    def _parse_input(self, query: str) -> tuple:
        return query, 10