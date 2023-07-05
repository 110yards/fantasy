from datetime import datetime, timezone
from typing import Optional

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

    def get_player_by_boxscore_source_id(self, boxscore_source_id: str) -> Optional[Player]:
        path = "players"
        query = self.firestore_client.query(path, "boxscore_source_id", "==", boxscore_source_id)
        players = self.firestore_client.get_query(query)

        players = [Player(**player) for player in players]
        return players[0] if players else None

    def save_player(self, player: Player) -> None:
        path = f"players/{player.player_id}"
        player.last_updated = datetime.now(timezone.utc)

        self.firestore_client.set(path, player.model_dump())

    def save_players_for_approval(self, players: list[Player]) -> None:
        for player in players:
            path = f"mod/approvals/players/{player.player_id}"
            self.firestore_client.set(path, player.model_dump())

    def get_player_by_team(self, team_abbr: str) -> dict[str, Player]:
        path = "players"
        query = self.firestore_client.query(path, "team_abbr", "==", team_abbr)
        players = self.firestore_client.get_query(query)

        players = [Player(**player) for player in players]
        return {player.player_id: player for player in players}


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
