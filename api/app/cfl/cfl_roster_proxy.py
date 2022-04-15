from typing import Dict, List
from api.app.core.logging import Logger
from api.app.core.exceptions import ApiException
from api.app.config.settings import Settings, get_settings
import logging
from fastapi.param_functions import Depends

import requests

logger = logging.getLogger()


def cfl_roster_proxy(settings: Settings = Depends(get_settings)):
    return CflRosterProxy(settings.cfl_roster_endpoint)


class CflRosterProxy:

    def __init__(self, endpoint: str):
        self.endpoint = endpoint

    def get_roster(self, roster_id) -> List[Dict]:
        Logger.info(f"[CFL API] Fetching roster id {roster_id}")
        url = f"{self.endpoint}{roster_id}"
        response = requests.get(url)
        data = response.json()

        try:
            if data["success"] == 1:
                return data["players"]
            else:
                raise ApiException(data["message"])
        except Exception as ex:
            Logger.exception(f"[CFL API] Failed to fetch team rosters for {roster_id}", exc_info=ex)
            raise ApiException("Failed to retrieve rosters")
