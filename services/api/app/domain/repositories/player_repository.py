from datetime import datetime, timezone
from typing import List, Union

from google.cloud.firestore_v1.transaction import Transaction

from app.yards_py.core.firestore_proxy import FirestoreProxy, Query
from app.yards_py.domain.entities.player import Player


def create_player_repository():
    firestore = FirestoreProxy[Player](Player.parse_obj)
    return PlayerRepository(firestore)


class PlayerRepository:
    def __init__(self, firestore: FirestoreProxy[Player]):
        self.firestore = firestore

    @staticmethod
    def path():
        return "players"

    def get(self, player_id, transaction: Transaction = None) -> Player:
        return self.firestore.get(PlayerRepository.path(), player_id, transaction)

    def get_all(self, season: int, transaction: Transaction = None) -> List[Player]:
        query = Query("seasons", "array_contains", season)
        return self.firestore.where(PlayerRepository.path(), query, transaction)

    # def set(self, player: Player, transaction: Transaction = None):
    #     return self.firestore.set(PlayerRepository.path(season), player, transaction)

    # def set_all(self, players: List[Player]):
    #     self.firestore.set_all(PlayerRepository.path(season), players)

    def where(self, season, queries: Union[Query, List[Query]], transaction: Transaction = None) -> List[Player]:
        return self.firestore.where(PlayerRepository.path(season), queries, transaction)

    def get_last_updated(self) -> datetime:
        path = PlayerRepository.path()
        ref = self.firestore.client.collection(path).order_by("last_updated", direction="DESCENDING").limit(1)
        player = ref.get()

        if not player:
            return datetime.min.replace(tzinfo=timezone.utc)

        return player[0].to_dict()["last_updated"]
