from fastapi import Depends

from ...core.firestore_client import FirestoreClient, create_firestore_client
from ..models.state import State


class StateStore:
    def __init__(self, firestore_client: FirestoreClient):
        self.firestore_client = firestore_client

    def get_state(self) -> State:
        path = "public/state"
        data = self.firestore_client.get(path)
        return State(**data)


def create_state_store(firestore_client: FirestoreClient = Depends(create_firestore_client)) -> StateStore:
    return StateStore(
        firestore_client=firestore_client,
    )
