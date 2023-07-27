import base64
import json
from datetime import datetime
from typing import Dict, Optional

from google.api_core.exceptions import NotFound
from google.cloud.pubsub_v1 import PublisherClient, SubscriberClient
from google.protobuf.duration_pb2 import Duration
from google.pubsub_v1.services.publisher.client import PublisherClient as PublisherWrapper
from google.pubsub_v1.services.subscriber import SubscriberClient as SubscriberWrapper
from google.pubsub_v1.types.pubsub import ExpirationPolicy, PushConfig, RetryPolicy, Subscription
from pydantic.main import BaseModel

from app.domain.repositories.virtual_pubsub_repository import VirtualPubSubPayload, VirtualPubsubRepository
from app.yards_py.core.annotate_args import annotate_args
from app.yards_py.core.exceptions import InvalidPushException
from app.yards_py.core.logging import Logger


@annotate_args
class SubscriptionConfig(BaseModel):
    expiration_days: Optional[int] = 31
    retention_days: int = 7
    ack_deadline: int = 60


class Publisher:
    def __init__(self, project_id: str):
        self.project_id = project_id

    def publish(self, payload: BaseModel, topic_name: str):
        pass

    def create_topic(self, topic_name: str):
        pass

    def create_push_subscription(self, subscription_name: str, topic_name: str, endpoint: str, config: SubscriptionConfig = None) -> Subscription:
        pass

    def get_topic_path(self, topic_name):
        return topic_name if "/" in topic_name else f"projects/{self.project_id}/topics/{topic_name}"

    def serialize_payload(self, payload: Optional[BaseModel]):
        if payload:
            serialized = payload.json()
            return serialized.encode("utf-8")
        else:
            return None


class PubSubPublisher(Publisher):
    def __init__(self, project_id):
        super().__init__(project_id)

        self.publisher: PublisherWrapper = PublisherClient()

    def publish(self, payload: BaseModel, topic_name: str):
        topic_path = self.get_topic_path(topic_name)
        data = self.serialize_payload(payload)

        self.publisher.publish(topic_path, data)

    def create_topic(self, topic_name: str):
        topic_path = self.get_topic_path(topic_name)
        try:
            try:
                self.publisher.get_topic(topic=topic_path)
                Logger.info("Topic exists", extra={"topic_name": topic_name})
            except NotFound:
                self.publisher.create_topic(name=topic_path)
                Logger.info("Topic created", extra={"topic_name": topic_name})
        except BaseException as ex:
            Logger.error("Failed to create topic", extra={"topic_name": topic_name}, exc_info=ex)
            raise ex

    def create_push_subscription(self, subscription_name: str, topic_name: str, endpoint: str, config: SubscriptionConfig = None) -> Subscription:
        subscriber: SubscriberWrapper = SubscriberClient()
        subcription_path = subscriber.subscription_path(self.project_id, subscription_name)
        topic_path = self.get_topic_path(topic_name)

        if not config:
            config = SubscriptionConfig()

        logging_extra = {
            "subscription_name": subscription_name,
            "topic_name": topic_name,
            "config": config.dict(),
        }

        with subscriber:
            try:
                try:
                    subscription = subscriber.get_subscription(request={"subscription": subcription_path})
                    Logger.info("Push subscription exists", logging_extra)
                    return subscription
                except NotFound:
                    request = Subscription(
                        name=subcription_path,
                        topic=topic_path,
                        push_config=PushConfig(push_endpoint=endpoint),
                        ack_deadline_seconds=config.ack_deadline,
                        expiration_policy=ExpirationPolicy(ttl=Duration(seconds=config.expiration_days * 86400) if config.expiration_days else None),
                        retry_policy=RetryPolicy(),
                        message_retention_duration=Duration(seconds=config.retention_days * 86400),
                    )
                    subscription = subscriber.create_subscription(request=request)
                    Logger.info("Push subscription created", logging_extra)
                    return subscription

            except BaseException as ex:
                Logger.error("Failed to create push subscription", exc_info=ex, extra=logging_extra)
                raise ex


class VirtualPubSubPublisher(Publisher):
    def __init__(self, project_id, repo: VirtualPubsubRepository = None):
        super().__init__(project_id)
        self.repo = repo

    def publish(self, payload: BaseModel, topic_name: str):
        topic_path = self.get_topic_path(topic_name)

        if self.repo:
            entity = VirtualPubSubPayload(topic=topic_name, data=payload.dict(), timestamp=datetime.now())
            self.repo.create(entity)

        Logger.info(f"Published virtual pub/sub message to '{topic_path}")

    def create_topic(self, topic_name: str):
        # PubSubPublisher(self.project_id).create_topic(topic_name)
        Logger.info(f"Created virtual topic '{topic_name}'")

    def create_push_subscription(self, subscription_name: str, topic_name: str, endpoint: str, config: SubscriptionConfig = None):
        # return PubSubPublisher(self.project_id).create_push_subscription(subscription_name, topic_name, endpoint, config)
        Logger.info(f"Created virtual push subscription '{subscription_name}' on topic '{topic_name}' to {endpoint}")
        return Subscription(name=subscription_name)


def get_message_data(push: Dict) -> Dict:
    Logger.info(f"[PUB/SUB] {push}")

    if not push:
        raise InvalidPushException()

    message = push["message"]
    if not message:
        raise InvalidPushException()

    data = message["data"]
    if not data:
        raise InvalidPushException()

    try:
        payload = base64.b64decode(data)
        return json.loads(payload)
    except Exception:
        return data
