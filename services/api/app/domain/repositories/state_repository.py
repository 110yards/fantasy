from google.cloud.firestore_v1.transaction import Transaction

from app.core.firestore_proxy import FirestoreProxy
from app.domain.entities.state import State


def create_state_repository():
    proxy = FirestoreProxy(State.parse_obj)
    return StateRepository(proxy)


class StateRepository:
    def __init__(self, firestore: FirestoreProxy):
        self.firestore = firestore

    def get(self, transaction: Transaction = None) -> State:
        return self.firestore.get("public", "state", transaction)

    def set(self, state: State, transaction: Transaction = None) -> State:
        return self.firestore.set("public", state, transaction)
