from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class InjuryStatusId(str, Enum):
    probable = "probable"
    questionable = "questionable"
    out = "out"
    injured_six = "six-game"


class InjuryStatus(BaseModel):
    status_id: InjuryStatusId
    text: str
    last_updated: datetime
    injury: str
