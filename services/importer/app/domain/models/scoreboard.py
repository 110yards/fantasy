import hashlib
import json
from datetime import datetime, timedelta, timezone
from typing import Optional

from pydantic import BaseModel, computed_field
from strivelogger import StriveLogger


class ScoreboardGame(BaseModel):
    game_id: str
    game_date: datetime
    end_date: Optional[datetime] = None
    away_abbr: str
    home_abbr: str
    away_score: int
    home_score: int
    status: str
    quarter: Optional[str]
    clock: Optional[str]
    started: bool
    realtime_source_id: int
    boxscore_source_id: str

    @computed_field
    @property
    def is_complete(self) -> bool:
        return self.status == "complete" and self.end_date is not None

    def is_active(self) -> bool:
        buffer_minutes = 30
        within_start_buffer = self.game_date - timedelta(minutes=buffer_minutes) <= datetime.now(timezone.utc)
        within_end_buffer = self.end_date is None or self.end_date + timedelta(minutes=buffer_minutes) >= datetime.now(timezone.utc)

        StriveLogger.info(f"Game {self.game_id} is active: {within_start_buffer and within_end_buffer}")

        return within_start_buffer and within_end_buffer


class Team(BaseModel):
    locked: bool = False
    opponent: Optional[str] = None
    game: Optional[ScoreboardGame] = None
    is_at_home: Optional[bool] = None


class Teams(BaseModel):
    bc: Team = Team()
    cgy: Team = Team()
    edm: Team = Team()
    ham: Team = Team()
    mtl: Team = Team()
    ott: Team = Team()
    ssk: Team = Team()
    tor: Team = Team()
    wpg: Team = Team()

    def lock_all(self) -> None:
        self.bc.locked = True
        self.cgy.locked = True
        self.edm.locked = True
        self.ham.locked = True
        self.mtl.locked = True
        self.ott.locked = True
        self.ssk.locked = True
        self.tor.locked = True
        self.wpg.locked = True


# class Opponents(BaseModel):
#     BC: Optional[str] = None
#     CGY: Optional[str] = None
#     EDM: Optional[str] = None
#     HAM: Optional[str] = None
#     MTL: Optional[str] = None
#     OTT: Optional[str] = None
#     SSK: Optional[str] = None
#     TOR: Optional[str] = None
#     WPG: Optional[str] = None


class Scoreboard(BaseModel):
    focus_game: Optional[ScoreboardGame] = None
    games: list[ScoreboardGame]
    teams: Teams

    def hash(self) -> str:
        return hashlib.md5(json.dumps(self.model_dump_json()).encode("utf-8")).hexdigest()
