from crewai_tools import BaseTool
import os
import requests
from dotenv import load_dotenv

load_dotenv()

class YoutubeVideoSearchTool(BaseTool):
    name: str = "YouTube Video Search Tool"
    description: str = "Search for YouTube videos based on a query."

    def _run(self, query: str) -> str:
        api_key = os.getenv('YOUTUBE_API_KEY')
        if not api_key:
            return "Error: YouTube API key not found."

        search_url = "https://www.googleapis.com/youtube/v3/search"
        params = {
            'part': 'snippet',
            'q': query,
            'key': api_key,
            'type': 'video',
            'maxResults': 5
        }
        response = requests.get(search_url, params=params)
        if response.status_code == 200:
            videos = response.json().get('items', [])
            results = []
            for video in videos:
                video_info = {
                    'title': video['snippet']['title'],
                    'url': f"https://www.youtube.com/watch?v={video['id']['videoId']}",
                    'description': video['snippet']['description']
                }
                results.append(video_info)
            return results
        else:
            return f"Error: {response.status_code}, {response.text}"