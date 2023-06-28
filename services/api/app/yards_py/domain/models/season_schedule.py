from datetime import datetime

from pydantic import BaseModel


class ScheduleGame(BaseModel):
    game_id: str
    date_start: datetime
    game_number: int
    week: int
    away_abbr: str
    home_abbr: str


class ScheduleWeek(BaseModel):
    week_number: int
    games: list[ScheduleGame]


class SeasonSchedule(BaseModel):
    year: int
    weeks: dict[str, ScheduleWeek]
