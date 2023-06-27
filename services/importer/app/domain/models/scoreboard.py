import hashlib
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ScoreboardGame(BaseModel):
    game_date: datetime
    away_abbr: str
    home_abbr: str
    away_score: int
    home_score: int
    status: str
    quarter: Optional[str]
    clock: Optional[str]


class Locks(BaseModel):
    BC: bool = False
    CGY: bool = False
    EDM: bool = False
    HAM: bool = False
    MTL: bool = False
    OTT: bool = False
    SSK: bool = False
    TOR: bool = False
    WPG: bool = False

    @staticmethod
    def all_locked() -> "Locks":
        return Locks(
            BC=True,
            CGY=True,
            EDM=True,
            HAM=True,
            MTL=True,
            OTT=True,
            SSK=True,
            TOR=True,
            WPG=True,
        )


class Opponents(BaseModel):
    BC: Optional[str] = None
    CGY: Optional[str] = None
    EDM: Optional[str] = None
    HAM: Optional[str] = None
    MTL: Optional[str] = None
    OTT: Optional[str] = None
    SSK: Optional[str] = None
    TOR: Optional[str] = None
    WPG: Optional[str] = None


class Scoreboard(BaseModel):
    games: list[ScoreboardGame]
    locks: Locks
    opponents: Opponents

    def hash(self) -> str:
        return hashlib.md5(self.model_dump_json()).encode("utf-8").hexdigest()
