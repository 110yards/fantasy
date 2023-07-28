from __future__ import annotations

from typing import Optional

from app.domain.entities.player import Player
from app.domain.enums.position_type import PositionType
from pydantic.main import BaseModel


class LeaguePosition(BaseModel):
    id: int
    name: str
    position_type: PositionType
    player: Optional[Player] = None
    game_id: Optional[str] = None
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
