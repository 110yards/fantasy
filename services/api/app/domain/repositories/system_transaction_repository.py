from google.cloud.firestore_v1.transaction import Transaction

from app.core.firestore_proxy import FirestoreProxy
from app.domain.entities.league_transaction import LeagueTransaction

from ...yards_py.domain.entities.system_transaction import SystemTransaction


class SystemTransactionRepository:
    def __init__(self, firestore: FirestoreProxy[LeagueTransaction]):
        self.firestore = firestore

    @staticmethod
    def path():
        return "system_transactions"

    def create(self, system_transaction: SystemTransaction, transaction: Transaction = None) -> SystemTransaction:
        return self.firestore.create(SystemTransactionRepository.path(), system_transaction, transaction)


def create_system_transaction_repository():
    firestore = FirestoreProxy[LeagueTransaction](LeagueTransaction.parse_obj)
    return SystemTransactionRepository(firestore)
