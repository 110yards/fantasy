from __future__ import annotations

from typing import Optional

from app.core.annotate_args import annotate_args
from app.core.base_entity import BaseEntity
from app.domain.enums.position_type import PositionType

# remember, the game player stats object contains a game player, not the other way around


@annotate_args
class GamePlayer(BaseEntity):
    first_name: str
    middle_name: str
    last_name: str
    birth_date: Optional[str] = None
    # uniform: int
    position: PositionType
    is_national: bool
    is_starter: bool
    is_inactive: bool
