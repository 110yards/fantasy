from fastapi import Depends, Request

from ..core.auth import require_role
from ..core.role import Role
from ..domain.commands.mod.add_new_player import AddNewPlayerCommand, AddNewPlayerCommandExecutor, create_add_new_player_command_executor
from ..domain.commands.mod.match_player import MatchPlayerCommand, MatchPlayerCommandExecutor, create_match_player_command_executor
from .api_router import APIRouter

router = APIRouter(prefix="/mod")


@router.post("/add_new_player")
@require_role(Role.mod)
async def add_new_player(
    request: Request,
    command: AddNewPlayerCommand,
    command_executor: AddNewPlayerCommandExecutor = Depends(create_add_new_player_command_executor),
):
    return command_executor.execute(command)


@router.post("/match_player")
@require_role(Role.mod)
async def match_player(
    request: Request,
    command: MatchPlayerCommand,
    command_executor: MatchPlayerCommandExecutor = Depends(create_match_player_command_executor),
):
    return command_executor.execute(command)
