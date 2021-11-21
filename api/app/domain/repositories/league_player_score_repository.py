from typing import List, Union
from api.app.domain.entities.league_player_score import LeaguePlayerScore
from api.app.domain.repositories.league_repository import LeagueRepository
from google.cloud.firestore_v1.transaction import Transaction
from api.app.core.firestore_proxy import FirestoreProxy, Query


def create_league_player_score_repository():
    firestore = FirestoreProxy[LeaguePlayerScore](LeaguePlayerScore.parse_obj)
    return LeaguePlayerScoreRepository(firestore)


class LeaguePlayerScoreRepository:

    def __init__(self, firestore: FirestoreProxy[LeaguePlayerScore]):
        self.firestore = firestore

    @staticmethod
    def path(league_id):
        return f"{LeagueRepository.path}/{league_id}/player_score"

    def set(self, league_id, player_score: LeaguePlayerScore, transaction: Transaction = None):
        return self.firestore.set(LeaguePlayerScoreRepository.path(league_id), player_score, transaction)

    def get(self, league_id, player_id, transaction: Transaction = None) -> LeaguePlayerScore:
        return self.firestore.get(LeaguePlayerScoreRepository.path(league_id), player_id, transaction)

    def get_all(self, league_id, transaction: Transaction = None) -> List[LeaguePlayerScore]:
        return self.firestore.get_all(LeaguePlayerScoreRepository.path(league_id), transaction)

    def where(self, league_id, queries: Union[List[Query], Query], transaction: Transaction = None) -> List[LeaguePlayerScore]:
        return self.firestore.where(LeaguePlayerScoreRepository.path(league_id), queries, transaction)
