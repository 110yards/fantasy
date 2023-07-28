from __future__ import annotations

from pydantic import BaseModel

from app.domain.entities.player_score import PlayerScore

from .player_game import GameResult


class PlayerLeagueGameScore(BaseModel):
    game_id: str
    game_result: GameResult
    score: PlayerScore
