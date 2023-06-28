from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic.main import BaseModel


class ScoreboardGame(BaseModel):
    game_id: str
    game_date: datetime
    away_abbr: str
    home_abbr: str
    away_score: int
    home_score: int
    status: str

    @property
    def is_complete(self) -> bool:
        return self.status == "complete"


class Team(BaseModel):
    opponent: Optional[str] = None
    locked: bool = False
    game_id: Optional[str] = None


class Teams(BaseModel):
    bc: Team
    cgy: Team
    edm: Team
    ham: Team
    mtl: Team
    ott: Team
    ssk: Team
    tor: Team
    wpg: Team

    def values(self) -> list[Team]:
        return [self.bc, self.cgy, self.edm, self.ham, self.mtl, self.ott, self.ssk, self.tor, self.wpg]


class Scoreboard(BaseModel):
    focus_game: Optional[ScoreboardGame] = None
    games: list[ScoreboardGame]
    teams: Teams

    def any_locks(self) -> bool:
        return any([team.locked for team in self.teams.values()])

    def is_locked(self, team_abbr: str) -> bool:
        return getattr(self.teams, team_abbr).locked

    def is_team_on_bye(self, team_abbr: str) -> bool:
        return getattr(self.teams, team_abbr).opponent is None
