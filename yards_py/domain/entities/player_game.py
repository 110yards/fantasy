from __future__ import annotations

from api.app.domain.entities.stats import Stats
from api.app.core.base_entity import BaseEntity
from .team import Team
from api.app.core.annotate_args import annotate_args


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
