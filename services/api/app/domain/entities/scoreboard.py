from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ScoreboardGame(BaseModel):
    game_id: str
    game_date: datetime
    away_abbr: str
    home_abbr: str
    away_score: int
    home_score: int
    status: str
    started: bool

    @property
    def is_complete(self) -> bool:
        return self.status == "complete"

    @property
    def is_in_progress(self) -> bool:
        return self.started

    @property
    def is_upcoming(self) -> bool:
        return self.status == "scheduled"


class Team(BaseModel):
    opponent: Optional[str] = None
    locked: bool = False
    game_id: Optional[str] = None


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

    def get_game_for_team(self, team_abbr: str) -> Optional[ScoreboardGame]:
        return next((game for game in self.games if game.game_id == getattr(self.teams, team_abbr).game_id), None)
