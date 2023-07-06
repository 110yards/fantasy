from fastapi import Depends
from google.cloud.firestore_v1.transaction import Transaction

from ...core.firestore_client import FirestoreClient, create_firestore_client
from ..models.state import State
from ..models.virtual_pubsub_payload import VirtualPubSubPayload


class StateStore:
    def __init__(self, firestore_client: FirestoreClient):
        self.firestore_client = firestore_client

    def get(self, transaction: Transaction = None) -> State:
        return self.firestore_client.get("public/state", transaction)

    def set(self, state: State, transaction: Transaction) -> VirtualPubSubPayload:
        return self.firestore_client.set("public/state", state.model_dump(), transaction)


def create_state_store(firestore_client: FirestoreClient = Depends(create_firestore_client)) -> StateStore:
    return StateStore(firestore_client=firestore_client)
