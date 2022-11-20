from datetime import datetime
from typing import Optional
import functions_framework
from pydantic import BaseSettings
from scheduler.store import initialize_firebase
from scheduler.update_schedule import update_schedule
from cloudevents.http import CloudEvent


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
def update_schedule_handler(event: CloudEvent):

    print(f"event data: {event}")
    data: dict = event.data.get("data")

    try:
        if not data:  # default
            year = datetime.now().year
            return update_schedule(settings.cfl_api_key, year, settings.post_week_buffer_hours)
        else:  # sim
            print("Running simulated update")
            print(data)
            sim_year = data.get("year")
            sim_segment = data.get("segment")
            sim_week = data.get("week")

            if not sim_year or not sim_segment or not sim_segment:
                print("Simulation input data is invalid, aborting")
                print(f"sim_year: {sim_year}")
                print(f"sim_segment: {sim_segment}")
                print(f"sim_week: {sim_week}")
                return

            return update_schedule(settings.cfl_api_key, sim_year, settings.post_week_buffer_hours, sim_segment, sim_week)

    except BaseException as ex:
        print(f"Update schedule failed: {ex}")
