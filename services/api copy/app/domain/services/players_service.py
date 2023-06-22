from fastapi import Depends

from app.config.settings import Settings, get_settings
from app.core.rtdb_client import RTDBClient, create_rtdb_client
from app.domain.api_response import ApiResponse


class PlayersService:
    def __init__(self, settings: Settings, rtdb_client: RTDBClient):
        self.settings = settings
        self.rtdb_client = rtdb_client

    def get_players(self, year: int) -> ApiResponse:
        env = self.settings.environment.lower()
        players_path = f"{env}/players/{year}"

        players = self.rtdb_client.get(players_path)
        injuries = self.rtdb_client.get(f"{env}/injury_report/reports") or []

        for injury in injuries:
            player_id = injury["player"]["player_id"]
            if player_id in players:
                players[player_id]["injury_status"] = injury["status"]

        players = list(players.values()) if players else []

        return ApiResponse(
            data=players,
            meta={
                "count": len(players),
            },
        )

    def get_player(self, year: int, player_id: str) -> ApiResponse:
        env = self.settings.environment.lower()
        path = f"{env}/players/{year}/{player_id}"

        player = self.rtdb_client.get(path)

        return ApiResponse(
            data=player,
        )


def create_players_service(
    settings: Settings = Depends(get_settings),
    rtdb_client: RTDBClient = Depends(create_rtdb_client),
) -> PlayersService:
    return PlayersService(settings=settings, rtdb_client=rtdb_client)
