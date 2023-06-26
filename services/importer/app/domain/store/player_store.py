from fastapi import Depends

from app.config.settings import Settings, get_settings
from app.domain.models.player import Player

from ...core.firestore_client import FirestoreClient, create_firestore_client


class PlayerStore:
    def __init__(self, settings: Settings, firestore_client: FirestoreClient):
        self.settings = settings
        self.firestore_client = firestore_client

    def get_players(self, year: int) -> dict[str, Player]:
        path = "players"

        players = self.firestore_client.get(path)
        players = [Player(**player) for player in players]
        return {player.player_id: player for player in players}

    def save_player(self, player: Player) -> None:
        path = f"players/{player.player_id}"
        self.firestore_client.set(path, player.model_dump())


def create_player_store(settings: Settings = Depends(get_settings), firestore_client: FirestoreClient = Depends(create_firestore_client)) -> PlayerStore:
    return PlayerStore(settings=settings, firestore_client=firestore_client)
