from fastapi import Depends

from app.config.settings import Settings, get_settings
from app.domain.repositories.virtual_pubsub_repository import VirtualPubsubRepository, create_virtual_pubsub_repository
from app.core.publisher import PubSubPublisher, VirtualPubSubPublisher


def create_publisher(
    settings: Settings = Depends(get_settings),
    virtual_pubsub_repo: VirtualPubsubRepository = Depends(create_virtual_pubsub_repository),
):
    project_id = settings.gcloud_project
    return VirtualPubSubPublisher(project_id, virtual_pubsub_repo) if settings.is_dev() else PubSubPublisher(project_id)
