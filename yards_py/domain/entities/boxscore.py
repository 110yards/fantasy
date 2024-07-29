
from datetime import datetime
from pydantic import BaseModel

from .stats import Stats

from .team import Team


class BoxscorePlayerStats(BaseModel):
    player_id: str
    game_id: str
    year: int
    week: int
    team: Team
    opponent: Team
    name: str
    date_updated: datetime
    stats: Stats

class BoxscoreTeams(BaseModel):
    away: Team
    away_stats: list[BoxscorePlayerStats]
    home: Team
    home_stats: list[BoxscorePlayerStats]

class Boxscore(BaseModel):
    game_id: str
    week: int
    year: int
    date_updated: datetime
    date_start: datetime
    teams: BoxscoreTeams

