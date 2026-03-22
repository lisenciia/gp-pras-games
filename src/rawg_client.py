# We use dotenv library for security purpose (to so that the API isn't publicily visible), but it isn't mandatory there

import time
import requests
import logging
import logging.config
import os
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger('rawg_api')

urll = "https://api.rawg.io/api"

class RAWGClient:
    def __init__(self):
        self.api_key = os.getenv("RAWG_api")
        if not self.api_key:
            raise ValueError("API key not found!")
        logger.info("RAWGClient initialized successfully")

    def _get(self, endpoint, params=None, retries=3):
        if params is None:
            params = {}
        params['key'] = self.api_key
        url = f"{urll}/{endpoint}"
        for attempt in range(retries):
            try:
                response = requests.get(url, params=params, timeout=5)
                response.raise_for_status()
                logger.info(
                    f"Successful request: {endpoint} | status {response.status_code}")
                return response.json()
            except requests.exceptions.HTTPError as e:
                logger.error(f"HTTP error {endpoint}: {e}")
            except requests.exceptions.Timeout:
                logger.error(f"Request timeout: {endpoint}")
            except requests.exceptions.RequestException as e:
                logger.error(f"Request error {endpoint}: {e}")
            return None
        return None