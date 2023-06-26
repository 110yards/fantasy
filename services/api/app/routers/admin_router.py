
from typing import Optional
from app.config.settings import Settings, get_settings
from app.core.auth import require_role
from app.core.role import Role
from app.domain.services.ownership_report_service import OwnershipReportService, create_ownership_report_service
from app.yards_py.core.sim_state import SimState
from app.domain.commands.admin.reset_week_end import ResetWeekEndCommand, ResetWeekEndCommandExecutor, create_reset_week_end_command_executor
from app.domain.services.league_problems_service import (
    LeagueProblemsService, create_league_problems_service)
from app.routers.api_router import APIRouter
from fastapi.params import Depends
from starlette.requests import Request

router = APIRouter(prefix="/admin")


@router.get("/problems")
@require_role(Role.admin)
async def problems(
    request: Request,
    league_problems_service: LeagueProblemsService = Depends(create_league_problems_service)
):
    return league_problems_service.get_leagues_with_problems()


@router.post("/update_players")
@require_role(Role.admin)
async def update_players(
    request: Request,
    settings: Settings = Depends(get_settings),
):
    raise NotImplementedError("Needs to call system service")
    # command = UpdateActivePlayersCommand()
    # result = command_executor.execute(command)

    # if settings.is_dev():
    #     dev_pubsub_service.process_pubsub_payloads()

    # return result


@router.post("/update_games")
@require_role(Role.admin)
async def update_games(
    request: Request,
    sim_state: Optional[SimState] = None,
    settings: Settings = Depends(get_settings),
):
    # command = UpdateGamesCommand(sim_state=sim_state)
    # result = command_executor.execute(command)

    # if settings.is_dev():
    #     dev_pubsub_service.process_pubsub_payloads()

    # return result
    raise NotImplementedError("Needs to call system service")


@router.post("/end_of_day")
async def end_of_day(
    settings: Settings = Depends(get_settings),
):
    # service.run_workflow()

    # if settings.is_dev():
    #     dev_pubsub_service.process_pubsub_payloads()
    raise NotImplementedError("Needs to call system service")


@router.post("/reset_week_end")
@require_role(Role.admin)
async def reset_week_end(
    request: Request,
    command_executor: ResetWeekEndCommandExecutor = Depends(create_reset_week_end_command_executor),
):
    command = ResetWeekEndCommand()
    return command_executor.execute(command)


@router.post("/schedule")
@require_role(Role.admin)
async def update_schedule(
    request: Request,
):
    # return command_executor.execute(command)
    raise NotImplementedError("Needs to call system service")


@router.get("/report/ownership")
@require_role(Role.admin)
async def get_ownership_report(
    request: Request,
    service: OwnershipReportService = Depends(create_ownership_report_service)
):
    return service.get_ownership_report()
