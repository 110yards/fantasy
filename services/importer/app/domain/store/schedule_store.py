from typing import Optional

from fastapi import Depends

from app.core.rtdb_client import RTDBClient, create_rtdb_client
from app.domain.models.schedule import Schedule


class ScheduleStore:
    def __init__(self, rtdb_client: RTDBClient):
        self.rtdb_client = rtdb_client

    def path(self, year: int) -> str:
        return f"schedule/{year}"

    def get_schedule(self, year: int) -> Optional[Schedule]:
        path = self.path(year)
        data = self.rtdb_client.get(path)
        return Schedule(**data) if data else None

    def save_schedule(self, schedule: Schedule) -> None:
        path = self.path(schedule.year)
        self.rtdb_client.set(path, schedule.dict())


def create_schedule_store(rtbd_client: RTDBClient = Depends(create_rtdb_client)) -> ScheduleStore:
    return ScheduleStore(
        rtdb_client=rtbd_client,
    )
