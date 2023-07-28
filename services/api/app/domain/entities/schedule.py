from __future__ import annotations

from copy import deepcopy
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, computed_field

from app.core.annotate_args import annotate_args
from app.core.base_entity import BaseEntity
from app.domain.entities.roster import Roster
from app.domain.enums.matchup_type import MatchupType
from app.domain.enums.week_type import WeekType


class PlayoffType(int, Enum):
    TOP_2 = 2
    TOP_3 = 3
    TOP_4 = 4
    TOP_6 = 6

    @property
    def weeks(self) -> int:
        if self == PlayoffType.TOP_2:
            return 1

        if self == PlayoffType.TOP_3 or self == PlayoffType.TOP_4:
            return 2

        if self == PlayoffType.TOP_6:
            return 3

        raise ValueError()


def get_playoff_type_config():
    return [
        {"id": str(PlayoffType.TOP_2.value), "name": "Top 2", "weeks": 1},
        {"id": str(PlayoffType.TOP_3.value), "name": "Top 3", "weeks": 2},
        {"id": str(PlayoffType.TOP_4.value), "name": "Top 4", "weeks": 2},
        {"id": str(PlayoffType.TOP_6.value), "name": "Top 6", "weeks": 3},
    ]


@annotate_args
class Matchup(BaseEntity):
    away: Optional[Roster] = None
    home: Optional[Roster] = None
    type: MatchupType
    type_display: Optional[str] = None
    away_score: float = 0.0
    home_score: float = 0.0
    away_bench_score: float = 0.0
    home_bench_score: float = 0.0

    @computed_field
    @property
    def type_display(self) -> str:
        return self.type.display()


@annotate_args
class ScheduleWeek(BaseModel):
    week_number: int
    week_type: WeekType
    matchups: List[Matchup] = []

    @computed_field
    @property
    def week_id(self) -> str | None:
        return f"{self.week_number:02}" if self.week_number else None

    @computed_field
    @property
    def heading(self) -> str | None:
        if self.week_type == WeekType.PLAYOFFS:
            return "Playoffs"

        if self.week_type == WeekType.CHAMPIONSHIP:
            return "Championship"

        return f"Week {self.week_number}"

    def assign_playoff_matchups(self, playoff_type: PlayoffType, rosters: List[Roster], previous_week: ScheduleWeek):
        if previous_week.week_type == WeekType.REGULAR:
            self._assign_round_1_matchups(playoff_type, rosters)
        else:
            self._assign_winner_matchups(previous_week)

        for matchup in self.matchups:
            if matchup.away:
                matchup.away.positions = {}
            if matchup.home:
                matchup.home.positions = {}

    def _assign_round_1_matchups(self, playoff_type: PlayoffType, rosters: List[Roster]):
        sorted = deepcopy(rosters)
        sorted.sort(key=lambda x: x.rank)
        assert sorted[0].rank == 1

        if playoff_type == PlayoffType.TOP_2:
            self.matchups[0].home = sorted[0]  # 1 vs 2
            self.matchups[0].away = sorted[1]

        if playoff_type == PlayoffType.TOP_3:
            self.matchups[0].home = sorted[1]  # 2 vs 3
            self.matchups[0].away = sorted[2]
            self.matchups[1].home = sorted[0]  # 1 bye

        if playoff_type == PlayoffType.TOP_4:
            self.matchups[0].home = sorted[0]  # 1 vs 4
            self.matchups[0].away = sorted[3]
            self.matchups[1].home = sorted[1]  # 2 vs 3
            self.matchups[1].away = sorted[2]

        if playoff_type == PlayoffType.TOP_6:
            self.matchups[0].home = sorted[2]  # 3 v 6
            self.matchups[0].away = sorted[5]
            self.matchups[1].home = sorted[3]  # 4 v 5
            self.matchups[1].away = sorted[4]
            self.matchups[2].home = sorted[0]  # 1 bye
            self.matchups[3].home = sorted[1]  # 2 bye

        for matchup in self.matchups:
            if matchup.type == MatchupType.LOSER:
                matchup.away = sorted[-1]
                matchup.home = sorted[-2]

    def _assign_winner_matchups(self, previous_week: ScheduleWeek):
        winners: List[Roster] = []

        for matchup in previous_week.matchups:
            if matchup.type == MatchupType.PLAYOFF:
                winner = matchup.away if matchup.away_score > matchup.home_score else matchup.home
                winners.append(winner)
            if matchup.type == MatchupType.PLAYOFF_BYE:
                winners.append(matchup.home)

        winners.sort(key=lambda x: x.rank)
        for matchup in self.matchups:
            matchup.away = winners.pop(-1)
            matchup.home = winners.pop(0)


@annotate_args
class Schedule(BaseEntity):
    weeks: List[ScheduleWeek]
    playoff_type: PlayoffType
    first_playoff_week: Optional[int] = None
    enable_loser_playoff: bool
    id: str = "schedule"

    def reset(self):
        self.weeks = []
        self.first_playoff_week = None
