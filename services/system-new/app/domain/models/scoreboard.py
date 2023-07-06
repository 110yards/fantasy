from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ScoreboardGame(BaseModel):
    game_id: str
    game_date: datetime
    end_date: Optional[datetime] = None
    status: str

    def is_complete(self) -> bool:
        return self.status == "complete" and self.end_date is not None


class Scoreboard(BaseModel):
    games: list[ScoreboardGame]

    def all_games_complete(self) -> bool:
        return all(game.is_complete() for game in self.games)

    def last_game_start_time(self) -> datetime:
        return max(game.game_date for game in self.games)
