from fastapi import Depends

from ...core.firestore_client import FirestoreClient, create_firestore_client
from ..models.virtual_pubsub_payload import VirtualPubSubPayload


class VirtualPubsubStore:
    def __init__(self, firestore_client: FirestoreClient):
        self.firestore_client = firestore_client

    def get_all(self) -> list[VirtualPubSubPayload]:
        return self.firestore_client.get("pubsub")

    def delete(self, payload_id: str):
        self.firestore_client.delete(f"pubsub/{payload_id}")

    def create(self, payload: VirtualPubSubPayload) -> VirtualPubSubPayload:
        return self.firestore_client.set(f"pubsub/{payload.message_id}", payload.model_dump())


def create_virtual_pubsub_store(firestore_client: FirestoreClient = Depends(create_firestore_client)) -> VirtualPubsubStore:
    return VirtualPubsubStore(firestore_client=firestore_client)
