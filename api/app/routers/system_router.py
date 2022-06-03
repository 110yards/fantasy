
from fastapi import Depends, Response, status
from api.app.domain.services.smoke_test_service import smoke_test
from .api_router import APIRouter


router = APIRouter(prefix="/system")


@router.post("/configure")
async def configure(
):
    return {}


@router.post("/smoke_test")
async def run_smoke_test(
    response: Response,
    result=Depends(smoke_test),
):
    passes, failures = result

    output = {}

    if passes:
        output["passed"] = passes

    if failures:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        output["failed"] = failures

    return output
