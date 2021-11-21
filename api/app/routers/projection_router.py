from api.app.domain.services.player_projection_service import PlayerProjectionService, create_player_projection_service
from fastapi import Depends
from .api_router import APIRouter

router = APIRouter(prefix="/projection/league/{league_id}")


@router.get("/player/{player_id}")
async def player(
    league_id: str,
    player_id: str,
    service: PlayerProjectionService = Depends(create_player_projection_service)
):
    return service.get_projection(league_id, player_id)
