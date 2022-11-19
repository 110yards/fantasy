from pathlib import Path
from google.api_core.exceptions import NotFound
from pydantic import BaseSettings

from google.cloud.pubsub_v1 import PublisherClient
from google.pubsub_v1.services.publisher.client import PublisherClient as PublisherWrapper


class Settings(BaseSettings):
    gcloud_project: str

    class Config:
        env_file = ".env"


settings = Settings()
publisher: PublisherWrapper = PublisherClient()


def get_topic_path(topic_name):
    return topic_name if "/" in topic_name else f"projects/{settings.gcloud_project}/topics/{topic_name}"


def create_topic(topic_name: str):
    topic_path = get_topic_path(topic_name)
    try:
        try:
            publisher.get_topic(topic=topic_path)
            print(f"Topic already exists: {topic_name}")
        except NotFound:
            publisher.create_topic(name=topic_path)
            print(f"Topic created: {topic_name}")
    except BaseException as ex:
        print(f"Failed to create topic: {topic_name}")
        raise ex


def create_topics():
    path = Path("topics")
    topics = path.read_text().splitlines()
    topics = set(t.strip() for t in topics)

    for topic in topics:
        create_topic(topic)


if __name__ == "__main__":
    create_topics()
