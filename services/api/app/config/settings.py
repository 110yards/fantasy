from enum import Enum
from functools import lru_cache
from typing import Optional

from dotenv import load_dotenv
from pydantic import BaseSettings


class Environment(str, Enum):
    Dev = "DEV"
    Test = "TEST"
    Live = "LIVE"


class Settings(BaseSettings):
    dev: bool = False
    firebase_api_key: str
    endpoint: str
    gcloud_project: str
    service_name: Optional[str]
    region: Optional[str]
    origins: str
    version: str = "dev"
    rtdb_emulator_host: Optional[str] = None
    firebase_auth_emulator_host: Optional[str] = None
    firestore_emulator_host: str

    class Config:
        env_file = ".env"

    def is_dev(self):
        return self.dev


@lru_cache()
def get_settings():
    load_dotenv(".env")
    return Settings()
