import os
import time
import logging
import requests
import dotenv
from helpers import load_file, save_data  # Ensure these functions are correctly defined in helpers.py

# Configure logging
logging.basicConfig(level=logging.INFO)

# Load environment variables
dotenv.load_dotenv()

API_TOKEN = os.getenv('PIPEDRIVE_API_TOKEN')
if not API_TOKEN:
    raise EnvironmentError("Please set the PIPEDRIVE_API_TOKEN environment variable.")

# Set up headers and base URL
headers = {
    'x-api-token': API_TOKEN,
    'content-type': 'application/json'
}
BASE_URL = 'https://pland3.pipedrive.com'
DATA_FILE = "test.json"

# Load products from the JSON file
products = load_file("products.json")
products.reverse()

# Record the start time
start = time.time()
changed_products = []

def product_billing_frequency(product_id):
    """Determine the billing frequency based on the product ID."""
    match product_id:
        case 1:
            return "annually"
        case 2 | 4 | 5 | 46 | 55:
            return "one-time"
        case _:
            return "monthly"

# Test the billing frequency function
# print(product_billing_frequency(4))  # Should output: one-time

try:
    with requests.Session() as session:
        for product in products:
            # Extract necessary information from the product
            deal_id = product.get("deal_id")
            product_attachment_id = product.get("product_attachment_id")
            product_id = product.get("product_id")
            product_name = product.get("name")
            product_billing_frequency_term = product_billing_frequency(product_id)
    
            body = {
                "is_enabled": True,
                "billing_frequency": product_billing_frequency_term
            }
    
            try:
                # Send PATCH request to update the product
                response = session.patch(
                    f"{BASE_URL}/api/v2/deals/{deal_id}/products/{product_attachment_id}",
                    json=body,
                    headers=headers
                )
                # Parse the response
                data = response.json()
                error_message = data.get('error', '')
    
                selected_data = {
                    "success": data.get('success', "null"),
                    "error": data.get('error', "null"),
                    "deal_id": data.get("data", {}).get('deal_id', deal_id),
                    "product_id": data.get("data", {}).get("product_id", product_id),
                    "product_attachment_id": data.get("data", {}).get("id", product_attachment_id),
                    "billing_frequency": data.get("data", {}).get("billing_frequency", product_billing_frequency_term),
                }
    
                logging.info(
                    f"Request for deal {deal_id} and product {product_id} "
                    f"completed with status code {response.status_code}. {error_message}"
                )
            except Exception as e:
                logging.error(f"Something went wrong with deal {deal_id} - error: {e}")
                # Define selected_data with error information
                selected_data = {
                    "success": False,
                    "error": str(e),
                    "deal_id": deal_id,
                    "product_id": product_id,
                    "product_attachment_id": product_attachment_id
                }
            # Append selected_data to the list regardless of success or failure
            changed_products.append(selected_data)
except KeyboardInterrupt:
    logging.info("Process interrupted by user. Saving data before exiting.")
except Exception as e:
    logging.error(f"An unexpected error occurred: {e}")
finally:
    # Save the data after processing all products or upon interruption
    try:
        save_data(changed_products, "updated_products.json")
        logging.info("Data saved successfully.")
    except Exception as save_error:
        logging.error(f"Failed to save data: {save_error}")

# Record the end time and print the duration
end = time.time()
print(f"Processed {len(products)} products in {end - start:.2f} seconds.")