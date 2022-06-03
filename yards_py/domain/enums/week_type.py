from enum import Enum


class WeekType(str, Enum):
    REGULAR = "regular"
    PLAYOFFS = "playoffs"
    CHAMPIONSHIP = "championship"

    def is_playoffs(self):
        return self in [WeekType.PLAYOFFS, WeekType.CHAMPIONSHIP]
