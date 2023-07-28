from __future__ import annotations

from typing import Optional

from app.core.base_entity import BaseEntity
from app.domain.enums.position_type import PositionType

# remember, the game player stats object contains a game player, not the other way around


class GamePlayer(BaseEntity):
    first_name: str
    middle_name: str
    last_name: str
    birth_date: Optional[str]
    # uniform: int
    position: PositionType
    is_national: bool
    is_starter: bool
    is_inactive: bool
