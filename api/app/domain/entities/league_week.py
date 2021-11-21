from __future__ import annotations
from api.app.domain.entities.waiver_bid import WaiverBid

from typing import List

from api.app.core.base_entity import BaseEntity
from api.app.core.annotate_args import annotate_args


@annotate_args
class LeagueWeek(BaseEntity):
    waiver_bids: List[WaiverBid] = []
