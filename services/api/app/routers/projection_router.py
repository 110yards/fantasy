from app.domain.services.player_projection_service import PlayerProjectionService, create_player_projection_service
from fastapi import Depends

from app.domain.services.roster_projection_service import RosterProjectionService, create_roster_projection_service
from .api_router import APIRouter

router = APIRouter(prefix="/projection/league/{league_id}")


@router.get("/player/{player_id}")
async def player(league_id: str, player_id: str, service: PlayerProjectionService = Depends(create_player_projection_service)):
    return service.get_projection(league_id, player_id)


@router.get("/roster/{roster_id}")
async def roster(
    league_id: str,
    roster_id: str,
    service: RosterProjectionService = Depends(create_roster_projection_service),
):
    return service.get_projection(league_id, roster_id)
