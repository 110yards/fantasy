from __future__ import annotations
from app.yards_py.domain.entities.waiver_bid import WaiverBid

from typing import List

from app.yards_py.core.base_entity import BaseEntity
from app.yards_py.core.annotate_args import annotate_args


@annotate_args
class LeagueWeek(BaseEntity):
    waiver_bids: List[WaiverBid] = []
