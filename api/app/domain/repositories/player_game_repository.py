

from typing import List, Union
from fastapi.param_functions import Query
from google.cloud.firestore_v1.transaction import Transaction
from api.app.core.firestore_proxy import FirestoreProxy
from api.app.domain.entities.player import PlayerGame


def create_player_game_repository():
    firestore = FirestoreProxy[PlayerGame](PlayerGame.parse_obj)
    return PlayerGameRepository(firestore)


class PlayerGameRepository():
    def __init__(self, firestore: FirestoreProxy[PlayerGame]):
        self.firestore = firestore

    @staticmethod
    def path(season: int):
        # return f"season/{season}/player/{player_id}/game"
        return f"season/{season}/player_game"

    # def get(self, season: int, player_id: str, game_id: str, transaction: Transaction = None) -> PlayerGame:
    #     return self.firestore.get(PlayerGameRepository.path(season, player_id), game_id, transaction)

    def get_all(self, season: int, player_id: str, transaction: Transaction = None) -> List[PlayerGame]:
        return self.firestore.get_all(PlayerGameRepository.path(season, player_id), transaction)

    def set(self, season: int, player_game: PlayerGame, transaction: Transaction = None):
        return self.firestore.set(PlayerGameRepository.path(season), player_game, transaction)

    # def where(self, season: int, queries: Union[Query, List[Query]], transaction: Transaction = None) -> List[PlayerGame]:
    #     return self.firestore.where(PlayerGameRepository.path(season, player_id), queries, transaction)

    def where(self, season: int, queries: Union[Query, List[Query]], transaction: Transaction = None) -> List[PlayerGame]:
        return self.firestore.where(PlayerGameRepository.path(season), queries, transaction)
