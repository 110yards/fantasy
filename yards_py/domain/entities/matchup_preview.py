

from yards_py.domain.entities.roster import Roster
from yards_py.domain.entities.schedule import Matchup
from typing import Optional
from pydantic.main import BaseModel
from yards_py.core.annotate_args import annotate_args


@annotate_args
class MatchupPreviewTeam(BaseModel):
    id: str
    name: str

    @staticmethod
    def from_roster(roster: Roster):
        return MatchupPreviewTeam(id=roster.id, name=roster.name)


@annotate_args
class MatchupPreview(BaseModel):
    matchup_id: Optional[int]
    away: Optional[MatchupPreviewTeam]
    home: Optional[MatchupPreviewTeam]
    away_score: Optional[int] = 0
    home_score: Optional[int] = 0

    @staticmethod
    def from_matchup(matchup: Matchup):
        return MatchupPreview(
            matchup_id=matchup.id,
            away=MatchupPreviewTeam.from_roster(matchup.away) if matchup.away else None,
            home=MatchupPreviewTeam.from_roster(matchup.home) if matchup.home else None,
        )
