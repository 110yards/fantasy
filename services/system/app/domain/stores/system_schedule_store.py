from fastapi import Depends

from ...core.rtdb_client import RTDBClient, create_rtdb_client
from ..entities.system_schedule import SystemSchedule, SystemScheduleWeek


class SystemScheduleStore:
    def __init__(self, rtdb_client: RTDBClient):
        self.rtdb_client = rtdb_client

    def get_schedule_week(self, year: int, week_number: int) -> SystemScheduleWeek | None:
        week_key = f"W{str(week_number).zfill(2)}"
        data = self.rtdb_client.get(f"schedules/{year}/weeks/{week_key}")

        return SystemScheduleWeek(**data) if data else None

    def get_schedule(self, year: int) -> SystemSchedule | None:
        data = self.rtdb_client.get(f"schedules/{year}")

        return SystemSchedule(**data) if data else None


def create_system_schedule_store(rtdb_client: RTDBClient = Depends(create_rtdb_client)) -> SystemScheduleStore:
    return SystemScheduleStore(rtdb_client=rtdb_client)
