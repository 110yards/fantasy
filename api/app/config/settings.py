from enum import Enum
from functools import lru_cache
from typing import Optional

from pydantic import BaseSettings
from dotenv import load_dotenv


class Environment(str, Enum):
    Dev = "DEV"
    Test = "TEST"
    Live = "LIVE"


class Settings(BaseSettings):
    dev: bool = False
    firebase_api_key: str
    endpoint: str
    cfl_api_key: Optional[str]
    cfl_api_endpoint: str = "https://api.cfl.ca/v1"
    cfl_roster_endpoint: str = "http://www.cfl.ca/wp-content/themes/cfl.ca/inc/admin-ajax.php?action=get_roster&teamId="
    current_season: int  # DEPRECATED
    gcloud_project: str
    service_name: Optional[str]
    region: Optional[str]
    season_weeks: int  # DEPRECATED
    origins: str
    api_key: str
    version: str = "dev"
    min_stat_correction_hours: int = 24

    class Config:
        env_file = ".env"

    def is_dev(self):
        return self.dev


@lru_cache()
def get_settings():
    load_dotenv(".env")
    return Settings()
