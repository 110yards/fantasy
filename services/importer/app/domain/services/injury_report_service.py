from datetime import datetime

import requests
from dateutil import parser
from fastapi import Depends
from strivelogger import StriveLogger

from app.config.settings import Settings, get_settings
from app.domain.constants.gracenote import map_gracenote_team
from app.domain.models.injury_report import (
    InjuryPlayer,
    InjuryReport,
    InjuryStatus,
    InjuryStatuses,
    PlayerInjuryStatus,
)
from app.domain.models.player import Player, Team
from app.domain.store.player_store import PlayerStore, create_player_store


class InjuryReportService:
    def __init__(
        self,
        settings: Settings,
        player_store: PlayerStore,
    ):
        self.settings = settings
        self.player_store = player_store
        self.players: dict[int, Player] = {}

    def get_report(self) -> InjuryReport:
        url = "https://prod-ghosts-api-widgets.prod.sports.gracenote.com/api/Injuries?customerId=375&editionId=%2Fsport%2Ffootball%2Fseason:245&filter=%7B%22include%22:%5B%22team%22,%22players%22%5D,%22fields%22:%7B%22teamInjuries%22:%7B%22injuries%22:%7B%22playerId%22:true,%22location%22:true,%22teamId%22:true,%22startDate%22:true,%22injury%22:true,%22status%22:true,%22displayStatus%22:true,%22note%22:true,%22lastUpdated%22:true%7D%7D,%22players%22:%7B%22playerFirstName%22:true,%22playerLastName%22:true,%22thumbnailUrl%22:true,%22seasonDetails%22:%7B%22position%22:%7B%22positionShortName%22:true%7D%7D%7D,%22team%22:%7B%22teamName%22:true,%22teamShortName%22:true,%22type%22:true%7D%7D%7D&languageCode=2&module=na_teamsports&sportId=%2Fsport%2Ffootball&type=injuries"
        response = requests.get(url, headers={"Referer": "https://widgets.sports.gracenote.com/"})

        if response.status_code != 200:
            raise Exception(f"Error getting injuries: {response.status_code}")

        injury_data = response.json()["injuries"]["teamInjuries"]

        players = self.player_store.get_players(datetime.now().year)
        self.players_by_gracenote_id = {player.gracenote_id: player for player in players.values()}
        self.players_by_slug = {player_slug(player): player for player in players.values()}

        injuries: list[PlayerInjuryStatus] = []

        for team_data in injury_data:
            injuries.extend(self.map_team_injuries(team_data))

        return InjuryReport(reports=injuries)

    def map_team_injuries(self, injuries_data: dict) -> list[PlayerInjuryStatus]:
        injuries = []
        for injury_data in injuries_data["injuries"]:
            injury = self.map_player_injury(injury_data)
            if injury:
                injuries.append(injury)

        return injuries

    def map_player_injury(self, injury_data: dict) -> PlayerInjuryStatus:
        gracenote_id = injury_data["playerId"]
        team = map_gracenote_team(injury_data["team"][0]["teamShortName"])

        slug = create_slug(team, injury_data["playerFirstName"], injury_data["playerLastName"])

        if gracenote_id in self.players_by_gracenote_id:
            StriveLogger.info(f"Found player by gracenote id: {gracenote_id}")
            player = self.players_by_gracenote_id[gracenote_id]
        elif slug in self.players_by_slug:
            StriveLogger.info(f"Found player by slug: {slug}")
            player = self.players_by_slug[slug]
            player.gracenote_id = gracenote_id
        else:
            StriveLogger.warn(f"Could not find player by gracenote id or slug: {gracenote_id} - {slug}")
            return None

        return PlayerInjuryStatus(
            player=InjuryPlayer(**player.dict()),
            status=InjuryStatus(
                status_id=map_injury_status(injury_data["status"]),
                text=injury_data["displayStatus"],
                injury=injury_data["injury"],
                last_updated=parser.parse(injury_data["lastUpdated"]).strftime("%Y-%m-%d"),
            ),
        )


def map_injury_status(status_text: str) -> InjuryStatuses:
    match status_text:
        case "questionable":
            return InjuryStatuses.Questionable
        case "Six-Game Injured List":
            return InjuryStatuses.InjuredSixGames
        case "out":
            return InjuryStatuses.Inactive
        case "probable":
            return InjuryStatuses.Probable
        case _:
            StriveLogger.warn(f"Unknown injury status: {status_text}")
            return InjuryStatuses.Inactive


def player_slug(player: Player) -> str:
    return create_slug(player.team, player.first_name, player.last_name)


def create_slug(team: Team, first_name: str, last_name: str) -> str:
    return f"{team.abbreviation}-{first_name}-{last_name}".lower()


def create_injury_report_service(
    settings: Settings = Depends(get_settings),
    player_store: PlayerStore = Depends(create_player_store),
) -> InjuryReportService:
    return InjuryReportService(
        settings=settings,
        player_store=player_store,
    )
