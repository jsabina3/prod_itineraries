from dotenv import load_dotenv
import os
load_dotenv()
from crewai_tools import BaseTool
import requests
import json
from datetime import datetime, timedelta

class ViatorTopProductsTool(BaseTool):
    name: str = "Viator Lookup"
    description: str = "Searches for tours and activities with their respective availabilities in a given destination using the Viator API."
    api_key: str = os.getenv('EXP_API_KEY')

    def _run(self, destination: str, start_date: str, end_date: str) -> str:
        try:
            # Step 1: Search for the destination ID
            url = "https://api.viator.com/partner/search/freetext"
            payload = {
                "searchTerm": destination,
                "currency": "EUR",
                "searchTypes": [
                    {
                        "searchType": "DESTINATIONS",
                        "pagination": {
                            "start": 1,
                            "count": 3
                        }
                    }
                ]
            }
            headers = {
                "Accept": "application/json;version=2.0",
                "Accept-Language": "en-US",
                "exp-api-key": self.api_key
            }
            response_destination = requests.post(url, json=payload, headers=headers)
            response_destination.raise_for_status()
            destination_results = response_destination.json().get('destinations', {}).get('results', [])
            if not destination_results:
                return f"No destinations found for '{destination}'."
            destination_id = destination_results[0]['id']  # Get the first destination ID

            # Step 2: Search for products in the destination
            url = "https://api.viator.com/partner/products/search"
            payload = {
                "filtering": {
                    "destination": destination_id,
                    "lowestPrice": 5,
                    "highestPrice": 45,
                    "startDate": start_date,
                    "endDate": end_date,
                    "includeAutomaticTranslations": False,
                    "confirmationType": "INSTANT",
                    "durationInMinutes": {"from": 20, "to": 360},
                    "rating": {"from": 4, "to": 5},
                    "flags": ["LIKELY_TO_SELL_OUT"]
                },
                "sorting": {"sort": "DEFAULT", "order": "DESCENDING"},
                "pagination": {"start": 1, "count": 15},
                "currency": "EUR"
            }
            response_products = requests.post(url, json=payload, headers=headers)
            response_products.raise_for_status()
            products = response_products.json().get('products', [])
            if not products:
                return f"No products found for destination '{destination}'."

            product_data = []
            for value in products:
                # Fetch product options
                url_options = f"https://api.viator.com/partner/products/{value['productCode']}"
                response_options = requests.get(url_options, headers=headers)
                response_options.raise_for_status()
                option_descriptions = ''
                for option in response_options.json().get('productOptions', []):
                    option_description = f"Product Option {option['productOptionCode']} -> Title: {option['title']}. Description: {option['description']}."
                    option_descriptions += option_description + '\n'
                product_data.append({
                    'product_code': value['productCode'],
                    'product_title': value['title'],
                    'product_description': value['description'],
                    'product_options': option_descriptions,
                    'product_reviews': value.get('reviews', []),
                    'product_duration_minutes': value.get('duration', 0),
                    'product_price': value.get('pricing', {}),
                    'product_flags': value.get('flags', []),
                    'product_availability_and_pricing': '',
                    'product_url': value['productUrl'],
                    'ageBands': response_options.json().get('pricingInfo', {}).get('ageBands', [])
                })

            # Step 3: Get availability for each specific product
            for i in range(len(products)):
                url = f"https://api.viator.com/partner/availability/schedules/{product_data[i]['product_code']}"
                response_availability = requests.get(url, headers=headers)
                response_availability.raise_for_status()
                availability_data = response_availability.json()

                # Initialize a dictionary to store JSONs by product option
                product_options_availability = {}

                for bookable_item in availability_data.get('bookableItems', []):
                    product_option_code = bookable_item['productOptionCode']
                    # Initialize list to store availability for the current product option
                    product_options_availability[product_option_code] = []

                    for season in bookable_item.get('seasons', []):
                        # Handle missing 'startDate' and 'endDate'
                        if "startDate" not in season:
                            continue
                        if "endDate" not in season:
                            # Set endDate to startDate + 384 days
                            start_date_obj = datetime.strptime(season['startDate'], "%Y-%m-%d")
                            end_date_obj = start_date_obj + timedelta(days=384)
                            season['endDate'] = end_date_obj.strftime("%Y-%m-%d")

                        # Check if season overlaps with requested dates
                        if season['startDate'] <= end_date and season['endDate'] >= start_date:
                            season_with_code = season.copy()
                            season_with_code['productOptionCode'] = product_option_code
                            # Add each season data to the product option's list
                            product_options_availability[product_option_code].append(season_with_code)

                # Now process the availabilities for each product option separately
                product_availabilities = {}

                for product_option_code, seasons in product_options_availability.items():
                    result = {}

                    for season in seasons:
                        # Parse start and end dates
                        season_start_date = datetime.strptime(season["startDate"], "%Y-%m-%d")
                        season_end_date = datetime.strptime(season["endDate"], "%Y-%m-%d")

                        # Calculate the overlapping date range between the season and the requested dates
                        requested_start_date = datetime.strptime(start_date, "%Y-%m-%d")
                        requested_end_date = datetime.strptime(end_date, "%Y-%m-%d")
                        overlap_start_date = max(season_start_date, requested_start_date)
                        overlap_end_date = min(season_end_date, requested_end_date)

                        if overlap_start_date > overlap_end_date:
                            continue  # No overlap

                        # Generate a list of dates between overlap start and end dates
                        delta = overlap_end_date - overlap_start_date
                        date_list = [overlap_start_date + timedelta(days=i) for i in range(delta.days + 1)]

                        # Process each date
                        for date in date_list:
                            date_str = date.strftime("%Y-%m-%d")
                            day_of_week = date.strftime("%A").upper()
                            available_times = {}

                            # Check each pricing record
                            for record in season.get("pricingRecords", []):
                                # Handle missing or empty daysOfWeek
                                days_of_week = record.get("daysOfWeek")
                                if not days_of_week or day_of_week in days_of_week:
                                    # Proceed to process timedEntries
                                    timed_entries = record.get("timedEntries", [])
                                    if not timed_entries:
                                        # Handle case when timedEntries is missing or empty
                                        continue

                                    for timed_entry in timed_entries:
                                        # Assume the time is available unless marked unavailable
                                        is_unavailable = False
                                        for unavailable in timed_entry.get("unavailableDates", []):
                                            if unavailable["date"] == date_str:
                                                is_unavailable = True
                                                break
                                        if not is_unavailable:
                                            start_time = timed_entry["startTime"]
                                            # Collect prices
                                            prices = {}
                                            for pricingDetail in record.get("pricingDetails", []):
                                                ageBand = pricingDetail.get("ageBand")
                                                price_info = pricingDetail.get("price", {}).get("original", {})
                                                price = price_info.get("recommendedRetailPrice")
                                                if ageBand and price is not None:
                                                    prices[ageBand] = price
                                            if not prices:
                                                # Handle missing pricingDetails
                                                continue
                                            # Check for conflicts
                                            if start_time in available_times:
                                                # Handle price conflicts
                                                if available_times[start_time] != prices:
                                                    if not isinstance(available_times[start_time], list):
                                                        available_times[start_time] = [available_times[start_time]]
                                                    if prices not in available_times[start_time]:
                                                        available_times[start_time].append(prices)
                                            else:
                                                available_times[start_time] = prices

                            # Add the available times to the result
                            if available_times:
                                if date_str not in result:
                                    result[date_str] = {}
                                result[date_str].update(available_times)

                    if result:
                        product_availabilities[product_option_code] = result

                # Assign the availabilities dictionary to the product data
                product_data[i]['product_availability_and_pricing'] = product_availabilities

            # Remove products with empty availability
            product_data = [element for element in product_data if element['product_availability_and_pricing']]

            return f"Found products for '{destination}':\n" + json.dumps(product_data, indent=2)

        except requests.RequestException as e:
            return f"Error fetching data from Viator: {str(e)}"
        except (IndexError, KeyError, ValueError) as e:
            return f"Error processing data: {str(e)}"
