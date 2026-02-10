from dotenv import load_dotenv
import os
load_dotenv()
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
import requests


class RealTimeSearchToolInput(BaseModel):
    """Input schema for RealTimeSearchTool."""
    query: str = Field(
        ...,
        description="The search query to look up real-time travel information for."
    )


class RealTimeSearchTool(BaseTool):
    name: str = "Generic Travel Information Lookup"
    description: str = (
        "Fetches comprehensive, real-time travel information based on queries "
        "using the Perplexity API. Returns detailed results with source citations."
    )
    args_schema: type[BaseModel] = RealTimeSearchToolInput
    api_key: str = os.getenv('PERPLEXITY_API_KEY')

    def _run(self, query: str) -> str:
        try:
            url = "https://api.perplexity.ai/chat/completions"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }

            data = {
                "model": "sonar-pro",
                "messages": [
                    {"role": "system", "content": "You are a senior travel research expert providing detailed, personalized guides."},
                    {"role": "user", "content": query}
                ],
                "max_tokens": 16384,
                "temperature": 0.2,
                "top_p": 0.9,
                "return_citations": True,
                "return_images": False,
                "return_related_questions": False,
                "search_recency_filter": "month",
                "stream": False,
                "presence_penalty": 0,
                "frequency_penalty": 1
            }

            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            response_data = response.json()

            if response_data.get("choices"):
                content = response_data["choices"][0]["message"]["content"]

                # Append source citations if available
                citations = response_data.get("citations")
                if citations:
                    citation_lines = [f"[{i+1}] {cite}" for i, cite in enumerate(citations)]
                    content += "\n\nSources:\n" + "\n".join(citation_lines)

                return content
            else:
                return "No comprehensive travel information available for the provided query."

        except requests.RequestException as e:
            return f"Error fetching data from Perplexity API: {str(e)}"
        except Exception as ex:
            return f"An unexpected error occurred: {str(ex)}"
