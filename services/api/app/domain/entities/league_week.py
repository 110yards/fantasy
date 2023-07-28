from __future__ import annotations

from typing import List

from app.core.annotate_args import annotate_args
from app.core.base_entity import BaseEntity
from app.domain.entities.waiver_bid import WaiverBid


@annotate_args
class LeagueWeek(BaseEntity):
    waiver_bids: List[WaiverBid] = []
