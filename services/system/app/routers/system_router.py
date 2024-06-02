from typing import Optional

from fastapi import Depends, Response, status
from services.system.app.domain.commands.system.end_of_season import (
    EndOfSeasonCommand, EndOfSeasonCommandExecutor,
    create_end_of_season_command_executor)
from ..domain.commands.system.import_prior_season_player_stats import ImportPriorSeasonPlayerStatsCommand, ImportPriorSeasonPlayerStatsCommandExecutor, create_import_prior_season_player_stats_command_executor
from services.system.app.domain.commands.system.insert_public_config import (
    InsertPublicConfigCommand, InsertPublicConfigCommandExecutor,
    create_insert_public_config_command_executor)
from services.system.app.domain.commands.system.update_active_players import (
    UpdateActivePlayersCommand, UpdateActivePlayersCommandExecutor,
    UpdateActivePlayersCommandResult, update_active_players_command_executor)
# from services.system.app.domain.commands.system.update_games import (
#     SimState, UpdateGamesCommand, UpdateGamesCommandExecutor,
#     create_update_games_command_executor)
from services.system.app.domain.commands.system.update_schedule import (
    UpdateScheduleCommand, UpdateScheduleCommandExecutor,
    create_update_schedule_command_executor)
from services.system.app.domain.events.configure_events import (
    ConfigureEvents, create_configure_events)
from services.system.app.domain.services.end_of_day_service import (
    EndOfDayService, create_end_of_day_service)
from services.system.app.domain.services.end_of_week_service import (
    EndOfWeekRequest, EndOfWeekService, create_end_of_week_service)
from services.system.app.domain.services.import_season_service import (
    ImportSeasonService, create_previous_season_stats_service)
from services.system.app.domain.services.league_command_service import (
    LeagueCommandService, create_league_command_service)
from services.system.app.domain.services.recalc_waiver_budgets_service import RecalcWaiverBudgetsService, create_recalc_waiver_budgets_service
from services.system.app.domain.services.smoke_test_service import smoke_test
from services.system.app.domain.services.start_next_season_service import (
    StartNextSeasonService, create_start_next_season_service)
from yards_py.core.pubsub.pubsub_push import PubSubPush

from .api_router import APIRouter

router = APIRouter(prefix="/system")


@router.post("/configure")
async def configure(
    public_config_command_executor: InsertPublicConfigCommandExecutor = Depends(create_insert_public_config_command_executor),
    events_service: ConfigureEvents = Depends(create_configure_events)
):

    return {
        "events_configured": events_service.configure_events(),
        "public_info": public_config_command_executor.execute(InsertPublicConfigCommand()).success
    }


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


# @router.post("/games")
# async def update_games(
#     week: Optional[int] = None,
#     sim_state: Optional[SimState] = None,
#     command_executor: UpdateGamesCommandExecutor = Depends(create_update_games_command_executor)
# ):
#     command = UpdateGamesCommand(week=week, sim_state=sim_state)
#     return command_executor.execute(command)


# @router.post("/games/all")
# async def update_all_games(
#     command_executor: UpdateGamesCommandExecutor = Depends(create_update_games_command_executor)
# ):
#     command = UpdateGamesCommand()
#     return command_executor.execute(command)


@router.post("/players", response_model=UpdateActivePlayersCommandResult)
# Invoked by scheduled task - gets all players from CFL team rosters and updates player master data
async def update_players(
    command: Optional[UpdateActivePlayersCommand] = None,
    command_executor: UpdateActivePlayersCommandExecutor = Depends(update_active_players_command_executor)
):
    command = command or UpdateActivePlayersCommand()
    return command_executor.execute(command)

@router.post("/player_stats/import/{year}")
async def import_prior_season_player_stats(
    year: int,
    command_executor: ImportPriorSeasonPlayerStatsCommandExecutor = Depends(create_import_prior_season_player_stats_command_executor),
):
    command = ImportPriorSeasonPlayerStatsCommand(year=year)
    return command_executor.execute(command)

@router.post("/end_of_day")
async def end_of_day(
    service: EndOfDayService = Depends(create_end_of_day_service)
):
    service.run_workflow()


@router.post("/end_of_week")
async def end_of_week(
    push: PubSubPush,
    service: EndOfWeekService = Depends(create_end_of_week_service)
):
    push_data = push.get_data()
    request = EndOfWeekRequest(**push_data)
    return service.run_workflow(request.completed_week_number)


@router.post("/league_command")
async def league_command(
    league_id: str,
    push: PubSubPush,
    league_command_service: LeagueCommandService = Depends(create_league_command_service)
):
    return league_command_service.execute_league_command(league_id, push)


@router.post("/set_end_of_season")
async def set_end_of_season(
    command: EndOfSeasonCommand,
    command_executor: EndOfSeasonCommandExecutor = Depends(create_end_of_season_command_executor),
):
    return command_executor.execute(command)


@router.post("/schedule")
async def update_schedule(
    command: UpdateScheduleCommand,
    command_executor: UpdateScheduleCommandExecutor = Depends(create_update_schedule_command_executor),
):
    return command_executor.execute(command)


@router.post("/start_next_season")
async def start_next_season(
    season: Optional[int] = None,
    service: StartNextSeasonService = Depends(create_start_next_season_service),
):
    return service.run_workflow(season)


@router.post("/import_season")
async def import_season(
    season: int,
    clean: bool = False,
    service: ImportSeasonService = Depends(create_previous_season_stats_service),
):
    return service.import_season(season, clean)


@router.post("/recalc_waiver_budgets")
async def recalc_waiver_budgets(
    service: RecalcWaiverBudgetsService = Depends(create_recalc_waiver_budgets_service),
):
    return service.recalc()
