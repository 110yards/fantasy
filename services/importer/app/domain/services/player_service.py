from datetime import datetime
from typing import Optional

import requests
from dateutil import parser
from fastapi import Depends
from strivelogger import StriveLogger

from app.config.settings import Settings, get_settings
from app.domain.models.player import InjuryDetails, InjuryStatus, Player, Position
from app.domain.store.schedule_store import ScheduleStore, create_schedule_store


class PlayerService:
    def __init__(
        self,
        settings: Settings,
        schedule_store: ScheduleStore,
    ):
        self.settings = settings
        self.schedule_store = schedule_store

    def get_players(self) -> list[Player]:
        season_id = self.schedule_store.get_boxscore_source_season_id(datetime.now().year)
        if not season_id:
            raise ValueError("No boxscore source season id found")

        players_data = self.load_players_data(season_id)
        injury_data = self.load_injury_data(season_id)

        injuries = map_injuries_data(injury_data)
        players = map_players(players_data, injuries)

        return players

    def load_players_data(self, season_id: str) -> list[Player]:
        url = self.settings.players_url_format.replace("{season_id}", season_id)
        StriveLogger.info(f"Fetching {url}")
        response = requests.get(url, headers={"Referer": self.settings.players_url_referer})

        data = response.json()
        if not data:
            return []

        return data["playerListWidgetData"]["players"]

    def load_injury_data(self, season_id: str) -> list[InjuryDetails]:
        url = self.settings.injuries_url_format.replace("{season_id}", season_id)
        StriveLogger.info(f"Fetching {url}")
        response = requests.get(url, headers={"Referer": self.settings.injuries_url_referer})

        data = response.json()
        if not data:
            return []

        return data["injuries"]["teamInjuries"]


def map_injuries_data(injuries_data: dict) -> dict[str, InjuryDetails]:
    injuries = {}

    for team_injury_data in injuries_data:
        for injury_data in team_injury_data["injuries"]:
            injury_player_id = injury_data["playerId"]
            injuries[injury_player_id] = map_player_injury(injury_data)

    return injuries


def map_player_injury(injury_data: dict) -> InjuryDetails:
    return InjuryDetails(
        status_id=map_injury_status(injury_data["status"]),
        text=injury_data.get("displayStatus") or "",
        injury=injury_data["injury"],
        last_updated=parser.parse(injury_data["lastUpdated"]).strftime("%Y-%m-%d"),
    )


def map_injury_status(status_text: str) -> InjuryStatus:
    match status_text:
        case "questionable":
            return InjuryStatus.Questionable
        case "Six-Game Injured List":
            return InjuryStatus.InjuredSixGames
        case "out":
            return InjuryStatus.Out
        case "probable":
            return InjuryStatus.Probable
        case _:
            StriveLogger.warn(f"Unknown injury status: {status_text}")
            return InjuryStatus.Out


def map_players(players_data: dict, injuries: dict[str, InjuryDetails]) -> list[Player]:
    players = []

    for player_data in players_data:
        player = map_player(player_data, injuries)

        if player:
            players.append(player)

    return players


def map_player(player_data: dict, injuries: dict[str, InjuryDetails]) -> Optional[Player]:
    displayName = f"{player_data['playerFirstName']} {player_data['playerLastName']}"
    if len(player_data["seasonDetails"]["position"]) != 1:
        StriveLogger.warn(f"Found multiple positions for player: {displayName}")
        return None

    birth_date = parser.isoparse(player_data.get("birthdate")) if player_data.get("birthdate") else None
    if not birth_date:
        StriveLogger.warn(f"No birthdate for player: {displayName}")
        return None

    position_short = player_data["seasonDetails"]["position"][0]["positionShortName"]
    position = map_position(position_short)

    if not position:
        StriveLogger.warn(f"Unknown position '{position_short}' for player: {displayName}")
        return None

    uniform = player_data["seasonDetails"].get("number")
    team_abbr = map_boxscore_source_team_id(player_data["teamId"])

    height_inches = int(player_data["height"]["value"]) if player_data.get("height") else 0
    height_feet = height_inches // 12 if height_inches else None
    height_inches = height_inches % 12 if height_inches else None
    height = f"{height_feet}'{height_inches}" if height_feet and height_inches else None

    birth_place = player_data.get("birthplace")

    if birth_place and "," in birth_place:
        birth_place = birth_place.replace(",", ", ")

    player = Player(
        first_name=player_data["playerFirstName"],
        last_name=player_data["playerLastName"],
        boxscore_source_id=player_data["playerId"],
        birth_date=birth_date,
        birth_place=birth_place,
        height=height,
        weight=player_data.get("weight", {"value": None})["value"],
        rookie_year=None,
        canadian_player=player_data.get("location")["country"] == "CAN" if player_data.get("location") else True,
        image_url=None,
        school=player_data.get("school"),
        position=position,
        team_abbr=team_abbr,
        uniform=uniform,
        injury_status=injuries.get(player_data["playerId"]),
        seasons=[datetime.now().year],
    )

    player.player_id = player.computed_player_id
    return player


def map_position(abbr: str) -> Optional[Position]:
    abbr = abbr.lower()

    return Position(abbr) if abbr in Position.__members__.values() else None


def map_boxscore_source_team_id(team_id: str) -> str:
    match team_id:
        case "/sport/football/team:241":
            return "bc"

        case "/sport/football/team:243":
            return "cgy"

        case "/sport/football/team:242":
            return "edm"

        case "/sport/football/team:246":
            return "ham"

        case "/sport/football/team:249":
            return "mtl"

        case "/sport/football/team:947":
            return "ott"

        case "/sport/football/team:244":
            return "ssk"

        case "/sport/football/team:247":
            return "tor"

        case "/sport/football/team:245":
            return "wpg"

        case _:
            raise ValueError(f"Unknown team id '{team_id}'")


def create_player_service(
    settings: Settings = Depends(get_settings),
    schedule_store: ScheduleStore = Depends(create_schedule_store),
) -> PlayerService:
    return PlayerService(
        settings=settings,
        schedule_store=schedule_store,
    )
