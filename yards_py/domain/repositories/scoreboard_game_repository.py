

from typing import List
from google.cloud.firestore_v1.transaction import Transaction
from yards_py.core.firestore_proxy import FirestoreProxy
from ..entities.scoreboard import ScoreboardGame



class ScoreboardGameRepository():
    def __init__(self, firestore: FirestoreProxy[ScoreboardGame]):
        self.firestore = firestore

    @staticmethod
    def path(season: int):
        return f"season/{season}/scoreboard_game"

    def get(self, season, player_id, transaction: Transaction = None) -> ScoreboardGame:
        return self.firestore.get(ScoreboardGameRepository.path(season), player_id, transaction)

    def get_all(self, season, transaction: Transaction = None) -> List[ScoreboardGame]:
        return self.firestore.get_all(ScoreboardGameRepository.path(season), transaction)

    def set(self, season, game: ScoreboardGame, transaction: Transaction = None):
        return self.firestore.set(ScoreboardGameRepository.path(season), game, transaction)

def create_scoreboard_game_repository():
    firestore = FirestoreProxy[ScoreboardGame](ScoreboardGame.parse_obj)
    return ScoreboardGameRepository(firestore)
