from __future__ import annotations
from yards_py.domain.entities.event_status import EVENT_STATUS_POSTPONED
from yards_py.domain.entities.scheduled_game import ScheduledGame

from yards_py.domain.entities.team import Team
from typing import Dict, List, Union
from yards_py.core.base_entity import BaseEntity
from yards_py.core.annotate_args import annotate_args

BYE = "BYE"


@annotate_args
class Opponents(BaseEntity):
    BC: str
    CGY: str
    EDM: str
    HAM: str
    MTL: str
    OTT: str
    SSK: str
    TOR: str
    WPG: str
    FA: str = "N/A"
    id: str = "opponents"

    def is_team_on_bye(self, team: Union[Team, str]):
        if isinstance(team, Team):
            team = team.abbreviation

        return self.dict()[team] == BYE

    @staticmethod
    def create(opponents: Dict[str]) -> Opponents:
        return Opponents(
            BC=opponents.get("BC", BYE),
            CGY=opponents.get("CGY", BYE),
            EDM=opponents.get("EDM", BYE),
            HAM=opponents.get("HAM", BYE),
            MTL=opponents.get("MTL", BYE),
            OTT=opponents.get("OTT", BYE),
            SSK=opponents.get("SSK", BYE),
            TOR=opponents.get("TOR", BYE),
            WPG=opponents.get("WPG", BYE)
        )

    @staticmethod
    def from_scheduled_games(games: List[ScheduledGame]) -> Opponents:
        opponents: Dict[str, str] = {}

        for game in games:
            # if game.event_status.event_status_id == EVENT_STATUS_POSTPONED:
            #     continue

            opponents[game.teams.away.abbreviation] = game.teams.home.abbreviation
            opponents[game.teams.home.abbreviation] = game.teams.away.abbreviation

        return Opponents.create(opponents)

    def changed(self, other: Opponents) -> bool:
        return \
            self.BC != other.BC or \
            self.CGY != other.CGY or \
            self.EDM != other.EDM or \
            self.SSK != other.SSK or \
            self.WPG != other.WPG or \
            self.HAM != other.HAM or \
            self.TOR != other.TOR or \
            self.OTT != other.OTT or \
            self.MTL != other.MTL
