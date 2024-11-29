# iterate throught all deals
# if(product count == 0) -> next

# get all products for this deal


# iterate through products
# - is_enabled = true

# match id
# case 1 -> yearly
# case 2,4,5,46,55 -> onetime
# case _ -> monthly

# - billing_frequency = return

# update deal products

import os
from helpers import *
import dotenv
import threading
import requests
import time
import logging

logging.basicConfig(level=logging.INFO)

dotenv.load_dotenv()


API_TOKEN = os.getenv('PIPEDRIVE_API_TOKEN')
if not API_TOKEN:
    raise EnvironmentError("Please set the PIPEDRIVE_API_TOKEN environment variable.")

headers = {
    'x-api-token': API_TOKEN,
    'content-type':'application/json'
}
BASE_URL = 'https://pland3.pipedrive.com'
DATA_FILE = "test.json"

products = load_file("products.json")


start = time.time()
changed_products = []

def product_billing_frequency(product_id):
    match product_id:
            case 1:
              billing_frequency = "annually"
            case 2,4,5,46,55:
              billing_frequency = "one-time"
            case _:
                billing_frequency = "monthly" 
    return billing_frequency

with requests.Session() as session:
    for product in products:
        deal_id = product["deal_id"]
        product_attachment_id = product["product_attachment_id"]
        product_id = product["product_id"]
        product_name = product["name"]

        body = {"is_enabled": True,
                "billing_frequency": product_billing_frequency(product_id)}
        try: 
            # Send PATCH request
            response = session.patch(
                f"{BASE_URL}/api/v2/deals/{deal_id}/products/{product_attachment_id}",
                json=body,
                headers=headers
            )
            # Log the result
            data = response.json()
            error_message = data.get('error', '')

            logging.info(f"Request for deal {deal_id} and product {product_id} with code {response.status_code} {error_message}")
        except Exception as e:
            logging.error(f"Request {deal_id} failed due to an unexpected error: {e}")
        changed_products.append(data)
save_data(changed_products, "changed_products.json")

end = time.time()
print(end-start)


# start = time.time()
# for i in range(0,100):
#     try:
#         response = requests.get(BASE_URL, headers=headers)
#         print(f"Request {i} completed with status code {response.status_code}")
#         # Optionally, process the response here
#     except Exception as e:
#         print(f"Request {i} failed: {e}") 
# end = time.time()
# print(end-start)
