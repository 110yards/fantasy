from datetime import datetime
from typing import Optional

from pydantic import BaseModel, computed_field


class ScoreboardGame(BaseModel):
    game_id: str
    game_date: datetime
    end_date: Optional[datetime] = None
    away_abbr: str
    home_abbr: str
    away_score: int
    home_score: int
    status: str
    quarter: Optional[str]
    clock: Optional[str]
    started: bool
    realtime_source_id: int
    boxscore_source_id: str

    @computed_field
    @property
    def is_complete(self) -> bool:
        return self.status == "complete" and self.end_date is not None


class Team(BaseModel):
    locked: bool = False
    opponent: Optional[str] = None
    game: Optional[ScoreboardGame] = None
    is_at_home: Optional[bool] = None


class Scoreboard(BaseModel):
    games: list[ScoreboardGame]

    def all_games_complete(self) -> bool:
        return all([game.is_complete for game in self.games])

    def last_game_start_time(self) -> datetime:
        return max([game.game_date for game in self.games])
