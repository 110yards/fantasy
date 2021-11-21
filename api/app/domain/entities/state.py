from __future__ import annotations
from datetime import datetime
from api.app.domain.entities.team import Team
from api.app.core.base_entity import BaseEntity
from typing import List, Optional, Union
from pydantic import BaseModel
from api.app.core.annotate_args import annotate_args


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
    def create(locked_teams: List[str], all_games_active: bool) -> Locks:

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
    waivers_end: Optional[datetime]

    locks: Locks = Locks()
    waivers_active = False

    id: str = "state"

    def changed(self, previous: State) -> bool:
        if self.current_week != previous.current_week:
            return True

        return self.locks.changed(previous.locks)
