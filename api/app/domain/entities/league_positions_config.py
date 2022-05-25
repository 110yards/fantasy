from __future__ import annotations
from api.app.domain.entities.league_position import LeaguePosition


from api.app.core.annotate_args import annotate_args
from api.app.core.base_entity import BaseEntity
from api.app.domain.enums.position_type import PositionType


@annotate_args
class LeaguePositionsConfig(BaseEntity):
    id: str = "positions"
    qb: int = 1
    rb: int = 1
    wr: int = 2
    k: int = 1
    lb: int = 1
    dl: int = 1
    db: int = 1
    o_flex: int = 0
    d_flex: int = 0
    flex: int = 0
    ir: int = 1
    bye: int = 1
    bench: int = 2
    allow_bench_qb: bool = False
    allow_bench_rb: bool = False
    allow_bench_k: bool = False

    def active_position_count(self):
        return self.qb + self.rb + self.wr + self.k + self.lb + self.dl + self.db + self.o_flex + self.d_flex + self.flex + self.bench

    @staticmethod
    def create_positions_for_type(starting_id: int, count: int, prefix: str, position_type: PositionType) -> list[LeaguePosition]:
        positions = []
        for i in range(0, count):
            positions.append(LeaguePosition.create(starting_id + i, f"{prefix}{i+1}", position_type))

        return positions

    def create_positions(self) -> dict[int, LeaguePosition]:
        positions = []  # type: list[LeaguePosition]

        starting_id = 1

        positions.extend(LeaguePositionsConfig.create_positions_for_type(starting_id, self.qb, "QB", PositionType.qb))
        starting_id = starting_id + self.qb

        positions.extend(LeaguePositionsConfig.create_positions_for_type(starting_id, self.rb, "RB", PositionType.rb))
        starting_id = starting_id + self.rb

        positions.extend(LeaguePositionsConfig.create_positions_for_type(starting_id, self.wr, "WR", PositionType.wr))
        starting_id = starting_id + self.wr

        positions.extend(LeaguePositionsConfig.create_positions_for_type(starting_id, self.o_flex, "OFlex", PositionType.o_flex))
        starting_id = starting_id + self.o_flex

        positions.extend(LeaguePositionsConfig.create_positions_for_type(starting_id, self.k, "K", PositionType.k))
        starting_id = starting_id + self.k

        positions.extend(LeaguePositionsConfig.create_positions_for_type(starting_id, self.lb, "LB", PositionType.lb))
        starting_id = starting_id + self.lb

        positions.extend(LeaguePositionsConfig.create_positions_for_type(starting_id, self.dl, "DL", PositionType.dl))
        starting_id = starting_id + self.dl

        positions.extend(LeaguePositionsConfig.create_positions_for_type(starting_id, self.db, "DB", PositionType.db))
        starting_id = starting_id + self.db

        positions.extend(LeaguePositionsConfig.create_positions_for_type(starting_id, self.d_flex, "DFlex", PositionType.d_flex))
        starting_id = starting_id + self.d_flex

        positions.extend(LeaguePositionsConfig.create_positions_for_type(starting_id, self.flex, "Flex", PositionType.flex))
        starting_id = starting_id + self.flex

        positions.extend(LeaguePositionsConfig.create_positions_for_type(starting_id, self.ir, "IR", PositionType.ir))
        starting_id = starting_id + self.ir

        positions.extend(LeaguePositionsConfig.create_positions_for_type(starting_id, self.bye, "BYE", PositionType.bye))
        starting_id = starting_id + self.bye

        positions.extend(LeaguePositionsConfig.create_positions_for_type(starting_id, self.bench, "BN", PositionType.bench))
        starting_id = starting_id + self.bench

        return {str(position.id): position for position in positions}
