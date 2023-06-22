from enum import Enum
from functools import lru_cache
from typing import Optional

from dotenv import load_dotenv
from pydantic import BaseSettings


class Environment(str, Enum):
    Dev = "dev"
    Test = "test"
    Live = "live"


class Settings(BaseSettings):
    environment: Environment
    gcloud_project: str
    rtdb_url: str
    api_key: str
    service_name: Optional[str]
    region: Optional[str]
    version: str = "dev"

    class Config:
        env_file = ".env"

    def is_dev(self):
        return self.environment == Environment.Dev


@lru_cache()
def get_settings():
    load_dotenv(".env")
    return Settings()
