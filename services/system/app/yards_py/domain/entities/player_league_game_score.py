from __future__ import annotations

from app.yards_py.domain.entities.player_score import PlayerScore
from pydantic import BaseModel

from .player_game import GameResult


class PlayerLeagueGameScore(BaseModel):
    game_id: str
    game_result: GameResult
    score: PlayerScore
