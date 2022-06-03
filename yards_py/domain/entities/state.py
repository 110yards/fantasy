from __future__ import annotations
from datetime import datetime
from yards_py.domain.entities.team import Team
from yards_py.core.base_entity import BaseEntity
from typing import List, Optional, Union
from pydantic import BaseModel
from yards_py.core.annotate_args import annotate_args


@annotate_args
class Locks(BaseModel):
    BC: Optional[bool]
    CGY: Optional[bool]
    EDM: Optional[bool]
    SSK: Optional[bool]
    WPG: Optional[bool]
    HAM: Optional[bool]
    TOR: Optional[bool]
    OTT: Optional[bool]
    MTL: Optional[bool]

    def is_locked(self, team: Union[Team, str]) -> bool:
        if isinstance(team, Team):
            team = team.abbreviation

        if team == "FA":
            return False

        return self.dict()[team]

    def any_locks(self) -> bool:
        for team_locked in self.dict().values():
            if team_locked:
                return True

        return False

    @staticmethod
    def create(locked_teams: List[str] = None, all_games_active: bool = False) -> Locks:
        if locked_teams is None:
            locked_teams = []

        locks = Locks()
        if all_games_active:
            locks.BC = True
            locks.CGY = True
            locks.EDM = True
            locks.HAM = True
            locks.MTL = True
            locks.OTT = True
            locks.SSK = True
            locks.TOR = True
            locks.WPG = True
        else:
            locks.BC = "BC" in locked_teams
            locks.CGY = "CGY" in locked_teams
            locks.EDM = "EDM" in locked_teams
            locks.HAM = "HAM" in locked_teams
            locks.MTL = "MTL" in locked_teams
            locks.OTT = "OTT" in locked_teams
            locks.SSK = "SSK" in locked_teams
            locks.TOR = "TOR" in locked_teams
            locks.WPG = "WPG" in locked_teams

        return locks

    @staticmethod
    def reset() -> Locks:
        locks = Locks()
        locks.BC = False
        locks.CGY = False
        locks.EDM = False
        locks.HAM = False
        locks.MTL = False
        locks.OTT = False
        locks.SSK = False
        locks.TOR = False
        locks.WPG = False

        return locks

    def changed(self, previous: Locks) -> bool:
        if not previous:
            return True

        return \
            self.BC != previous.BC or \
            self.CGY != previous.CGY or \
            self.EDM != previous.EDM or \
            self.SSK != previous.SSK or \
            self.WPG != previous.WPG or \
            self.HAM != previous.HAM or \
            self.TOR != previous.TOR or \
            self.OTT != previous.OTT or \
            self.MTL != previous.MTL


@annotate_args
class State(BaseEntity):
    current_week: int
    current_season: int
    season_weeks: int
    waivers_end: Optional[datetime]

    locks: Locks = Locks()
    waivers_active = False
    is_offseason: bool = False

    id: str = "state"

    def changed(self, previous: State) -> bool:
        if self.current_week != previous.current_week:
            return True

        return self.locks.changed(previous.locks)

    @staticmethod
    def default(
        with_current_week: int = None,
        with_current_season: int = None,
        with_season_weeks: int = None,
        with_waivers_end: datetime = None
    ):
        return State(
            current_week=with_current_week or 1,
            current_season=with_current_season or 2021,
            season_weeks=with_season_weeks or 16,
            waivers_end=with_waivers_end or None,
        )
