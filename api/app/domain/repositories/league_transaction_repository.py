from typing import List
from google.cloud.firestore_v1.transaction import Transaction
from api.app.domain.entities.league_transaction import LeagueTransaction
from api.app.core.firestore_proxy import FirestoreProxy


def create_league_transaction_repository():
    firestore = FirestoreProxy[LeagueTransaction](LeagueTransaction.parse_obj)
    return LeagueTransactionRepository(firestore)


class LeagueTransactionRepository:

    def __init__(self, firestore: FirestoreProxy[LeagueTransaction]):
        self.firestore = firestore

    @staticmethod
    def path(league_id):
        return f"league/{league_id}/transaction"

    def create(self, league_id: str, league_transaction: LeagueTransaction, transaction: Transaction = None) -> LeagueTransaction:
        return self.firestore.create(LeagueTransactionRepository.path(league_id), league_transaction, transaction)

    def get_all(self, league_id: str, transaction: Transaction = None) -> List[LeagueTransaction]:
        return self.firestore.get_all(LeagueTransactionRepository.path(league_id), transaction)

    def delete(self, league_id: str, transaction_id: str, transaction: Transaction = None):
        return self.firestore.delete(LeagueTransactionRepository.path(league_id), transaction_id, transaction)

    def delete_all(self, league_id: str):
        return self.firestore.delete_all(LeagueTransactionRepository.path(league_id))
