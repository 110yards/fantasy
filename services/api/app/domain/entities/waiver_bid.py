from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel

from app.core.annotate_args import annotate_args
from app.domain.entities.player import Player


class WaiverBidResult(int, Enum):
    Unprocessed = 0

    SuccessPending = 1
    Success = 2

    FailedDropPlayerNotOnRoster = -1
    FailedNotEnoughMoney = -2
    FailedNoRosterSpace = -3
    FailedOutBid = -4
    FailedLowerPriority = -5


@annotate_args
class WaiverBid(BaseModel):
    roster_id: str
    player: Player
    drop_player: Optional[Player] = None
    amount: int
    timestamp: datetime = datetime.now()
    result: WaiverBidResult = WaiverBidResult.Unprocessed
