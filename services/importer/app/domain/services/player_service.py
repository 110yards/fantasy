from typing import Optional

import requests
from fastapi import Depends
from strivelogger import StriveLogger

from app.config.settings import Settings, get_settings
from app.domain.constants.tsn import TeamIds, map_tsn_position, map_tsn_teams
from app.domain.models.player import Player, Position, Team


class PlayerService:
    def __init__(
        self,
        settings: Settings,
    ):
        self.settings = settings

    def get_players(self) -> list[Player]:
        return get_from_tsn()


def get_from_tsn() -> list[Player]:
    team_ids = [
        TeamIds.BC,
        TeamIds.CGY,
        TeamIds.EDM,
        TeamIds.HAM,
        TeamIds.MTL,
        TeamIds.OTT,
        TeamIds.SSK,
        TeamIds.TOR,
        TeamIds.WPG,
    ]

    players = []
    for team_id in team_ids:
        StriveLogger.info(f"Getting players for team: {team_id.name}")
        team_players = get_from_tsn_roster(team_id)

        if len(team_players) == 0:
            StriveLogger.warn(f"No players found for team: {team_id.name}")
            return []

        players.extend(team_players)

    return players


def get_from_tsn_roster(team_id: TeamIds) -> list[Player]:
    url = f"https://stats.sports.bellmedia.ca/sports/football/leagues/cfl/competitor/{team_id.value}/players"
    response = requests.get(url)

    data = response.json()

    players = [map_tsn_player(player_data) for player_data in data]
    return [player for player in players if player is not None]


def map_tsn_player(player_data: dict) -> Optional[Player]:
    position = map_tsn_position(player_data["positionShort"])

    if position == Position.unknown():
        StriveLogger.warn(f"Unknown position '{player_data['positionShort']}' for player: {player_data['displayName']}")

    team = map_tsn_teams(player_data["competitorId"], player_data["number"])

    if team == Team.free_agent():
        StriveLogger.warn(f"Found free agent on TSN roster somehow: {player_data['displayName']}")

    return Player(
        tsn_id=player_data["playerId"],
        first_name=player_data["firstName"],
        last_name=player_data["lastName"],
        birth_date=player_data["birthDate"],
        birth_place=player_data["birthPlace"],
        height=f"{player_data['heightFeet']}'{player_data['heightInches']}",
        weight=player_data["weight"],
        rookie_year=None,
        foreign_player=player_data.get("iso") != "CA",
        image_url=None,
        school=None,  # Not available in TSN data
        position=position,
        team=team,
    )


# uses the cfl list which is fucked
# class PlayerService:
#     def get_players(self) -> list[Player]:
#         url = "https://www.cfl.ca/wp-content/themes/cfl.ca/inc/admin-ajax.php?action=get_all_players"
#         response = requests.get(url)

#         data = response.json()

#         players = [map_cfl_player(player_data) for player_data in data["data"]]
#         return [player for player in players if player is not None]


# def map_cfl_player(player_data: list) -> Player:
#     StriveLogger.debug(f"Mapping player: {player_data}")

#     jersey: str = player_data[0]
#     name: str = player_data[1]
#     team_abbr: str = player_data[2]
#     position: str = player_data[3]
#     a_n_g: str = player_data[4]
#     height: str = player_data[5]
#     weight: str = player_data[6]
#     age: int = player_data[7]
#     college: str = player_data[8]
#     url: str = player_data[9]

#     parts = url.split("/")

#     cfl_central_id = parts[-2]

#     try:
#         cfl_central_id = int(cfl_central_id)
#     except ValueError:
#         StriveLogger.error(f"Could not determine CFL Central ID: {url}")
#         return None

#     if ", Jr" in name:
#         name = name.replace(", Jr", " Jr")

#     parts = name.split(",")
#     if len(parts) != 2:
#         StriveLogger.error(f"Invalid name: {name}")
#         return None

#     last_name = parts[0].strip()
#     first_name = parts[1].strip()

#     foreign_player = a_n_g != "N"

#     position = map_cfl_position(position)

#     if position is None:
#         StriveLogger.error(f"No position for player: {url}")
#         return None

#     weight = weight.replace("lbs", "").strip()
#     weight = int(weight) if weight else None

#     team = map_cfl_team(team_abbr)

#     pseudo_id = f"{team.abbreviation}-{last_name}-{first_name}".lower()

#     return Player(
#         cfl_central_id=cfl_central_id,
#         pseudo_id=pseudo_id,
#         stats_inc_id=0,
#         first_name=first_name,
#         last_name=last_name,
#         jersey=jersey,
#         team=team,
#         position=position,
#         age=age,
#         height=height,
#         weight=weight,
#         college=college,
#         foreign_player=foreign_player,
#         school=School(name=college),
#     )


# def map_cfl_team(abbr: str) -> Team:
#     match abbr:
#         case "BC":
#             return Team.bc()
#         case "CGY":
#             return Team.cgy()
#         case "EDM":
#             return Team.edm()
#         case "HAM":
#             return Team.ham()
#         case "MTL":
#             return Team.mtl()
#         case "OTT":
#             return Team.ott()
#         case "SSK":
#             return Team.ssk()
#         case "TOR":
#             return Team.tor()
#         case "WPG":
#             return Team.wpg()
#         case _:
#             return Team.free_agent()


# def map_cfl_position(pos: str) -> Optional[Position]:
#     match pos:
#         case "QB":
#             return Position(position_id=1, abbreviation="QB", description="Quarterback", offence_defence_or_special="O")
#         case "RB":
#             return Position(
#                 position_id=2, abbreviation="RB", description="Running Back", offence_defence_or_special="O"
#             )
#         case "FB":
#             return Position(position_id=3, abbreviation="FB", description="Full Back", offence_defence_or_special="O")
#         case "SB":
#             return Position(position_id=4, abbreviation="SB", description="Slot Back", offence_defence_or_special="O")
#         case "OL":
#             return Position(
#                 position_id=5, abbreviation="OL", description="Offensive Lineman", offence_defence_or_special="O"
#             )
#         case "G":
#             return Position(position_id=6, abbreviation="G", description="Guard", offence_defence_or_special="O")
#         case "DE":
#             return Position(
#                 position_id=7, abbreviation="DE", description="Defensive End", offence_defence_or_special="D"
#             )
#         case "WR":
#             return Position(
#                 position_id=8, abbreviation="WR", description="Wide Receiver", offence_defence_or_special="O"
#             )
#         case "LB":
#             return Position(position_id=11, abbreviation="LB", description="Linebacker", offence_defence_or_special="D")
#         case "DB":
#             return Position(
#                 position_id=12, abbreviation="DB", description="Defensive Back", offence_defence_or_special="D"
#             )
#         case "DL":
#             return Position(
#                 position_id=13, abbreviation="DL", description="Defensive Lineman", offence_defence_or_special="D"
#             )
#         case "P":
#             return Position(position_id=14, abbreviation="P", description="Punter", offence_defence_or_special="S")
#         case "K":
#             return Position(position_id=16, abbreviation="K", description="Kicker", offence_defence_or_special="S")
#         case "LS":
#             return Position(
#                 position_id=17, abbreviation="LS", description="Long Snapper", offence_defence_or_special="S"
#             )
#         case "DT":
#             return Position(
#                 position_id=18, abbreviation="DT", description="Defensive Tackle", offence_defence_or_special="D"
#             )
#         case "C":
#             return Position(position_id=19, abbreviation="C", description="Center", offence_defence_or_special="O")
#         case "CB":
#             return Position(
#                 position_id=21, abbreviation="CB", description="Corner Back", offence_defence_or_special="D"
#             )
#         case "S":
#             return Position(position_id=23, abbreviation="S", description="Safety", offence_defence_or_special="D")
#         case "T":
#             return Position(position_id=24, abbreviation="T", description="Tackle", offence_defence_or_special="D")
#         case "TE":
#             return Position(position_id=26, abbreviation="TE", description="Tight End", offence_defence_or_special="O")
#         case "ST":
#             return Position(
#                 position_id=27, abbreviation="ST", description="Special Teams Tackle", offence_defence_or_special="S"
#             )
#         case "RE":
#             return Position(position_id=28, abbreviation="RE", description="Right End", offence_defence_or_special="D")
#         case "NT":
#             return Position(
#                 position_id=30, abbreviation="NT", description="Nose Tackle", offence_defence_or_special="D"
#             )
#         case _:
#             return None


def create_player_service(
    settings: Settings = Depends(get_settings),
) -> PlayerService:
    return PlayerService(
        settings=settings,
    )
