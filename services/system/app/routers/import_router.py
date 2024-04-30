from fastapi import Depends

from yards_py.core.pubsub.pubsub_push import PubSubPush
from yards_py.domain.entities.player import Player
from yards_py.domain.entities.schedule import Schedule
from yards_py.domain.entities.scheduled_game import ScheduledGame

from ..domain.commands.imports.import_schedule import ImportScheduleCommand, ImportScheduleCommandExecutor, create_import_schedule_command_executor
from .api_router import APIRouter

router = APIRouter(prefix="/import")


@router.put("/game")
async def import_game():
    pass


@router.put("/player")
async def import_player(
    push: PubSubPush,
):
    data = push.get_data()

    return Player.from_core(data)


@router.put("/schedule")
async def import_schedule(
    push: PubSubPush,
    executor: ImportScheduleCommandExecutor = Depends(create_import_schedule_command_executor),
):
    data = push.get_data()

    command = ImportScheduleCommand(data=data)

    return executor.execute(command)
