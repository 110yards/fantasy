from yards_py.domain.entities.owned_player import OwnedPlayer
from yards_py.domain.repositories.league_repository import LeagueRepository
from google.cloud.firestore_v1.transaction import Transaction
from typing import List
from yards_py.core.firestore_proxy import FirestoreProxy


def create_league_owned_player_repository():
    firestore = FirestoreProxy[OwnedPlayer](OwnedPlayer.parse_obj)
    return LeagueOwnedPlayerRepository(firestore)


class LeagueOwnedPlayerRepository:

    def __init__(self, firestore: FirestoreProxy[OwnedPlayer]):
        self.firestore = firestore

    @staticmethod
    def path(league_id):
        return f"{LeagueRepository.path}/{league_id}/owned_player"

    def get_all(self, league_id, transaction: Transaction = None) -> List[OwnedPlayer]:
        return self.firestore.get_all(LeagueOwnedPlayerRepository.path(league_id), transaction)

    def set(self, league_id, owned_player: OwnedPlayer, transaction: Transaction = None):
        return self.firestore.set(LeagueOwnedPlayerRepository.path(league_id), owned_player, transaction)

    def get(self, league_id, player_id, transaction: Transaction = None):
        return self.firestore.get(LeagueOwnedPlayerRepository.path(league_id), player_id, transaction)

    def delete(self, league_id, player_id, transaction: Transaction = None):
        self.firestore.delete(LeagueOwnedPlayerRepository.path(league_id), player_id, transaction)

    def delete_all(self, league_id):
        self.firestore.delete_all(LeagueOwnedPlayerRepository.path(league_id))
