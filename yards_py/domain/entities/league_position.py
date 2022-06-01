from __future__ import annotations
from api.app.domain.entities.player import Player
from typing import Optional

from api.app.core.annotate_args import annotate_args
from api.app.domain.enums.position_type import PositionType
from pydantic.main import BaseModel


@annotate_args
class LeaguePosition(BaseModel):
    id: int
    name: str
    position_type: PositionType
    player: Optional[Player]
    game_id: Optional[str]
    game_score: float = 0

    @staticmethod
    def create(id: int, name: str, position_type: PositionType) -> LeaguePosition:
        return LeaguePosition(id=id, name=name, position_type=position_type)

    def is_active_position_type(self) -> bool:
        return self.position_type.is_active_position_type()

    def is_starting_position_type(self) -> bool:
        return self.position_type.is_starting_position_type()

    def is_reserve_type(self) -> bool:
        return self.position_type.is_reserve_type()
