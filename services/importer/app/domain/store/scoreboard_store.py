from typing import Optional

from fastapi import Depends

from app.config.settings import Settings, get_settings

from ...core.firestore_client import FirestoreClient, create_firestore_client
from ..models.scoreboard import Scoreboard


class ScoreboardStore:
    def __init__(self, settings: Settings, firestore_client: FirestoreClient):
        self.settings = settings
        self.firestore_client = firestore_client

    def get_scoreboard(self) -> Optional[Scoreboard]:
        path = "public/scoreboard"
        data = self.firestore_client.get(path)
        return Scoreboard(**data) if data else None

    def save_scoreboard(self, scoreboard: Scoreboard) -> None:
        path = "public/scoreboard"
        self.firestore_client.set(path, scoreboard.model_dump())


def create_scoreboard_store(
    settings: Settings = Depends(get_settings),
    firestore_client: FirestoreClient = Depends(create_firestore_client),
) -> ScoreboardStore:
    return ScoreboardStore(
        settings=settings,
        firestore_client=firestore_client,
    )
