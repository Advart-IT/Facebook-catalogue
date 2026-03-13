import requests
import time
import pandas as pd
from io import StringIO
import logging
import sys

# Configure logging for this script
logger = logging.getLogger('aalam_fetcher')
logger.setLevel(logging.INFO)

# Remove any existing handlers
if logger.hasHandlers():
    logger.handlers.clear()

file_handler = logging.FileHandler('logs/aalam_fetcher.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Also log to stdout so `run_all` captures these messages in per-script logs
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

# Constants
RETRIES = 30  # Number of retries for API calls
RETRY_DELAY = 5  # Delay in seconds between retries
REQUEST_TIMEOUT = 30  # Timeout for API requests in seconds

def fetch_items(host_name, auth_token):
    url = f"https://{host_name}/aalam/stock/items?download&fields=id,name,type,code,sale_price,sale_discount,sale_discount_pr,sale_discount_mode,stock,is_public,properties"
    headers = {"X-Auth-Token": auth_token}

    for attempt in range(RETRIES):
        try:
            logger.info(f"Attempting to fetch items from {url}. Attempt {attempt + 1} of {RETRIES}.")
            response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)  # Use REQUEST_TIMEOUT
            response.raise_for_status()  # Raise an exception for HTTP errors
            # Read CSV from response and return as DataFrame
            item_df = pd.read_csv(StringIO(response.text))
            logger.info(f"Items fetched successfully with {len(item_df)} rows and {len(item_df.columns)} columns.")
            return item_df
        except requests.RequestException as e:
            logger.error(f"Attempt {attempt + 1} failed to fetch items: {e}")
            time.sleep(RETRY_DELAY)
    logger.error(f"Failed to fetch items after {RETRIES} retries.")
    raise Exception(f"Failed to fetch items after {RETRIES} retries.")





