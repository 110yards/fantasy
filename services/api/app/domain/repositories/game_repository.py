from typing import List

from google.cloud.firestore_v1.transaction import Transaction

from app.yards_py.core.base_repository import Query
from app.yards_py.core.firestore_proxy import FirestoreProxy
from app.yards_py.domain.entities.game import Game


def create_game_repository():
    firestore = FirestoreProxy[Game](Game.parse_obj)
    return GameRepository(firestore)


class GameRepository:
    def __init__(self, firestore: FirestoreProxy):
        self.firestore = firestore

    @staticmethod
    def path(season: int):
        return f"season/{season}/game"

    def get(self, season, game_id, transaction: Transaction = None) -> Game:
        return self.firestore.get(GameRepository.path(season), game_id, transaction)

    def get_all(self, season, transaction: Transaction = None) -> List[Game]:
        return self.firestore.get_all(GameRepository.path(season), transaction)

    def set(self, season, game: Game, transaction: Transaction = None):
        return self.firestore.set(GameRepository.path(season), game, transaction)

    def for_week(self, season: int, week: int) -> List[Game]:
        query = Query("week", "==", week)
        return self.firestore.where(GameRepository.path(season), query)

    def delete_all(self, season: int):
        self.firestore.delete_all(GameRepository.path(season))
