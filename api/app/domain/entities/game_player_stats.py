from __future__ import annotations
from api.app.domain.entities.stats import Stats

from typing import Optional

from pydantic import BaseModel

from .game_player import GamePlayer
from .team import Team


class GamePlayerStats(BaseModel):
    game_id: str
    player: GamePlayer
    team: Team
    opponent: Team
    hash: Optional[str]
    stats: Stats
