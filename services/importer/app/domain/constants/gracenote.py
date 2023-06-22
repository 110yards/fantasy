from app.domain.models.player import Team


def map_gracenote_team(team_short_name: str) -> Team:
    match team_short_name:
        case "BC":
            return Team.bc()
        case "CGY":
            return Team.cgy()
        case "EDM":
            return Team.edm()
        case "HAM":
            return Team.ham()
        case "MTL":
            return Team.mtl()
        case "OTT":
            return Team.ott()
        case "SSK":
            return Team.ssk()
        case "TOR":
            return Team.tor()
        case "WPG":
            return Team.wpg()
        case _:
            return Team.free_agent()
