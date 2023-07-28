from typing import List

from app.core.firestore_proxy import FirestoreProxy, Query
from app.domain.entities.scheduled_game import ScheduledGame
from google.cloud.firestore_v1.transaction import Transaction


def create_scheduled_game_repository():
    firestore = FirestoreProxy(ScheduledGame.parse_obj)
    return ScheduledGameRepository(firestore)


class ScheduledGameRepository:
    def __init__(self, firestore: FirestoreProxy[ScheduledGame]):
        self.firestore = firestore

    def get_all(self, season: int) -> List[ScheduledGame]:
        return self.firestore.get_all(f"season/{season}/scheduled_game")

    def set(self, season: int, scheduled_game: ScheduledGame, transaction: Transaction = None):
        self.firestore.set(f"season/{season}/scheduled_game", scheduled_game, transaction)

    def get_for_week(self, season: int, week_number: int) -> List[ScheduledGame]:
        query = Query("week", "==", week_number)
        return self.firestore.where(f"season/{season}/scheduled_game", query)
