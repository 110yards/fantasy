from app.yards_py.domain.repositories.league_repository import LeagueRepository
from google.cloud.firestore_v1.transaction import Transaction
from typing import Dict, List
from app.yards_py.core.firestore_proxy import FirestoreProxy
from app.yards_py.domain.entities.roster import Roster


def create_league_roster_repository():
    firestore = FirestoreProxy[Roster](Roster.parse_obj)
    return LeagueRosterRepository(firestore)


class LeagueRosterRepository:

    def __init__(self, firestore: FirestoreProxy[Roster]):
        self.firestore = firestore

    @staticmethod
    def path(league_id):
        return f"{LeagueRepository.path}/{league_id}/roster"

    def get_all(self, league_id, transaction: Transaction = None) -> List[Roster]:
        return self.firestore.get_all(LeagueRosterRepository.path(league_id), transaction)

    def set(self, league_id, roster: Roster, transaction: Transaction = None) -> Roster:
        return self.firestore.set(LeagueRosterRepository.path(league_id), roster, transaction)

    def update(self, league_id, roster: Roster, transaction: Transaction = None) -> Roster:
        return self.firestore.update(LeagueRosterRepository.path(league_id), roster, transaction)

    def get(self, league_id, user_id, transaction: Transaction = None) -> Roster:
        return self.firestore.get(LeagueRosterRepository.path(league_id), user_id, transaction)

    def delete(self, league_id, user_id, transaction: Transaction = None):
        self.firestore.delete(LeagueRosterRepository.path(league_id), user_id, transaction)

    def partial_update(self, league_id: str, roster_id: str, updates: Dict, transaction: Transaction = None):
        self.firestore.partial_update(LeagueRosterRepository.path(league_id), roster_id, updates, transaction)
