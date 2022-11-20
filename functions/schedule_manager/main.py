from datetime import datetime
from typing import Optional
import functions_framework
from pydantic import BaseSettings
from scheduler.store import initialize_firebase
from scheduler.update_schedule import update_schedule

class Settings(BaseSettings):
    cfl_api_key: str
    gcloud_project: str
    is_dev: bool = False
    rtdb_emulator_host: Optional[str] = None
    post_week_buffer_hours: int = 24

    class Config:
        env_file = ".env"


settings = Settings()
initialize_firebase(
    rtdb_emulator_host=settings.rtdb_emulator_host,
    project_id=settings.gcloud_project
)


@functions_framework.cloud_event
def update_schedule_handler(event_data: functions_framework.BackgroundEvent):

    # TODO: get year from event data
    year = datetime.now().year

    return update_schedule(settings.cfl_api_key, year, settings.post_week_buffer_hours)
