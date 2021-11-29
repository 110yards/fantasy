# from api.app.core.auth import require_role
from api.app.core.pubsub.pubsub_push import PubSubPush
from api.app.domain.commands.league.close_league_registration import (
    CloseLeagueRegistrationCommand, CloseLeagueRegistrationCommandExecutor,
    create_close_league_registration_command_executor)
from api.app.domain.commands.league.create_league import (
    CreateLeagueCommand, CreateLeagueCommandExecutor,
    create_league_command_executor)
from api.app.domain.commands.league.create_league_subscriptions import (
    CreateLeagueSubscriptionsCommand, CreateLeagueSubscriptionsCommandExecutor,
    create_league_subscriptions_command_executor)
from api.app.domain.commands.league.generate_schedule import (
    GenerateScheduleCommand, GenerateScheduleCommandExecutor,
    create_generate_schedule_command_executor)
from api.app.domain.commands.league.join_league import (
    JoinLeagueCommand, JoinLeagueCommandExecutor,
    create_join_league_command_executor)
from api.app.domain.commands.league.open_league_registration import (
    OpenLeagueRegistrationCommand, OpenLeagueRegistrationCommandExecutor,
    create_open_league_registration_command_executor)
from api.app.domain.commands.league.remove_roster import (
    RemoveRosterCommand, RemoveRosterCommandExecutor,
    create_remove_roster_command_executor)
from api.app.domain.commands.league.update_draft_order import (
    UpdateDraftOrderCommand, UpdateDraftOrderCommandExecutor,
    create_update_draft_order_command_executor)
from api.app.domain.commands.league.update_league import (
    UpdateLeagueCommand, UpdateLeagueCommandExecutor,
    create_update_league_command_executor)
from api.app.domain.commands.league.update_league_positions import (
    UpdateLeaguePositionsCommand, UpdateLeaguePositionsCommandExecutor,
    create_update_league_positions_command_executor)
from api.app.domain.commands.league.update_league_scoring import (
    UpdateLeagueScoringCommand, UpdateLeagueScoringCommandExecutor,
    create_update_league_scoring_command_executor)
from api.app.domain.entities.league import League
from api.app.domain.repositories.league_repository import LeagueRepository
from api.app.domain.repositories.repository_factory import get_league_repository
from fastapi import Depends, Request

from api.app.domain.services.discord_service import DiscordService, create_discord_service

from .api_router import APIRouter

router = APIRouter(prefix="/league")


@router.get("/{league_id}", response_model=League)
async def get_league(league_id: str, league_repo: LeagueRepository = Depends(get_league_repository)):
    return league_repo.get(league_id)


@router.post("/")
async def create_league(
        request: Request,
        command: CreateLeagueCommand,
        command_executor: CreateLeagueCommandExecutor = Depends(create_league_command_executor)):
    uid = request.state.uid
    command.commissioner_id = uid
    return command_executor.execute(command)


@router.post("/subscriptions")
async def configure_subscriptions(
    push: PubSubPush,
    command_executor: CreateLeagueSubscriptionsCommandExecutor = Depends(create_league_subscriptions_command_executor)
):
    league = push.get_data()
    command = CreateLeagueSubscriptionsCommand(league=league)
    return command_executor.execute(command)


@router.post("/fix_subscriptions")
async def fix_subscriptions(
    command: CreateLeagueSubscriptionsCommand,
    command_executor: CreateLeagueSubscriptionsCommandExecutor = Depends(create_league_subscriptions_command_executor)
):
    return command_executor.execute(command)


@router.put("/{league_id}/registration/close")
# @require_role(Role.commissioner)
async def close_registration(
        league_id: str,
        command_executor: CloseLeagueRegistrationCommandExecutor = Depends(create_close_league_registration_command_executor)
):
    command = CloseLeagueRegistrationCommand(league_id=league_id)
    return command_executor.execute(command)


@router.put("/{league_id}/registration/open")
# @require_role(Role.commissioner)
async def open_registration(
        league_id: str,
        command_executor: OpenLeagueRegistrationCommandExecutor = Depends(create_open_league_registration_command_executor)
):
    command = OpenLeagueRegistrationCommand(league_id=league_id)
    return command_executor.execute(command)


@router.post("/{league_id}/join")
async def join_league(
        request: Request,
        league_id: str,
        command: JoinLeagueCommand,
        command_executor: JoinLeagueCommandExecutor = Depends(create_join_league_command_executor)
):
    command.user_id = request.state.uid
    command.league_id = league_id
    return command_executor.execute(command)


@router.delete("/{league_id}/roster/{roster_id}")
# @require_role(Role.commissioner)
async def remove_roster(
    league_id: str,
    roster_id: str,
    command_executor: RemoveRosterCommandExecutor = Depends(create_remove_roster_command_executor)
):
    command = RemoveRosterCommand(league_id=league_id, roster_id=roster_id)
    return command_executor.execute(command)


@router.put("/{league_id}")
async def update_league(
    league_id: str,
    command: UpdateLeagueCommand,
    command_executor: UpdateLeagueCommandExecutor = Depends(create_update_league_command_executor),
):
    command.league_id = league_id
    return command_executor.execute(command)


@router.put("/{league_id}/positions")
async def update_positions(
    league_id: str,
    command: UpdateLeaguePositionsCommand,
    command_executor: UpdateLeaguePositionsCommandExecutor = Depends(create_update_league_positions_command_executor),
):
    command.league_id = league_id
    return command_executor.execute(command)


@router.put("/{league_id}/scoring")
async def update_scoring(
    league_id: str,
    command: UpdateLeagueScoringCommand,
    command_executor: UpdateLeagueScoringCommandExecutor = Depends(create_update_league_scoring_command_executor),
):
    command.league_id = league_id
    return command_executor.execute(command)


@router.put("/{league_id}/schedule")
async def generate_schedule(
    league_id: str,
    command: GenerateScheduleCommand,
    command_executor: GenerateScheduleCommandExecutor = Depends(create_generate_schedule_command_executor)
):
    command.league_id = league_id
    return command_executor.execute(command)


@router.put("/{league_id}/draft_order")
async def update_draft_order(
    league_id: str,
    command: UpdateDraftOrderCommand,
    command_executor: UpdateDraftOrderCommandExecutor = Depends(create_update_draft_order_command_executor)
):
    command.league_id = league_id
    return command_executor.execute(command)


@router.post("/{league_id}/test_discord")
async def test_discord(
    league_id: str,
    webhook_url: str,
    service: DiscordService = Depends(create_discord_service),
):
    service.send_test_notification(webhook_url)
