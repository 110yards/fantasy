from typing import List, Union

from app.core.firestore_proxy import FirestoreProxy, Query
from app.domain.entities.player_league_season_score import PlayerLeagueSeasonScore
from app.domain.repositories.league_repository import LeagueRepository
from google.cloud.firestore_v1.transaction import Transaction


def create_player_league_season_score_repository():
    firestore = FirestoreProxy[PlayerLeagueSeasonScore](PlayerLeagueSeasonScore.parse_obj)
    return PlayerLeagueSeasonScoreRepository(firestore)


class PlayerLeagueSeasonScoreRepository:
    def __init__(self, firestore: FirestoreProxy[PlayerLeagueSeasonScore]):
        self.firestore = firestore

    @staticmethod
    def path(league_id):
        return f"{LeagueRepository.path}/{league_id}/player_score"

    def set(self, league_id, player_score: PlayerLeagueSeasonScore, transaction: Transaction = None):
        return self.firestore.set(PlayerLeagueSeasonScoreRepository.path(league_id), player_score, transaction)

    def get(self, league_id, player_id, transaction: Transaction = None) -> PlayerLeagueSeasonScore:
        return self.firestore.get(PlayerLeagueSeasonScoreRepository.path(league_id), player_id, transaction)

    def get_all(self, league_id, transaction: Transaction = None) -> List[PlayerLeagueSeasonScore]:
        return self.firestore.get_all(PlayerLeagueSeasonScoreRepository.path(league_id), transaction)

    def where(self, league_id, queries: Union[List[Query], Query], transaction: Transaction = None) -> List[PlayerLeagueSeasonScore]:
        return self.firestore.where(PlayerLeagueSeasonScoreRepository.path(league_id), queries, transaction)

    def delete(self, league_id: str, player_id: str, transaction: Transaction = None):
        return self.firestore.delete(PlayerLeagueSeasonScoreRepository.path(league_id), player_id, transaction)

    def delete_all(self, league_id: str):
        self.firestore.delete_all(PlayerLeagueSeasonScoreRepository.path(league_id))
