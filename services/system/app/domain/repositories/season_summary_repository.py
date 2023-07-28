from typing import List

from app.core.firestore_proxy import FirestoreProxy
from app.domain.entities.season_summary import SeasonSummary
from google.cloud.firestore_v1.transaction import Transaction


def create_season_summary_repository():
    firestore = FirestoreProxy[SeasonSummary](SeasonSummary.parse_obj)
    return SeasonSummaryRepository(firestore)


class SeasonSummaryRepository:
    def __init__(self, firestore: FirestoreProxy):
        self.firestore = firestore

    @staticmethod
    def path(league_id: str):
        return f"league/{league_id}/seasons"

    def get(self, league_id: str, year: int, transaction: Transaction = None) -> SeasonSummary:
        return self.firestore.get(SeasonSummaryRepository.path(league_id), year, transaction)

    def set(self, league_id: str, season_summary: SeasonSummary, transaction: Transaction = None) -> SeasonSummary:
        return self.firestore.set(SeasonSummaryRepository.path(league_id), season_summary, transaction)

    def get_all(self, league_id: str, transaction: Transaction = None) -> List[SeasonSummary]:
        return self.firestore.get_all(SeasonSummaryRepository.path(league_id), transaction)
