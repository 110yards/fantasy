
from starlette.requests import Request
from api.app.core.role import Role
from api.app.domain.services.league_problems_service import LeagueProblemsService, create_league_problems_service
from api.app.core.auth import require_role
from fastapi.params import Depends
from api.app.routers.api_router import APIRouter

router = APIRouter(prefix="/admin")


@router.get("/problems")
@require_role(Role.admin)
async def problems(
    request: Request,
    league_problems_service: LeagueProblemsService = Depends(create_league_problems_service)
):
    return league_problems_service.get_leagues_with_problems()
