from __future__ import annotations

from enum import Enum

from yards_py.core.logging import Logger


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
    
        if abbreviation in ["de", "dt"]:
            abbreviation = "dl"

        if abbreviation in ["ol", "ls", "g", "t", "ot"]:
            abbreviation = "ol"

        if abbreviation in ["p"]:
            abbreviation = "k"

        if abbreviation in ["fb"]:
            abbreviation = "rb"

        if abbreviation in ["sb", "te"]:
            abbreviation = "wr"

        if abbreviation in ["s", "cb"]:
            abbreviation = "db"

        try:
            return PositionType(abbreviation.lower())
        except Exception:
            Logger.warn(f"Encountered unknown position '{abbreviation}'")
            return PositionType.other


def get_position_type_config():
    return [
        {"id": str(PositionType.qb.value), "display": "Quarterback", "is_player_position": True, "order": 0, "reserve": False, "short": "QB", "max": 1},
        {"id": str(PositionType.rb.value), "display": "Running Back", "is_player_position": True, "order": 10, "reserve": False, "short": "RB", "max": 1},
        {"id": str(PositionType.wr.value), "display": "Receiver", "is_player_position": True, "order": 20, "reserve": False, "short": "WR"},

        {"id": str(PositionType.o_flex.name), "display": "Offensive Flex", "is_player_position": False, "order": 25, "reserve": False, "short": "OFF",
         "description": "Accepts running backs, kickers and receivers", "api_id": "o-flex"},

        {"id": str(PositionType.k.value), "display": "Kicker", "is_player_position": True, "order": 30, "reserve": False, "short": "K", "max": 1},

        {"id": str(PositionType.dl.value), "display": "Defensive Line", "is_player_position": True, "order": 40, "reserve": False, "short": "DL"},
        {"id": str(PositionType.lb.value), "display": "Linebacker", "is_player_position": True, "order": 50, "reserve": False, "short": "LB"},
        {"id": str(PositionType.db.value), "display": "Defensive Back", "is_player_position": True, "order": 60, "reserve": False, "short": "DB"},

        {"id": str(PositionType.d_flex.name), "display": "Defensive Flex", "is_player_position": False, "order": 80, "reserve": False, "short": "DEF",
         "description": "Accepts linebacker, defensive line or defensive back", "api_id": "d-flex"},

        {"id": str(PositionType.flex.value), "display": "Flex", "is_player_position": False, "order": 90, "reserve": False, "short": "FX"},

        {"id": str(PositionType.bench.value), "display": "Bench", "is_player_position": False, "order": 100, "reserve": False, "short": "BN"},
        {"id": str(PositionType.bye.value), "display": "Bye", "is_player_position": False, "order": 110, "reserve": True, "short": "BYE"},
        {"id": str(PositionType.ir.value), "display": "Injury Reserve", "is_player_position": False, "order": 120, "reserve": True, "short": "IR"},
    ]
