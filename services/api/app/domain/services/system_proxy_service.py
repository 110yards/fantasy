

from fastapi import Depends
import requests

from ...config.settings import Settings, get_settings


class SystemProxyService:
    def __init__(self, system_api: str, system_api_key: str):
        self.system_api = system_api
        self.system_api_key = system_api_key

    
    def post(self, endpoint: str) -> dict:
        # for now, this only supports calls without a body
        result = requests.post(f"{self.system_api}/{endpoint}?key={self.system_api_key}")

        if 200 <= result.status_code < 300:
            return result.json()
        
        raise Exception(f"Failed to call {endpoint} with status code {result.status_code}")

def create_system_proxy_service(settings: Settings = Depends(get_settings)):
    return SystemProxyService(settings.system_api, settings.system_api_key)
