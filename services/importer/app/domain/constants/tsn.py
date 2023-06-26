from enum import Enum

from app.domain.models.player import Position, Team


class TeamIds(int, Enum):
    BC = 1068
    CGY = 1069
    EDM = 1070
    HAM = 1071
    MTL = 1072
    OTT = 38354
    SSK = 1073
    TOR = 1074
    WPG = 1075


def map_tsn_teams(team_id: int) -> Team:
    match team_id:
        case TeamIds.BC:
            return Team.bc()
        case TeamIds.CGY:
            return Team.cgy()
        case TeamIds.EDM:
            return Team.edm()
        case TeamIds.HAM:
            return Team.ham()
        case TeamIds.MTL:
            return Team.mtl()
        case TeamIds.OTT:
            return Team.ott()
        case TeamIds.SSK:
            return Team.ssk()
        case TeamIds.TOR:
            return Team.tor()
        case TeamIds.WPG:
            return Team.wpg()
        case _:
            return Team.free_agent()


def map_tsn_position(abbr: str) -> Position:
    match abbr:
        case "QB":
            return Position.quarterback()
        case "RB":
            return Position.runningback()
        case "FB":
            return Position.fullback()
        case "DL":
            return Position.defensiveline()
        case "DB":
            return Position.defensiveback()
        case "WR":
            return Position.widereceiver()
        case "LB":
            return Position.linebacker()
        case "OL":
            return Position.offensiveline()
        case "K":
            return Position.kicker()
        case "P":
            return Position.punter()
        case "LS":
            return Position.longsnapper()
        case "DE":
            return Position.defensiveend()
        case "G":
            return Position.guard()
        case "DT":
            return Position.defensivetackle()
        case "S":
            return Position.safety()
        case "T":
            return Position.tackle()

        case _:
            return Position.unknown()
