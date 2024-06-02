
from fastapi import Depends

from yards_py.domain.entities.scoreboard import ScoreboardGame

from ..domain.commands.system.update_scoreboard import UpdateScoreboardCommand, UpdateScoreboardCommandExecutor, create_update_scoreboard_command_executor
from yards_py.core.pubsub.pubsub_push import PubSubPush
from .api_router import APIRouter

router = APIRouter(prefix="/core_event")

# This router handles events from the core service(s)

@router.post("/scoreboard_game_updated")
async def on_scoreboard_game_updated(
    push: PubSubPush,
    executor: UpdateScoreboardCommandExecutor = Depends(create_update_scoreboard_command_executor),
):
    command = UpdateScoreboardCommand(
        scoreboard_game=ScoreboardGame(**push.get_data())
    )
    
    return executor.execute(command)
    
