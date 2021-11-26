from api.app.core.logging import Logger

import requests
from api.app.config.settings import Settings, get_settings
from fastapi import Depends
from datetime import datetime


class CflApiException(BaseException):
    def __init__(self, message):
        self.message = message


def create_cfl_proxy(settings: Settings = Depends(get_settings)):
    return CflProxy(settings)


class CflProxy:
    last_request_time: datetime = None

    def __init__(self, settings: Settings):
        self.settings = settings

    def get(self, path: str) -> dict:
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
