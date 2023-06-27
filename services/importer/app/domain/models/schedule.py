import hashlib
import json
from datetime import datetime

from pydantic import BaseModel


def create_game_id(year: int, week: int, game_number: int) -> str:
    return f"{year}{week:0>2}{game_number:0>2}"


class ScheduleGame(BaseModel):
    game_id: str
    realtime_source_id: int
    boxscore_source_id: str
    date_start: datetime
    game_number: int
    week: int
    away_abbr: str
    home_abbr: str


class ScheduleWeek(BaseModel):
    week_number: int
    games: list[ScheduleGame]


class Schedule(BaseModel):
    year: int
    boxscore_source_season_id: str
    weeks: dict[str, ScheduleWeek]

    def hash(self) -> str:
        return hashlib.md5(json.dumps(self.json()).encode("utf-8")).hexdigest()
