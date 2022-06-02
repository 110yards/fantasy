from __future__ import annotations
from pydantic import BaseModel

from yards_py.domain.entities.player_score import PlayerScore
from .team import Team


class PlayerLeagueGameScore(BaseModel):
    game_id: str
    week_number: int
    team: Team
    opponent: Team
    score: PlayerScore
