from __future__ import annotations

from app.yards_py.domain.entities.stats import Stats
from app.yards_py.core.base_entity import BaseEntity
from .team import Team
from app.yards_py.core.annotate_args import annotate_args


@annotate_args
class PlayerGame(BaseEntity):
    player_id: str
    game_id: int
    week_number: int
    team: Team
    opponent: Team
    stats: Stats

    # TODO: automatically set this in init
    def set_id(self):
        self.id = PlayerGame.create_id(self.player_id, self.game_id)

    @staticmethod
    def create_id(player_id: str, game_id: int) -> str:
        return f"{player_id}_{game_id}"
