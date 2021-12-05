from typing import Optional

from api.app.config.settings import Settings, get_settings
from api.app.core.pubsub.pubsub_push import PubSubPush
from api.app.domain.commands.system.end_of_season import EndOfSeasonCommand, EndOfSeasonCommandExecutor, create_end_of_season_command_executor
from api.app.domain.commands.system.insert_public_config import (
    InsertPublicConfigCommand, InsertPublicConfigCommandExecutor,
    create_insert_public_config_command_executor)
from api.app.domain.commands.system.update_active_players import (
    UpdateActivePlayersCommand, UpdateActivePlayersCommandExecutor,
    UpdateActivePlayersCommandResult, update_active_players_command_executor)
from api.app.domain.commands.system.update_games import (
    SimState, UpdateGamesCommand, UpdateGamesCommandExecutor,
    create_update_games_command_executor)
from api.app.domain.commands.system.update_player_stats_for_week import (
    UpdatePlayerStatsForWeekCommand, UpdatePlayerStatsForWeekCommandExecutor,
    create_update_player_stats_for_week_command_executor)
from api.app.domain.events.configure_events import (ConfigureEvents,
                                                    create_configure_events)
from api.app.domain.repositories.state_repository import (StateRepository,
                                                          create_state_repository)
from api.app.domain.services.end_of_day_service import EndOfDayService, create_end_of_day_service
from api.app.domain.services.end_of_week_service import EndOfWeekRequest, EndOfWeekService, create_end_of_week_service
from api.app.domain.services.league_command_service import (
    LeagueCommandService, create_league_command_service)
from api.app.domain.services.smoke_test_service import smoke_test
from fastapi import Depends, Response, status

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


@router.post("/games")
async def update_games(
    week: Optional[int] = None,
    sim_state: Optional[SimState] = None,
    state_repo: StateRepository = Depends(create_state_repository),
    settings: Settings = Depends(get_settings),
    command_executor: UpdateGamesCommandExecutor = Depends(create_update_games_command_executor)
):
    state = state_repo.get()
    command = UpdateGamesCommand(season=settings.current_season, week=week or state.current_week, sim_state=sim_state)
    return command_executor.execute(command)


@router.post("/games/all")
async def update_all_games(
    settings: Settings = Depends(get_settings),
    command_executor: UpdateGamesCommandExecutor = Depends(create_update_games_command_executor)
):
    command = UpdateGamesCommand(season=settings.current_season)
    return command_executor.execute(command)


@router.post("/players", response_model=UpdateActivePlayersCommandResult)
# Invoked by scheduled task - gets all players from CFL team rosters and updates player master data
async def update_players(command_executor: UpdateActivePlayersCommandExecutor = Depends(update_active_players_command_executor)):
    command = UpdateActivePlayersCommand()
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


@router.post("/update_player_stats_for_week")
async def update_player_stats_for_week(
    command: UpdatePlayerStatsForWeekCommand,
    command_executor: UpdatePlayerStatsForWeekCommandExecutor = Depends(create_update_player_stats_for_week_command_executor),
):
    return command_executor.execute(command)


@router.post("/set_end_of_season")
async def set_end_of_season(
    command: EndOfSeasonCommand,
    command_executor: EndOfSeasonCommandExecutor = Depends(create_end_of_season_command_executor),
):
    return command_executor.execute(command)
