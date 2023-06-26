

from fastapi import Depends
from app.config.settings import Settings, get_settings
from app.yards_py.core.publisher import PubSubPublisher, VirtualPubSubPublisher
from app.yards_py.domain.repositories.virtual_pubsub_repository import (
    VirtualPubsubRepository, create_virtual_pubsub_repository)

# DI for dependencies should be next to the class it is creating, unless the class is in a different package.


def create_publisher(
    settings: Settings = Depends(get_settings),
    virtual_pubsub_repo: VirtualPubsubRepository = Depends(create_virtual_pubsub_repository),
):
    project_id = settings.gcloud_project
    return VirtualPubSubPublisher(project_id, virtual_pubsub_repo) if settings.is_dev() else PubSubPublisher(project_id)
