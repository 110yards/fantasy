

from datetime import datetime
from typing import Literal
from pydantic import BaseModel

from .team import Team


class ScheduleGame(BaseModel):
    year: int
    week: int
    game_id: str
    date_start: datetime
    game_number: int
    game_type: Literal["preseason", "regular", "division-semifinal", "division-final", "grey-cup"]
    away: Team
    home: Team


"""
This model represents the CFL's schedule for the current season
"""
class SeasonSchedule(BaseModel):
    id: str = "schedule"
    year: int
    games: list[ScheduleGame]
