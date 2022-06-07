from typing import Dict, List, Union
from yards_py.core.firestore_proxy import FirestoreProxy, Query
from google.cloud.firestore_v1.transaction import Transaction
from yards_py.domain.entities.league import League


def create_league_repository():
    firestore = FirestoreProxy[League](League.parse_obj)
    return LeagueRepository(firestore)


class LeagueRepository:
    path = "league"

    def __init__(self, firestore: FirestoreProxy[League]):
        self.firestore = firestore

    def create(self, league, transaction: Transaction = None) -> League:
        return self.firestore.create(self.path, league, transaction)

    def get(self, league_id, transaction: Transaction = None) -> League:
        return self.firestore.get(self.path, league_id, transaction)

    def get_all(self, transaction: Transaction = None) -> List[League]:
        return self.firestore.get_all(self.path, transaction)

    def update(self, league, transaction: Transaction = None) -> League:
        return self.firestore.update(self.path, league, transaction)

    def where(self, queries: Union[List[Query], Query], transaction=None) -> List[League]:
        return self.firestore.where(self.path, queries, transaction)

    def partial_update(self, league_id: str, updates: Dict, transaction: Transaction = None) -> League:
        return self.firestore.partial_update(self.path, league_id, updates, transaction)
