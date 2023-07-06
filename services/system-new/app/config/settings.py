from enum import Enum
from functools import lru_cache
from typing import Optional

from dotenv import load_dotenv
from pydantic_settings import BaseSettings


class Environment(str, Enum):
    Dev = "dev"
    Test = "test"
    Live = "live"


class Settings(BaseSettings):
    environment: Environment
    gcloud_project: str
    service_name: Optional[str] = None
    region: Optional[str] = None
    api_key: str
    version: str = "dev"
    rtdb_emulator_host: Optional[str] = None
    firestore_emulator_host: Optional[str] = None
    min_stat_correction_hours: int = 24

    class Config:
        env_file = ".env"

    def is_dev(self):
        return self.environment == Environment.Dev


@lru_cache()
def get_settings():
    load_dotenv(".env")
    return Settings()
