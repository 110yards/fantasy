from enum import Enum


class EventType(str, Enum):
    preseason = "preseason"
    regular = "regular"
    division_semi = "division-semifinal"
    division_final = "division-final"
    grey_cup = "grey-cup"
