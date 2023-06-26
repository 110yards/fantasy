from datetime import datetime
from typing import List
from app.yards_py.core.base_entity import BaseEntity
from app.yards_py.core.firestore_proxy import FirestoreProxy


class VirtualPubSubPayload(BaseEntity):
    topic: str
    data: dict
    timestamp: datetime


def create_virtual_pubsub_repository():
    firestore = FirestoreProxy[VirtualPubSubPayload](VirtualPubSubPayload.parse_obj)
    return VirtualPubsubRepository(firestore)


class VirtualPubsubRepository:
    path = "pubsub"

    def __init__(self, firestore: FirestoreProxy[VirtualPubSubPayload]):
        self.firestore = firestore

    def get_all(self) -> List[VirtualPubSubPayload]:
        return self.firestore.get_all(self.path)

    def delete(self, payload_id: str):
        self.firestore.delete(self.path, payload_id)

    def create(self, payload: VirtualPubSubPayload) -> VirtualPubSubPayload:
        return self.firestore.create(self.path, payload)
