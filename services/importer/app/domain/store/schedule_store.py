from typing import Optional

from fastapi import Depends

from app.domain.models.schedule import Schedule, ScheduleWeek

from ...core.rtdb_client import RTDBClient, create_rtdb_client


class ScheduleStore:
    def __init__(self, rtdb_client: RTDBClient):
        self.rtdb_client = rtdb_client

    def path(self, year: int) -> str:
        return f"schedules/{year}"

    def get_schedule(self, year: int) -> Optional[Schedule]:
        path = self.path(year)
        data = self.rtdb_client.get(path)
        return Schedule(**data) if data else None

    def save_schedule(self, schedule: Schedule) -> None:
        path = self.path(schedule.year)
        data = schedule.model_dump()

        for week in data["weeks"].values():
            for game in week["games"]:
                game["date_start"] = game["date_start"].isoformat()

        self.rtdb_client.set(path, data)

    def get_boxscore_source_season_id(self, year: int) -> Optional[str]:
        path = self.path(year)
        path = f"{path}/boxscore_source_season_id"
        data = self.rtdb_client.get(path)
        return data

    def get_schedule_week(self, year: int, week_key: str) -> Optional[ScheduleWeek]:
        path = self.path(year)
        path = f"{path}/weeks/{week_key}"
        data = self.rtdb_client.get(path)
        return ScheduleWeek(**data) if data else None


def create_schedule_store(rtbd_client: RTDBClient = Depends(create_rtdb_client)) -> ScheduleStore:
    return ScheduleStore(
        rtdb_client=rtbd_client,
    )
