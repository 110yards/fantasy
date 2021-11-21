
from api.app.domain.services.score_service import RosterScoreService, create_roster_score_service
from fastapi import Depends
from .api_router import APIRouter

router = APIRouter(prefix="/score/league/{league_id}")


@router.get("/roster/{roster_id}")
async def roster(
    league_id: str,
    roster_id: str,
    service: RosterScoreService = Depends(create_roster_score_service),
):
    return service.get_score(league_id, roster_id)
