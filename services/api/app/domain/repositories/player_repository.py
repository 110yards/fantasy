

from typing import List, Union
from fastapi.param_functions import Query
from google.cloud.firestore_v1.transaction import Transaction
from yards_py.core.firestore_proxy import FirestoreProxy
from yards_py.domain.entities.player import Player


def create_player_repository():
    firestore = FirestoreProxy[Player](Player.parse_obj)
    return PlayerRepository(firestore)


class PlayerRepository():
    def __init__(self, firestore: FirestoreProxy[Player]):
        self.firestore = firestore

    @staticmethod
    def path(season: int):
        return f"season/{season}/player"

    def get(self, season, player_id, transaction: Transaction = None) -> Player:
        return self.firestore.get(PlayerRepository.path(season), player_id, transaction)

    def get_all(self, season, transaction: Transaction = None) -> List[Player]:
        return self.firestore.get_all(PlayerRepository.path(season), transaction)

    def set(self, season, player: Player, transaction: Transaction = None):
        return self.firestore.set(PlayerRepository.path(season), player, transaction)

    def set_all(self, season: int, players: List[Player]):
        self.firestore.set_all(PlayerRepository.path(season), players)

    def where(self, season, queries: Union[Query, List[Query]], transaction: Transaction = None) -> List[Player]:
        return self.firestore.where(PlayerRepository.path(season), queries, transaction)
