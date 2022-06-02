import time
from datetime import datetime

import requests
from services.system.app.config.settings import Settings, get_settings
from yards_py.core.logging import Logger
from fastapi import Depends
from ratelimiter import RateLimiter


class CflApiException(BaseException):
    def __init__(self, message):
        self.message = message


def create_cfl_proxy(settings: Settings = Depends(get_settings)):
    return CflProxy(settings)


def limited(until):
    duration = int(round(until - time.time()))
    Logger.info(f"Rated limit reached, pausing for {duration} seconds")


class CflProxy:
    last_request_time: datetime = None

    def __init__(self, settings: Settings):
        self.settings = settings

    # enforcing the 30/minute limit as a 30 second interval should make it less likely to accidentally hit the limit.
    @RateLimiter(max_calls=15, period=30, callback=limited)
    def get(self, path: str) -> dict:
        if not self.settings.cfl_api_key:
            msg = "CFL API Key is not set. To enable CFL API requests, please add CFL_API_KEY=<key> to your .env file." \
                "You must have a key provided by the CFL; see https://api.cfl.ca/ for more information."
            Logger.error(msg)
            raise CflApiException(msg)

        url = f"{self.settings.cfl_api_endpoint}/{path}"
        url_no_key = url

        if "?" in url:
            url += f"&key={self.settings.cfl_api_key}"
        else:
            url += f"?key={self.settings.cfl_api_key}"

        Logger.info(f"[CFL API] Fetching {url_no_key}")
        response = requests.get(url)

        if response.ok:
            return response.json()
        else:
            Logger.error(f"[CFL API] Error fetching data from {url_no_key}: {response.text}")
            raise CflApiException(response.text)
