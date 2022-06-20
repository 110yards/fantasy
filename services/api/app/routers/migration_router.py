

from services.api.app.domain.migrations.issue_102_migration import Issue102Migration, create_issue_102_migration
from services.api.app.domain.migrations.issue_121_migration import Issue121Migration, create_issue_121_migration
from services.api.app.domain.migrations.issue_84_migration import Issue84Migration, create_issue_84_migration
from services.api.app.domain.migrations.issue_82_migration import Issue82Migration, create_issue_82_migration
from services.api.app.domain.migrations.issue_58_migration import Issue58Migration, create_issue_58_migration
from services.api.app.domain.migrations.league_command_sub_migration import LeagueCommandSubMigration, create_league_command_sub_migration
from typing import Optional
from services.api.app.domain.migrations.issue_46_migration import Issue46Migration, create_issue_46_migration
from starlette.requests import Request
from services.api.app.core.role import Role
from services.api.app.core.auth import require_role
from fastapi.params import Depends
from services.api.app.routers.api_router import APIRouter

router = APIRouter(prefix="/migration")


@router.post("/issue-46")
@require_role(Role.admin)
async def issue_46(
    request: Request,
    issue_46_migration: Issue46Migration = Depends(create_issue_46_migration)
):
    return issue_46_migration.run()


@router.post("/league_commands_sub")
@require_role(Role.admin)
async def create_league_commands_sub_migration(
    request: Request,
    league_id: Optional[str] = None,
    migration: LeagueCommandSubMigration = Depends(create_league_command_sub_migration),
):
    return migration.run(league_id)


@router.post("/league_previews")
@require_role(Role.admin)
async def league_previews_migration(
    request: Request,
    league_id: Optional[str] = None,
    migration: Issue58Migration = Depends(create_issue_58_migration),
):
    return migration.run(league_id)


@router.post("/clear_roster_scores")
@require_role(Role.admin)
async def clear_roster_scores(
    request: Request,
    league_id: Optional[str] = None,
    migration: Issue82Migration = Depends(create_issue_82_migration),
):
    return migration.run(league_id)


@router.post("/issue_84")
@require_role(Role.admin)
async def issue_84(
    request: Request,
    league_id: Optional[str] = None,
    migration: Issue84Migration = Depends(create_issue_84_migration),
):
    return migration.run(league_id)


@router.post("/issue_102")
@require_role(Role.admin)
async def issue_102(
    request: Request,
    league_id: Optional[str] = None,
    migration: Issue102Migration = Depends(create_issue_102_migration),
):
    return migration.run(league_id)


@router.post("/issue_121")
@require_role(Role.admin)
async def issue_121(
    request: Request,
    commit: bool = False,
    migration: Issue121Migration = Depends(create_issue_121_migration),
):
    return migration.run(commit)
