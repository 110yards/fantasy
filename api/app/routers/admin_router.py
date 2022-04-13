
from typing import Optional
from api.app.config.settings import Settings, get_settings
from api.app.core.auth import require_role
from api.app.core.role import Role
from api.app.core.sim_state import SimState
from api.app.domain.commands.admin.reset_week_end import ResetWeekEndCommand, ResetWeekEndCommandExecutor, create_reset_week_end_command_executor
from api.app.domain.commands.system.update_active_players import (
    UpdateActivePlayersCommand, UpdateActivePlayersCommandExecutor,
    update_active_players_command_executor)
from api.app.domain.commands.system.update_games import UpdateGamesCommand, UpdateGamesCommandExecutor, create_update_games_command_executor
from api.app.domain.commands.system.update_schedule import UpdateScheduleCommand, UpdateScheduleCommandExecutor, create_update_schedule_command_executor
from api.app.domain.services.dev_pubsub_service import DevPubSubService, create_dev_pubsub_service
from api.app.domain.services.end_of_day_service import EndOfDayService, create_end_of_day_service
from api.app.domain.services.league_problems_service import (
    LeagueProblemsService, create_league_problems_service)
from api.app.routers.api_router import APIRouter
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
    command_executor: UpdateActivePlayersCommandExecutor = Depends(update_active_players_command_executor),
    settings: Settings = Depends(get_settings),
    dev_pubsub_service: DevPubSubService = Depends(create_dev_pubsub_service),
):
    command = UpdateActivePlayersCommand()
    result = command_executor.execute(command)

    if settings.is_dev():
        dev_pubsub_service.process_pubsub_payloads()

    return result


@router.post("/update_games")
@require_role(Role.admin)
async def update_games(
    request: Request,
    sim_state: Optional[SimState] = None,
    command_executor: UpdateGamesCommandExecutor = Depends(create_update_games_command_executor)
):
    command = UpdateGamesCommand(sim_state=sim_state)
    return command_executor.execute(command)


@router.post("/end_of_day")
async def end_of_day(
    service: EndOfDayService = Depends(create_end_of_day_service),
    settings: Settings = Depends(get_settings),
    dev_pubsub_service: DevPubSubService = Depends(create_dev_pubsub_service),
):
    service.run_workflow()

    if settings.is_dev():
        dev_pubsub_service.process_pubsub_payloads()


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
    command: UpdateScheduleCommand,
    command_executor: UpdateScheduleCommandExecutor = Depends(create_update_schedule_command_executor),
):
    return command_executor.execute(command)
