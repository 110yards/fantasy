import hashlib
import json
from enum import Enum

from pydantic import BaseModel

from app.domain.models.player import Team


class InjuryStatuses(int, Enum):
    Inactive = 0
    Active = 1
    InjuredOneGame = 2
    InjuredSixGames = 3
    PracticeSquad = 4
    Suspended = 5
    Disabled = 7
    Questionable = 8
    Probable = 9


class InjuryStatus(BaseModel):
    status_id: InjuryStatuses
    text: str
    last_updated: str
    injury: str


class InjuryPlayer(BaseModel):
    first_name: str
    last_name: str
    team: Team
    player_id: str


class PlayerInjuryStatus(BaseModel):
    player: InjuryPlayer
    status: InjuryStatus


class InjuryReport(BaseModel):
    reports: list[PlayerInjuryStatus]

    def hash(self) -> str:
        return hashlib.md5(json.dumps(self.json()).encode("utf-8")).hexdigest()
