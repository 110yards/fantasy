from enum import Enum


class MatchupType(str, Enum):
    REGULAR = "regular"
    PLAYOFF = "playoff"
    PLAYOFF_BYE = "playoff_bye"
    LOSER = "loser"
    CHAMPIONSHIP = "championship"

    def display(self):
        if self == MatchupType.REGULAR:
            return "Regular season matchup"
        if self == MatchupType.PLAYOFF:
            return "Playoff"
        if self == MatchupType.PLAYOFF_BYE:
            return "Playoff Bye"
        if self == MatchupType.LOSER:
            return "Loser match"
        if self == MatchupType.CHAMPIONSHIP:
            return "Championship"
