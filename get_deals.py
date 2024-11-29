import requests
import json
import os
import logging
import dotenv
from helpers import *

dotenv.load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)

# Constants
BASE_URL = 'https://pland3.pipedrive.com'
DATA_FILE = "deals.json"
ENDPOINT = "/api/v2/deals?include_fields=products_count&limit=500"

# Read the API token from an environment variable
API_TOKEN = os.getenv('PIPEDRIVE_API_TOKEN')
if not API_TOKEN:
    raise EnvironmentError("Please set the PIPEDRIVE_API_TOKEN environment variable.")

headers = {
    'x-api-token': API_TOKEN
}

def get_all_deals_with_products(url, data_file=DATA_FILE):
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.HTTPError as e:
        logging.error(f"HTTPError: {e}")
        return None
    except ValueError as e:
        logging.error(f"JSON decode error: {e}")
        return None

    cursor = data.get("additional_data", {}).get("next_cursor", None)
    data_items = data.get("data", [])

    existing_data = load_file(data_file)

    for element in data_items:
        existing_data.append({
            "deal_id": element.get("id"),
            "products_count": element.get("products_count")
        })

    save_data(existing_data, data_file)
    return cursor



def main():
    cursor = None
    while True:
        if cursor:
            url = f"{BASE_URL}{ENDPOINT}&cursor={cursor}"
        else:
            url = f"{BASE_URL}{ENDPOINT}"
        logging.info("Fetching data...")
        cursor = get_all_deals_with_products(url)
        if cursor is None:
            break
    logging.info("Data fetching completed.")

if __name__ == "__main__":
    main()