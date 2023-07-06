from datetime import datetime
from typing import Optional

from fastapi import Depends
from google.cloud.pubsub_v1 import PublisherClient
from google.pubsub_v1.services.publisher.client import PublisherClient as PublisherWrapper
from pydantic.main import BaseModel
from strivelogger import StriveLogger

from ..config.settings import Settings, get_settings
from ..domain.models.virtual_pubsub_payload import VirtualPubSubPayload
from ..domain.store.virtual_pubsub_store import VirtualPubsubStore, create_virtual_pubsub_store


class Publisher:
    def __init__(self, project_id: str):
        self.project_id = project_id

    def publish(self, topic_name: str, payload: Optional[BaseModel] = None):
        pass

    def get_topic_path(self, topic_name):
        return topic_name if "/" in topic_name else f"projects/{self.project_id}/topics/{topic_name}"

    def serialize_payload(self, payload: Optional[BaseModel]):
        if payload:
            serialized = payload.model_dump_json()
            return serialized.encode("utf-8")
        else:
            return None


class PubSubPublisher(Publisher):
    def __init__(self, project_id):
        super().__init__(project_id)

        self.publisher: PublisherWrapper = PublisherClient()

    def publish(self, topic_name: str, payload: Optional[BaseModel] = None):
        topic_path = self.get_topic_path(topic_name)
        data = self.serialize_payload(payload)

        self.publisher.publish(topic_path, data)


class VirtualPubSubPublisher(Publisher):
    def __init__(self, project_id, store: VirtualPubsubStore = None):
        super().__init__(project_id)
        self.store = store

    def publish(self, topic_name: str, payload: Optional[BaseModel] = None):
        topic_path = self.get_topic_path(topic_name)

        if self.store:
            data = payload.model_dump() if payload else None
            entity = VirtualPubSubPayload(topic=topic_name, data=data, timestamp=datetime.now())
            self.store.create(entity)

        StriveLogger.info(f"Published virtual pub/sub message to '{topic_path}")


def create_publisher(
    settings: Settings = Depends(get_settings),
    store: VirtualPubsubStore = Depends(create_virtual_pubsub_store),
):
    project_id = settings.gcloud_project
    return VirtualPubSubPublisher(project_id, store) if settings.is_dev() else PubSubPublisher(project_id)
