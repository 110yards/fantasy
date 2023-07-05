from typing import Any, Dict, Optional

from google.cloud.firestore_v1 import Client, Query
from google.cloud.firestore_v1.base_query import BaseCompositeFilter, FieldFilter
from google.cloud.firestore_v1.transaction import Transaction

from ..config.settings import Settings


class FirestoreClient:
    def __init__(self, project_id: str):
        self.client = Client(project=project_id)

    def create_transaction(self) -> Transaction:
        return self.client.transaction()

    def query(self, path, field: str, operator: str, value: Any) -> Query:
        filter = BaseCompositeFilter("AND", filters=[FieldFilter(field, operator, value)])
        return self.client.collection(path).where(filter=filter)

    def get_query(self, query: Query) -> list[dict[str, Any]]:
        return [doc.to_dict() for doc in query.get()]

    def get(self, path: str, transaction: Optional[Transaction] = None) -> Optional[tuple | Any]:
        path_parts = len(path.split("/"))

        is_doc = path_parts % 2 == 0

        if is_doc:
            ref = self.client.document(path)
            if transaction is not None:
                snapshot = transaction.get(ref)
            else:
                snapshot = ref.get()
            return snapshot.to_dict()
        else:
            ref = self.client.collection(path)
            if transaction is not None:
                snapshots = transaction.get(ref)
            else:
                snapshots = ref.get()
            return [snapshot.to_dict() for snapshot in snapshots]

    def set(self, path: str, data: Dict, transaction: Optional[Transaction] = None):
        ref = self.client.document(path)

        if transaction is not None:
            transaction.set(ref, data)
        else:
            ref.set(data)


def create_firestore_client(settings: Settings) -> FirestoreClient:
    return FirestoreClient(project_id=settings.gcloud_project)
