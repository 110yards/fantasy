from fastapi import Depends

from app.config.settings import Settings, get_settings
from app.core.rtdb_client import RTDBClient, create_rtdb_client
from app.domain.models.player import Player


class PlayerStore:
    def __init__(self, settings: Settings, rtdb_client: RTDBClient):
        self.settings = settings
        self.rtdb_client = rtdb_client

    def path(self, year: int) -> str:
        return f"{self.settings.environment.lower()}/players/{year}"

    def get_players(self, year: int) -> dict[str, Player]:
        existing_players = self.rtdb_client.get(self.path(year))
        existing_players = [Player(**existing) for existing in existing_players.values()] if existing_players else {}

        return {player.player_id: player for player in existing_players}

    def save_player(self, year: int, player: Player) -> None:
        path = self.path(year)
        self.rtdb_client.set(f"{path}/{player.player_id}", player.dict())


def create_player_store(
    settings: Settings = Depends(get_settings), rtdb_client: RTDBClient = Depends(create_rtdb_client)
) -> PlayerStore:
    return PlayerStore(settings=settings, rtdb_client=rtdb_client)
