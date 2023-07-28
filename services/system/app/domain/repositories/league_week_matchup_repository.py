from typing import Dict, List

from app.core.firestore_proxy import FirestoreProxy
from app.domain.entities.schedule import Matchup
from app.domain.repositories.league_repository import LeagueRepository
from google.cloud.firestore_v1.transaction import Transaction


def create_league_week_matchup_repository():
    firestore = FirestoreProxy[Matchup](Matchup.parse_obj)
    return LeagueWeekMatchupRepository(firestore)


class LeagueWeekMatchupRepository:
    def __init__(self, firestore: FirestoreProxy[Matchup]):
        self.firestore = firestore

    @staticmethod
    def path(league_id, week_number):
        return f"{LeagueRepository.path}/{league_id}/week/{week_number}/matchup"

    def create(self, league_id, week_number, matchup, transaction: Transaction = None) -> Matchup:
        return self.firestore.create(LeagueWeekMatchupRepository.path(league_id, week_number), matchup, transaction)

    def set(self, league_id, week_number, matchup, transaction: Transaction = None) -> Matchup:
        return self.firestore.set(LeagueWeekMatchupRepository.path(league_id, week_number), matchup, transaction)

    def partial_update(self, league_id, week_number, matchup_id, updates: Dict, transaction=None):
        self.firestore.partial_update(LeagueWeekMatchupRepository.path(league_id, week_number), matchup_id, updates, transaction)

    def get(self, league_id, week_number: int, matchup_id, transaction: Transaction = None) -> Matchup:
        return self.firestore.get(LeagueWeekMatchupRepository.path(league_id, week_number), matchup_id, transaction)

    def get_all(self, league_id, week_number: int, transaction: Transaction = None) -> List[Matchup]:
        return self.firestore.get_all(LeagueWeekMatchupRepository.path(league_id, week_number), transaction)

    def delete(self, league_id, week_number: int, matchup_id, transaction: Transaction = None):
        return self.firestore.delete(LeagueWeekMatchupRepository.path(league_id, week_number), matchup_id, transaction)

    def delete_all(self, league_id):
        longest_season = 22
        for i in range(1, longest_season + 1):
            self.firestore.delete_all(LeagueWeekMatchupRepository.path(league_id, i))
