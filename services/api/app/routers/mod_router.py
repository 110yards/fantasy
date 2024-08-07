from fastapi import Depends, Request

from ..domain.commands.mod.revert_player_game import RevertPlayerGameCommand, RevertPlayerGameCommandExecutor, create_revert_player_game_command_executor

from ..domain.commands.mod.update_player_game import UpdatePlayerGameCommand, UpdatePlayerGameCommandExecutor, create_update_player_game_command_executor

from ..domain.services.system_proxy_service import SystemProxyService, create_system_proxy_service

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

@router.post("/update_game_data/{game_id}")
@require_role(Role.admin) # maybe mods later
async def update_game_data(
    request: Request,
    game_id: str,
    system_proxy_service: SystemProxyService = Depends(create_system_proxy_service),
):
    return system_proxy_service.post(f"manual/update_game/{game_id}")
    

@router.post("/update_player_game")
@require_role(Role.mod)
async def update_player_game(
    request: Request,
    command: UpdatePlayerGameCommand,
    command_executor: UpdatePlayerGameCommandExecutor = Depends(create_update_player_game_command_executor),
):
    return command_executor.execute(command)


@router.post("/revert_player_game")
@require_role(Role.mod)
async def revert_player_game(
    request: Request,
    command: RevertPlayerGameCommand,
    command_executor: RevertPlayerGameCommandExecutor = Depends(create_revert_player_game_command_executor),
):
    return command_executor.execute(command)

