from typing import List

from google.cloud.firestore_v1.transaction import Transaction

from app.core.firestore_proxy import FirestoreProxy
from app.domain.entities.league_week import LeagueWeek
from app.domain.repositories.league_repository import LeagueRepository


def create_league_week_repository():
    firestore = FirestoreProxy[LeagueWeek](LeagueWeek.parse_obj)
    return LeagueWeekRepository(firestore)


class LeagueWeekRepository:
    def __init__(self, firestore: FirestoreProxy[LeagueWeek]):
        self.firestore = firestore

    @staticmethod
    def path(league_id):
        return f"{LeagueRepository.path}/{league_id}/week"

    def get_all(self, league_id: str, transaction: Transaction = None) -> List[LeagueWeek]:
        return self.firestore.get_all(LeagueWeekRepository.path(league_id), transaction)

    def get(self, league_id, week_id: str, transaction: Transaction = None) -> LeagueWeek:
        return self.firestore.get(LeagueWeekRepository.path(league_id), week_id, transaction)

    def set(self, league_id, week: LeagueWeek, transaction: Transaction = None) -> LeagueWeek:
        return self.firestore.set(LeagueWeekRepository.path(league_id), week, transaction)

    def delete(self, league_id: str, week_id: str, transaction: Transaction = None):
        return self.firestore.delete(LeagueWeekRepository.path(league_id), week_id, transaction)

    def delete_all(self, league_id: str):
        return self.firestore.delete_all(LeagueWeekRepository.path(league_id))
