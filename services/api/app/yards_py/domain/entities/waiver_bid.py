from typing import Optional
from pydantic import BaseModel
from app.yards_py.domain.entities.player import Player
from datetime import datetime
from app.yards_py.core.annotate_args import annotate_args
from enum import Enum


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
    drop_player: Optional[Player]
    amount: int
    timestamp: datetime = datetime.now()
    result: WaiverBidResult = WaiverBidResult.Unprocessed
