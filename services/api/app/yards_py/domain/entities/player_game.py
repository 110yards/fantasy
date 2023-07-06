from __future__ import annotations

from typing import Literal

from pydantic import BaseModel

from app.yards_py.domain.entities.stats import Stats


class GameResult(BaseModel):
    team_abbr: str
    opponent_abbr: str
    score_for: int
    score_against: int
    result: Literal["W", "L", "T"]
    was_home: bool


class PlayerGame(BaseModel):
    player_id: str
    game_id: int
    week_number: int
    stats: Stats
    game_result: GameResult
