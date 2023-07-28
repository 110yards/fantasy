from __future__ import annotations

from datetime import datetime
from functools import cmp_to_key
from typing import List, Optional, Union

from app.yards_py.core.base_entity import BaseEntity
from app.yards_py.domain.entities.league_position import LeaguePosition
from app.yards_py.domain.entities.waiver_bid import WaiverBid
from app.yards_py.domain.enums.position_type import PositionType
from pydantic import field_validator

DEFAULT_WAIVER_BUDGET = 100


class Roster(BaseEntity):
    name: str
    draft_budget: Optional[int] = None
    current_matchup: Optional[str] = None
    positions: dict[str, LeaguePosition]
    record: str = "0-0"
    points_for: float = 0.0
    points_against: float = 0.0
    transaction_count: int = 0
    last_week_result: str = "-"
    waiver_budget: int = DEFAULT_WAIVER_BUDGET
    active_player_count: int = 0
    this_week_points_for: float = 0.0
    this_week_bench_points_for: float = 0.0
    waiver_bids: List[WaiverBid] = []
    processed_waiver_bids: List[WaiverBid] = []
    wins: int = 0
    losses: int = 0
    ties: int = 0
    wl_points: int = 0
    rank: int = 1
    name_changes_banned: bool = False

    @field_validator("positions", mode="before")
    @classmethod
    def validate_positions(cls, v):
        if isinstance(v, list):
            return {}

    # @model_validator(mode="before")
    # def validate_positions(self, data):
    #     positions = data.get("positions")

    #     if not positions and positions is not None:
    #         data.pop("positions")

    #     return data

    def reset(self):
        self.current_matchup = None
        self.positions = {}
        self.record = "0-0"
        self.points_for = 0.0
        self.points_against = 0.0
        self.transaction_count = 0
        self.last_week_result = "-"
        self.waiver_budget = DEFAULT_WAIVER_BUDGET
        self.active_player_count = 0
        self.this_week_points_for = 0.0
        self.this_week_bench_points_for = 0.0
        self.waiver_bids = []
        self.processed_waiver_bids = []
        self.wins = 0
        self.losses = 0
        self.ties = 0
        self.wl_points = 0
        self.rank = 1

    def find_player_position(self, player_id: str) -> Union[LeaguePosition, None]:
        for position_id in self.positions:
            position = self.positions[position_id]
            if position.player and position.player.player_id == player_id:
                return position

    def calculate_score(self) -> float:
        score = 0.0

        for position_id in self.positions:
            position = self.positions[position_id]

            if position.is_starting_position_type():
                score += position.game_score

        return score

    def calculate_bench_score(self) -> float:
        score = 0.0

        for position_id in self.positions:
            position = self.positions[position_id]

            if not position.is_starting_position_type():
                score += position.game_score

        return score

    def count_position_player(self, type: PositionType, ignore_reserve=True) -> int:
        return len(
            [
                position
                for position in self.positions.values()
                if position.player and position.player.position == type and (not ignore_reserve or not position.is_reserve_type())
            ]
        )

    def count_qbs(self) -> int:
        return self.count_position_player(PositionType.qb)

    def count_rbs(self) -> int:
        return self.count_position_player(PositionType.rb)

    def count_kickers(self) -> int:
        return self.count_position_player(PositionType.k)

    @staticmethod
    def calculate_wl_points(roster: Roster) -> float:
        return (roster.wins * 2) + roster.ties

    @staticmethod
    def format_record(roster: Roster) -> str:
        if roster.ties:
            return f"{roster.wins}-{roster.losses}-{roster.ties}"
        else:
            return f"{roster.wins}-{roster.losses}"

    @staticmethod
    def sort(rosters: List[Roster]):
        return sorted(rosters, key=cmp_to_key(Roster.compare))

    @staticmethod
    def compare(roster1: Roster, roster2: Roster):
        if roster1.wl_points > roster2.wl_points:
            return -1

        if roster1.wl_points < roster2.wl_points:
            return 1

        if roster1.points_for > roster2.points_for:
            return -1

        if roster1.points_for < roster2.points_for:
            return 1

        roster1_diff = roster1.points_for - roster1.points_against
        roster2_diff = roster2.points_for - roster2.points_against

        if roster1_diff > roster2_diff:
            return -1

        if roster1_diff < roster2_diff:
            return 1

        # tied! flip a virtual coin
        tiebreak = int((datetime.now() - datetime(1, 1, 1)).total_seconds())

        if tiebreak % 2 == 0:
            return 1
        else:
            return -1
