
from fastapi import Depends

from ..domain.commands.system.manual_update_game import ManualUpdateGameCommand, ManualUpdateGameCommandExecutor, create_manual_update_game_command_executor

from ..domain.commands.system.manual_update_scoreboard import ManualUpdateScoreboardCommand, ManualUpdateScoreboardCommandExecutor, create_manual_update_scoreboard_command_executor


from .api_router import APIRouter

router = APIRouter(prefix="/manual")

# This router handles events from the core service(s)

@router.post("/update_scoreboard")
async def update_scoreboard(
    executor: ManualUpdateScoreboardCommandExecutor = Depends(create_manual_update_scoreboard_command_executor),
):
    command = ManualUpdateScoreboardCommand()
    
    return executor.execute(command)
    

@router.post("/update_game/{game_id}")
async def update_game(
    game_id: int,
    executor: ManualUpdateGameCommandExecutor = Depends(create_manual_update_game_command_executor),
):
    command = ManualUpdateGameCommand(game_id=game_id)
    
    return executor.execute(command)
