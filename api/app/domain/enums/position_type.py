from __future__ import annotations

from enum import Enum

from api.app.core.logging import Logger


class PositionType(str, Enum):
    qb = "qb"
    rb = "rb"
    wr = "wr"
    k = "k"
    lb = "lb"
    dl = "dl"
    db = "db"
    ol = "ol"
    o_flex = "o-flex"
    d_flex = "d-flex"
    flex = "flex"
    ir = "ir"
    bye = "bye"
    bench = "bench"
    other = "other"

    @staticmethod
    def all():
        '''Returns a list of all PositionType items which are used in the system (excludes other and OL)'''
        return [e.name for e in PositionType if e not in [PositionType.other, PositionType.ol]]

    def display_name(self):
        if self == PositionType.qb:
            return "Quarterback"

        if self == PositionType.rb:
            return "Running Back"

        if self == PositionType.wr:
            return "Receiver"

        if self == PositionType.k:
            return "Kicker"

        if self == PositionType.lb:
            return "Linebacker"

        if self == PositionType.dl:
            return "Defensive Lineman"

        if self == PositionType.db:
            return "Defensive Back"

        if self == PositionType.ol:
            return "Offensive Lineman"

        return self.capitalize()

    def is_active_position_type(self):
        return self not in [PositionType.ir, PositionType.bye]

    def is_starting_position_type(self):
        return self not in [PositionType.ir, PositionType.bye, PositionType.bench]

    def is_reserve_type(self):
        return self in [PositionType.ir, PositionType.bye]

    def is_eligible_for(self, position_type: PositionType):
        if self == PositionType.ir or self == PositionType.bye:
            return True

        if self == position_type:
            return True

        if self == PositionType.bench:
            return True

        if self == PositionType.o_flex:
            return position_type in [PositionType.rb, PositionType.wr, PositionType.k]

        if self == PositionType.d_flex:
            return position_type in [PositionType.lb, PositionType.dl, PositionType.db]

        if self == PositionType.flex:
            return position_type in [PositionType.k, PositionType.rb, PositionType.wr, PositionType.lb, PositionType.dl, PositionType.db]

        return self == position_type

    @staticmethod
    def from_cfl_roster(abbreviation: str):
        if abbreviation in ["DE", "DT"]:
            abbreviation = "DL"

        if abbreviation in ["OL", "LS", "G", "T"]:
            abbreviation = "ol"

        if abbreviation in ["P"]:
            abbreviation = "K"

        if abbreviation in ["FB"]:
            abbreviation = "RB"

        if abbreviation in ["SB", "TE"]:
            abbreviation = "WR"

        if abbreviation in ["S", "CB"]:
            abbreviation = "DB"

        try:
            return PositionType(abbreviation.lower())
        except Exception:
            Logger.warn(f"Encountered unknown position '{abbreviation}'")
            return PositionType.other
