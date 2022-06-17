
from fastapi import Depends
from services.system.app.domain.services.dev_pubsub_service import DevPubSubService, create_dev_pubsub_service
from .api_router import APIRouter

router = APIRouter(prefix="/dev")


@router.post("/pubsub")
async def pubsub(
    service: DevPubSubService = Depends(create_dev_pubsub_service),
):
    return service.process_pubsub_payloads()
