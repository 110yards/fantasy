from datetime import datetime
from enum import Enum
from typing import Optional

from app.domain.entities.player import Player
from pydantic import BaseModel


class WaiverBidResult(int, Enum):
    Unprocessed = 0

    SuccessPending = 1
    Success = 2

    FailedDropPlayerNotOnRoster = -1
    FailedNotEnoughMoney = -2
    FailedNoRosterSpace = -3
    FailedOutBid = -4
    FailedLowerPriority = -5


class WaiverBid(BaseModel):
    roster_id: str
    player: Player
    drop_player: Optional[Player]
    amount: int
    timestamp: datetime = datetime.now()
    result: WaiverBidResult = WaiverBidResult.Unprocessed
