from datetime import datetime

from pydantic import BaseModel


class SystemScheduleGame(BaseModel):
    game_id: str
    date_start: datetime
    game_number: int
    week: int
    away_abbr: str
    home_abbr: str


class SystemScheduleWeek(BaseModel):
    week_number: int
    games: list[SystemScheduleGame]
