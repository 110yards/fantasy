

from typing import List
from google.cloud.firestore_v1.transaction import Transaction
from app.yards_py.core.firestore_proxy import FirestoreProxy
from app.yards_py.domain.entities.player_season import PlayerSeason


def create_player_season_repository():
    firestore = FirestoreProxy[PlayerSeason](PlayerSeason.parse_obj)
    return PlayerSeasonRepository(firestore)


class PlayerSeasonRepository():
    def __init__(self, firestore: FirestoreProxy[PlayerSeason]):
        self.firestore = firestore

    @staticmethod
    def path(season: int):
        return f"season/{season}/player_season"

    def set(self, season, player_season: PlayerSeason, transaction: Transaction = None):
        return self.firestore.set(PlayerSeasonRepository.path(season), player_season, transaction)

    def get(self, season, player_id: str, transaction: Transaction = None) -> PlayerSeason:
        return self.firestore.get(PlayerSeasonRepository.path(season), player_id, transaction)

    def get_all(self, season: int, transaction: Transaction = None) -> List[PlayerSeason]:
        return self.firestore.get_all(PlayerSeasonRepository.path(season), transaction)

    def set_all(self, season: int, player_seasons: List[PlayerSeason]):
        return self.firestore.set_all(PlayerSeasonRepository.path(season), player_seasons)
