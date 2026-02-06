from dotenv import load_dotenv
import os
load_dotenv()
from crewai.tools import BaseTool
import requests
import json
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed

class ViatorTopProductsTool(BaseTool):
    name: str = "Viator Lookup"
    description: str = "Searches for tours and activities with their respective availabilities in a given destination using the Viator API."
    api_key: str = os.getenv('EXP_API_KEY')

    def _fetch_product_options(self, product_code: str, headers: dict) -> dict:
        """Fetch product options for a single product."""
        url = f"https://api.viator.com/partner/products/{product_code}"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()

    def _fetch_availability(self, product_code: str, headers: dict) -> dict:
        """Fetch availability schedule for a single product."""
        url = f"https://api.viator.com/partner/availability/schedules/{product_code}"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()

    def _process_availability(self, availability_data: dict, start_date: str, end_date: str) -> dict:
        """Process availability data for a product and return availability by product option."""
        product_options_availability = {}

        for bookable_item in availability_data.get('bookableItems', []):
            product_option_code = bookable_item['productOptionCode']
            product_options_availability[product_option_code] = []

            for season in bookable_item.get('seasons', []):
                if "startDate" not in season:
                    continue
                if "endDate" not in season:
                    start_date_obj = datetime.strptime(season['startDate'], "%Y-%m-%d")
                    end_date_obj = start_date_obj + timedelta(days=384)
                    season['endDate'] = end_date_obj.strftime("%Y-%m-%d")

                if season['startDate'] <= end_date and season['endDate'] >= start_date:
                    season_with_code = season.copy()
                    season_with_code['productOptionCode'] = product_option_code
                    product_options_availability[product_option_code].append(season_with_code)

        product_availabilities = {}

        for product_option_code, seasons in product_options_availability.items():
            result = {}

            for season in seasons:
                season_start_date = datetime.strptime(season["startDate"], "%Y-%m-%d")
                season_end_date = datetime.strptime(season["endDate"], "%Y-%m-%d")

                requested_start_date = datetime.strptime(start_date, "%Y-%m-%d")
                requested_end_date = datetime.strptime(end_date, "%Y-%m-%d")
                overlap_start_date = max(season_start_date, requested_start_date)
                overlap_end_date = min(season_end_date, requested_end_date)

                if overlap_start_date > overlap_end_date:
                    continue

                delta = overlap_end_date - overlap_start_date
                date_list = [overlap_start_date + timedelta(days=i) for i in range(delta.days + 1)]

                for date in date_list:
                    date_str = date.strftime("%Y-%m-%d")
                    day_of_week = date.strftime("%A").upper()
                    available_times = {}

                    for record in season.get("pricingRecords", []):
                        days_of_week = record.get("daysOfWeek")
                        if not days_of_week or day_of_week in days_of_week:
                            timed_entries = record.get("timedEntries", [])
                            if not timed_entries:
                                continue

                            for timed_entry in timed_entries:
                                is_unavailable = False
                                for unavailable in timed_entry.get("unavailableDates", []):
                                    if unavailable["date"] == date_str:
                                        is_unavailable = True
                                        break
                                if not is_unavailable:
                                    start_time = timed_entry["startTime"]
                                    prices = {}
                                    for pricingDetail in record.get("pricingDetails", []):
                                        ageBand = pricingDetail.get("ageBand")
                                        price_info = pricingDetail.get("price", {}).get("original", {})
                                        price = price_info.get("recommendedRetailPrice")
                                        if ageBand and price is not None:
                                            prices[ageBand] = price
                                    if not prices:
                                        continue
                                    if start_time in available_times:
                                        if available_times[start_time] != prices:
                                            if not isinstance(available_times[start_time], list):
                                                available_times[start_time] = [available_times[start_time]]
                                            if prices not in available_times[start_time]:
                                                available_times[start_time].append(prices)
                                    else:
                                        available_times[start_time] = prices

                    if available_times:
                        if date_str not in result:
                            result[date_str] = {}
                        result[date_str].update(available_times)

            if result:
                product_availabilities[product_option_code] = result

        return product_availabilities

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
            destination_id = destination_results[0]['id']

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

            product_codes = [p['productCode'] for p in products]

            # Step 3: Fetch product options and availability in parallel
            options_results = {}
            availability_results = {}

            with ThreadPoolExecutor(max_workers=10) as executor:
                # Submit all product options requests
                options_futures = {
                    executor.submit(self._fetch_product_options, code, headers): code
                    for code in product_codes
                }
                # Submit all availability requests
                availability_futures = {
                    executor.submit(self._fetch_availability, code, headers): code
                    for code in product_codes
                }

                # Collect product options results
                for future in as_completed(options_futures):
                    code = options_futures[future]
                    try:
                        options_results[code] = future.result()
                    except Exception:
                        options_results[code] = {}

                # Collect availability results
                for future in as_completed(availability_futures):
                    code = availability_futures[future]
                    try:
                        availability_results[code] = future.result()
                    except Exception:
                        availability_results[code] = {}

            # Step 4: Assemble product data
            product_data = []
            for value in products:
                code = value['productCode']
                options_response = options_results.get(code, {})

                option_descriptions = ''
                for option in options_response.get('productOptions', []):
                    option_description = f"Product Option {option['productOptionCode']} -> Title: {option['title']}. Description: {option['description']}."
                    option_descriptions += option_description + '\n'

                availability_data = availability_results.get(code, {})
                product_availabilities = self._process_availability(availability_data, start_date, end_date)

                product_data.append({
                    'product_code': code,
                    'product_title': value['title'],
                    'product_description': value['description'],
                    'product_options': option_descriptions,
                    'product_reviews': value.get('reviews', []),
                    'product_duration_minutes': value.get('duration', 0),
                    'product_price': value.get('pricing', {}),
                    'product_flags': value.get('flags', []),
                    'product_availability_and_pricing': product_availabilities,
                    'product_url': value['productUrl'],
                    'ageBands': options_response.get('pricingInfo', {}).get('ageBands', [])
                })

            # Remove products with empty availability
            product_data = [element for element in product_data if element['product_availability_and_pricing']]

            return f"Found products for '{destination}':\n" + json.dumps(product_data, indent=2)

        except requests.RequestException as e:
            return f"Error fetching data from Viator: {str(e)}"
        except (IndexError, KeyError, ValueError) as e:
            return f"Error processing data: {str(e)}"
