
from fastapi import Depends

from ..domain.commands.system.update_player_stats import BoxscorePlayerStats, UpdatePlayerStatsCommand, UpdatePlayerStatsCommandExecutor, create_update_player_stats_command_executor
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
    

@router.post("/player_stats_updated")
async def on_player_stats_updated(
    push: PubSubPush,
    executor: UpdatePlayerStatsCommandExecutor = Depends(create_update_player_stats_command_executor),
):    
    command = UpdatePlayerStatsCommand(
        player_boxscore=BoxscorePlayerStats(**push.get_data())
    )
    
    return executor.execute(command)
