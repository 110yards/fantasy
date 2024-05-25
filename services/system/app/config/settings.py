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
    cfl_api_endpoint: str 
    cfl_roster_endpoint: str = "to be removed"
    gcloud_project: str
    service_name: Optional[str]
    region: Optional[str]
    api_key: str
    version: str = "dev"
    min_stat_correction_hours: int = 24

    @property
    def core_api_key(self) -> str:
        return self.cfl_api_key # temp until the CFL proxy is removed

    class Config:
        env_file = ".env"

    def is_dev(self):
        return self.dev


@lru_cache()
def get_settings():
    load_dotenv(".env")
    return Settings()
