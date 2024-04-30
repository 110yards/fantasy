from typing import List

from google.cloud.firestore_v1.transaction import Transaction

from yards_py.core.firestore_proxy import FirestoreProxy, Query
from yards_py.domain.entities.scheduled_game import ScheduledGame


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
