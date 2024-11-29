import requests
import os
from helpers import *
import dotenv

dotenv.load_dotenv()

API_TOKEN = os.getenv('PIPEDRIVE_API_TOKEN')
if not API_TOKEN:
    raise EnvironmentError("Please set the PIPEDRIVE_API_TOKEN environment variable.")

headers = {
    'x-api-token': API_TOKEN
}
BASE_URL = 'https://pland3.pipedrive.com'
DATA_FILE = "products_of_deals.json"

deals = load_file("deals.json")

products = []

for element in deals:
    if element["products_count"] != 0:
        
        deal_id = element["deal_id"]
        endpoint = f"/api/v2/deals/{deal_id}/products"
        response = requests.get(BASE_URL+endpoint, headers=headers)
        
        print("Request for", deal_id)
        
        data = response.json()
        data_items = data.get("data")
        
        for item in data_items:
            products.append({
                "deal_id": item.get("deal_id"),
                "product_id": item.get("product_id"),
                "product_attachment_id": item.get("id"),
                "name": item.get("name"),
                "is_enabled": item.get("is_enabled"),
                "billing_frequency": item.get("billing_frequency"),
            })
        
        save_data(products, "products.json")




