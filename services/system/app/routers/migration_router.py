

from services.system.app.domain.migrations.recreate_league_cmd_sub import LeagueCommandSubMigration, create_league_cmd_sub_migration
from typing import Optional
from starlette.requests import Request
from fastapi.params import Depends
from .api_router import APIRouter

router = APIRouter(prefix="/migration")


@router.post("/recreate_league_cmd_sub")
async def recreate_league_cmd_sub(
    request: Request,
    league_id: Optional[str] = None,
    migration: LeagueCommandSubMigration = Depends(create_league_cmd_sub_migration),
):
    return migration.run(league_id)
