from __future__ import annotations
from typing import Optional
from app.yards_py.domain.enums.position_type import PositionType

from app.yards_py.core.base_entity import BaseEntity
from app.yards_py.core.annotate_args import annotate_args
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
