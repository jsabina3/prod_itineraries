from typing import ClassVar
from crewai_tools import BaseTool
import requests
from bs4 import BeautifulSoup
import base64


class CivitatisActivityTool(BaseTool):
    name: str = "Civitatis Activity Lookup"
    description: str = "Fetches top 3 activities and their respective links from Civitatis for a given city."
    headers: ClassVar[dict] = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:92.0) Gecko/20100101 Firefox/92.0'
    }

    def _run(self, departure_city_language: str, city_in_english: str) -> str:
        """Fetches top 3 activities and links for a given city. The links will be provided in the language of the city of origin (departure city) if available."""
        activities, links = self.fetch_activities_and_links(city_in_english, departure_city_language)

        # Formatting the result to return it as a string response
        response = f"Top 3 activities for {city_in_english.capitalize()}:\n"
        for i, activity in enumerate(activities[:3]):
            link = links.get(activity, 'Not found')
            response += f"{i+1}. {activity}: {link}\n"

        return response

    def get_language_code(self, language):
        """Returns the Civitatis language code for a given language."""
        language_codes = {
            'Spanish': 'ES',
            'es': 'ES',
            'French': 'FR',
            'fr': 'FR',
            'Italian': 'IT',
            'it': 'IT',
        }
        return language_codes.get(language, 'EN')

    def get_city_link_origin_language(self, english_url, language):
        """Converts an English Civitatis activity URL to its version in the desired language."""
        try:
            # Enabling SSL verification
            response = requests.get(english_url, headers=self.headers)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')
            language_code = self.get_language_code(language)

            span_element = soup.find('span', class_='js-link', attrs={'data-value': language_code})

            if span_element:
                data_loc_value = span_element['data-loc']
                decoded_link = base64.b64decode(data_loc_value).decode('utf-8')
                return decoded_link
            else:
                return english_url

        except requests.exceptions.RequestException as e:
            print(f"Error fetching link in {language}: {e}")
            return english_url


    def fetch_city_activities(self, city, departure_city_language):
        """Fetches top 5 activities for a given city from Civitatis."""
        city_url = city.replace(" ", "-").lower()
        website = f"https://www.civitatis.com/en/{city_url}"

        final_url = self.get_city_link_origin_language(website, departure_city_language)

        website = f"{final_url}/?sort=pod"

        try:
            response = requests.get(website, headers=self.headers, verify=False)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')
            titles = soup.find_all('h2', class_='comfort-card__title')

            activities = [title.get_text(strip=True) for title in titles][:5]

            # Fill with empty strings if less than 5 activities
            while len(activities) < 5:
                activities.append('')

            return activities, website

        except Exception as e:
            print(f"Error fetching activities for {city}: {e}")
            return [''] * 5, website

    def get_activity_links(self, city, activities, website):
        """Fetches activity links from the Civitatis website for the given city."""
        url_base = f'{website}/?sort=pod'

        try:
            response = requests.get(url_base, headers=self.headers, verify=False)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')
            found_links = {}

            # Search for links matching each activity
            for activity in activities:
                if activity:
                    found = False
                    for link in soup.find_all('a', href=True):
                        if activity.lower() in link.text.lower():
                            found_links[activity] = f"https://www.civitatis.com{link['href']}?aid=2264"
                            found = True
                            break
                    if not found:
                        found_links[activity] = 'Not found'

            return found_links

        except Exception as e:
            print(f"Error fetching activity links for {city}: {e}")
            return {activity: 'Not found' for activity in activities}

    def fetch_activities_and_links(self, city, departure_city_language):
        """Fetch both activities and their links for a given city."""
        activities, website = self.fetch_city_activities(city, departure_city_language)
        links = self.get_activity_links(city, activities, website)
        return activities, links