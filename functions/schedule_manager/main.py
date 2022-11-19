from datetime import datetime
import functions_framework
from pydantic import BaseSettings
from functions.schedule_manager.scheduler.store import initialize_firebase
from scheduler.update_schedule import update_schedule


class Settings(BaseSettings):
    is_dev: bool
    cfl_api_key: str
    gcloud_project: str
    rtdb_emulator_host: str
    post_week_buffer_hours: int = 24

    class Config:
        env_file = ".env"


settings = Settings()
initialize_firebase(
    rtdb_emulator_host=settings.rtdb_emulator_host,
    project_id=settings.gcloud_project
)


@ functions_framework.cloud_event
def update_schedule_handler(event_data: functions_framework.BackgroundEvent):

    # TODO: get year from event data
    year = datetime.now().year

    return update_schedule(settings.cfl_api_key, year, settings.post_week_buffer_hours)
