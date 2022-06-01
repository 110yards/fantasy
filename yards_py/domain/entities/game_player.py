from __future__ import annotations
from api.app.domain.enums.position_type import PositionType

from api.app.core.base_entity import BaseEntity
from api.app.core.annotate_args import annotate_args
# remember, the game player stats object contains a game player, not the other way around


@annotate_args
class GamePlayer(BaseEntity):
    first_name: str
    middle_name: str
    last_name: str
    birth_date: str
    uniform: int
    position: PositionType
    is_national: bool
    is_starter: bool
    is_inactive: bool
