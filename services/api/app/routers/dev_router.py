from .api_router import APIRouter

router = APIRouter(prefix="/dev")


@router.post("/pubsub")
async def pubsub(
    # service: DevPubSubService = Depends(create_dev_pubsub_service),
):
    raise NotImplementedError("Needs to call system service")
    # return service.process_pubsub_payloads()
