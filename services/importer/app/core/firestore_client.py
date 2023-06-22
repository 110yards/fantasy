from typing import Any, Dict, Optional

from firebase_admin import firestore
from google.cloud.firestore_v1 import Client
from google.cloud.firestore_v1.transaction import Transaction


class FirestoreClient:
    def __init__(self):
        self.client: Client = firestore.client()

    def create_transaction(self) -> Transaction:
        return self.client.transaction()

    def get(self, transaction: Transaction, path: str) -> Optional[tuple | Any]:
        path_parts = len(path.split("/"))

        is_doc = path_parts % 2 == 0

        if is_doc:
            ref = self.client.document(path)
            snapshot = transaction.get(ref)
            return snapshot.to_dict()
        else:
            raise NotImplementedError()
            # ref = self.client.collection(path)
            # snapshots = transaction.
            # return [snapshot.to_dict() for snapshot in snapshots]

    def set(self, transaction: Transaction, path: str, data: Dict):
        ref = self.client.document(path)
        transaction.set(ref, data)


def create_firestore_client() -> FirestoreClient:
    return FirestoreClient()
