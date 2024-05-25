from datetime import datetime

import requests
from ..api_exception import ApiException
from services.system.app.config.settings import Settings, get_settings
from yards_py.core.logging import Logger
from fastapi import Depends




class CoreProxy:
    last_request_time: datetime = None

    def __init__(self, settings: Settings):
        self.settings = settings

    def get(self, path: str) -> dict:
        if not self.settings.cfl_api_key:
            msg = "Core API Key is not set. To enable API requests, please add CORE_API_KEY=<key> to your .env file." \
                "You must have a key provided by the 110yards."
            Logger.error(msg)
            raise ApiException(msg)

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
            raise ApiException(response.text)

def create_core_proxy(settings: Settings = Depends(get_settings)):
    return CoreProxy(settings)
