from __future__ import annotations

from typing import List

from app.core.annotate_args import annotate_args
from app.core.base_entity import BaseEntity
from app.domain.entities.player_game import PlayerGame
from app.domain.entities.stats import Stats


@annotate_args
class PlayerSeason(BaseEntity):
    season: int
    games_played: int
    player_id: str
    stats: Stats
    games: List[PlayerGame] = []
