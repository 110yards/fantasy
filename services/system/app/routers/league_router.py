from fastapi import Depends
from services.system.app.domain.commands.league.create_league_subscriptions import (
    CreateLeagueSubscriptionsCommand, CreateLeagueSubscriptionsCommandExecutor,
    create_league_subscriptions_command_executor)
from yards_py.core.pubsub.pubsub_push import PubSubPush

from .api_router import APIRouter

router = APIRouter(prefix="/league")


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
