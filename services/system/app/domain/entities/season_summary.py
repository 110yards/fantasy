from __future__ import annotations

from typing import List, Optional

from app.core.base_entity import BaseEntity
from app.domain.entities.draft import Draft, DraftSlot
from app.domain.entities.league_position import LeaguePosition
from app.domain.entities.roster import Roster
from app.domain.entities.schedule import Matchup, PlayoffType, Schedule, ScheduleWeek
from app.domain.enums.position_type import PositionType
from app.domain.enums.week_type import WeekType
from pydantic.main import BaseModel


class PositionSummary(BaseModel):
    position_id: int
    name: str
    position_type: PositionType
    player_id: Optional[str]
    player_name: Optional[str]

    @staticmethod
    def from_position(position: LeaguePosition) -> PositionSummary:
        summary = PositionSummary(
            position_id=position.id,
            name=position.name,
            position_type=position.position_type,
            player_id=position.player.player_id if position.player else None,
            player_name=position.player.full_name if position.player else None,
        )

        return summary


class RosterSummary(BaseModel):
    roster_id: str
    name: str
    record: str
    points_for: float
    regular_season_rank: int
    positions: List[PositionSummary]

    @staticmethod
    def from_roster(roster: Roster) -> RosterSummary:
        positions = [PositionSummary.from_position(p) for p in roster.positions.values()]

        summary = RosterSummary(
            roster_id=roster.id,
            name=roster.name,
            record=roster.record,
            points_for=roster.points_for,
            regular_season_rank=roster.rank,
            positions=positions,
        )

        return summary


class MatchupSummary(BaseModel):
    away_id: Optional[str]
    away_name: Optional[str]
    home_id: Optional[str]
    home_name: Optional[str]
    matchup_type: str
    away_score: Optional[float] | Optional[int]
    home_score: Optional[float] | Optional[int]

    @staticmethod
    def from_matchup(matchup: Matchup) -> MatchupSummary:
        summary = MatchupSummary(
            away_id=matchup.away.id if matchup.away else None,
            away_name=matchup.away.name if matchup.away else None,
            away_score=matchup.away_score,
            home_id=matchup.home.id if matchup.home else None,
            home_name=matchup.home.name if matchup.home else None,
            home_score=matchup.home_score,
            matchup_type=matchup.type.display(),
        )

        return summary


class WeekSummary(BaseModel):
    week_id: Optional[str]
    week_number: int
    week_type: WeekType
    heading: Optional[str]
    matchups: List[MatchupSummary] = []

    @staticmethod
    def from_week(week: ScheduleWeek) -> WeekSummary:
        matchups = [MatchupSummary.from_matchup(m) for m in week.matchups]

        summary = WeekSummary(
            week_id=week.week_id,
            week_number=week.week_number,
            week_type=week.week_type,
            heading=week.heading,
            matchups=matchups,
        )

        return summary


class DraftPickSummary(BaseModel):
    pick_number: int
    roster_id: Optional[str]
    player_id: Optional[str]
    player_name: Optional[str]
    nominator: Optional[str]
    bid: Optional[int]
    result: Optional[str]

    @staticmethod
    def create_from_draft_slot(draft_slot: DraftSlot) -> DraftPickSummary:
        return DraftPickSummary(
            pick_number=draft_slot.pick_number,
            roster_id=draft_slot.roster_id,
            player_id=draft_slot.player.player_id if draft_slot.player else None,
            player_name=draft_slot.player.full_name if draft_slot.player else None,
            nominator=draft_slot.nominator,
            bid=draft_slot.bid,
            result=draft_slot.result,
        )


class SeasonSummary(BaseEntity):
    season: int
    rosters: List[RosterSummary]
    champion: RosterSummary
    runner_up: RosterSummary
    playoff_type: PlayoffType
    weeks: List[WeekSummary]
    draft_picks: List[DraftPickSummary]

    @staticmethod
    def create_from_schedule(season: int, schedule: Schedule, rosters: List[Roster], draft: Draft) -> SeasonSummary:
        rosters_summaries = [RosterSummary.from_roster(r) for r in rosters]
        weeks_summaries = [WeekSummary.from_week(w) for w in schedule.weeks]

        last_week = weeks_summaries[-1]
        assert last_week.week_type == WeekType.CHAMPIONSHIP

        championship = last_week.matchups[0]

        champion_id = championship.away_id if championship.away_score > championship.home_score else championship.home_id
        runner_up_id = championship.away_id if champion_id == championship.home_id else championship.home_id

        champion = next(r for r in rosters_summaries if r.roster_id == champion_id)
        runner_up = next(r for r in rosters_summaries if r.roster_id == runner_up_id)

        draft_picks = [DraftPickSummary.create_from_draft_slot(slot) for slot in draft.slots]

        summary = SeasonSummary(
            id=season,
            season=season,
            rosters=rosters_summaries,
            playoff_type=schedule.playoff_type,
            weeks=weeks_summaries,
            champion=champion,
            runner_up=runner_up,
            draft_picks=draft_picks,
        )

        return summary
