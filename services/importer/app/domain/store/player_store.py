from datetime import datetime, timezone

from fastapi import Depends

from app.config.settings import Settings, get_settings
from app.domain.models.player import Player

from ...core.firestore_client import FirestoreClient, create_firestore_client
from ...core.rtdb_client import RTDBClient, create_rtdb_client


class PlayerStore:
    def __init__(self, settings: Settings, firestore_client: FirestoreClient, rtdb_client: RTDBClient):
        self.settings = settings
        self.firestore_client = firestore_client
        self.rtdb_client = rtdb_client

    def get_players(self) -> dict[str, Player]:
        path = "players"

        players = self.firestore_client.get(path)
        players = [Player(**player) for player in players]
        return {player.player_id: player for player in players}

    def save_player(self, player: Player) -> None:
        path = f"players/{player.player_id}"
        player.last_updated = datetime.now(timezone.utc)

        self.firestore_client.set(path, player.model_dump())

    def save_players_for_approval(self, players: list[Player]) -> None:
        count = len(players)

        players = [player.model_dump() for player in players]

        for player in players:
            player["birth_date"] = player["birth_date"].isoformat()

        data = {
            "count": count,
            "players": players,
        }
        path = "players_for_approval"
        self.rtdb_client.set(path, data)


def create_player_store(
    settings: Settings = Depends(get_settings),
    firestore_client: FirestoreClient = Depends(create_firestore_client),
    rtdb_client: RTDBClient = Depends(create_rtdb_client),
) -> PlayerStore:
    return PlayerStore(
        settings=settings,
        firestore_client=firestore_client,
        rtdb_client=rtdb_client,
    )
