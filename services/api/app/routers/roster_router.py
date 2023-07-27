from fastapi import Depends, Request

from app.core.auth import get_current_user_id, require_role
from app.core.role import Role
from app.domain.commands.roster.add_player import AddPlayerCommand, AddPlayerCommandExecutor, create_add_player_command_executor
from app.domain.commands.roster.ban_name_changes import SetNameChangeBanCommand, SetNameChangeBanCommandExecutor, create_set_name_change_ban_command_executor
from app.domain.commands.roster.cancel_bid import CancelBidCommand, CancelBidCommandExecutor, create_cancel_bid_command_executor
from app.domain.commands.roster.drop_player import DropPlayerCommand, DropPlayerCommandExecutor, create_drop_player_command_executor
from app.domain.commands.roster.move_player import MovePlayerCommand, MovePlayerCommandExecutor, create_move_player_command_executor
from app.domain.commands.roster.update_roster_name import UpdateRosterNameCommand, UpdateRosterNameCommandExecutor, create_update_roster_name_command_executor
from app.domain.commands.roster.update_waiver_budget import (
    UpdateWaiverBudgetCommand,
    UpdateWaiverBudgetCommandExecutor,
    create_update_waiver_budget_command_executor,
)
from app.domain.services.roster_progress_service import ProgressRequest, ProgressService, create_roster_progress_service

from ..domain.commands.roster.transfer_ownership import TransferOwnershipCommand, TransferOwnershipCommandExecutor, create_transfer_ownership_command_executor
from .api_router import APIRouter

router = APIRouter(prefix="/roster")


@router.put("/name")
async def update_roster_name(
    command: UpdateRosterNameCommand,
    current_user_id: str = Depends(get_current_user_id),
    cmd_ex: UpdateRosterNameCommandExecutor = Depends(create_update_roster_name_command_executor),
):
    command.current_user_id = current_user_id
    return cmd_ex.execute(command)


@router.put("/name_change_ban")
async def set_name_change_ban(command: SetNameChangeBanCommand, cmd_ex: SetNameChangeBanCommandExecutor = Depends(create_set_name_change_ban_command_executor)):
    return cmd_ex.execute(command)


@router.post("/drop")
async def drop_player(
    command: DropPlayerCommand,
    command_executor: DropPlayerCommandExecutor = Depends(create_drop_player_command_executor),
):
    return command_executor.execute(command)


@router.post("/add")
async def add_player(
    command: AddPlayerCommand,
    command_executor: AddPlayerCommandExecutor = Depends(create_add_player_command_executor),
):
    command.admin_override = False
    return command_executor.execute(command)


@router.post("/admin/add")
@require_role(Role.admin)
async def admin_add_player(
    request: Request,
    command: AddPlayerCommand,
    command_executor: AddPlayerCommandExecutor = Depends(create_add_player_command_executor),
):
    command.admin_override = True
    return command_executor.execute(command)


@router.post("/move")
async def move_player(
    command: MovePlayerCommand,
    command_executor: MovePlayerCommandExecutor = Depends(create_move_player_command_executor),
):
    return command_executor.execute(command)


@router.post("/cancel_bid")
async def cancel_bid(
    command: CancelBidCommand,
    command_executor: CancelBidCommandExecutor = Depends(create_cancel_bid_command_executor),
):
    return command_executor.execute(command)


@router.post("/progress")
async def progress(
    request: ProgressRequest,
    service: ProgressService = Depends(create_roster_progress_service),
):
    return service.get_projection(request.league_id, request.roster_id)


@router.put("/waiver_budget")
async def set_waiver_budget(
    command: UpdateWaiverBudgetCommand,
    current_user_id: str = Depends(get_current_user_id),
    command_executor: UpdateWaiverBudgetCommandExecutor = Depends(create_update_waiver_budget_command_executor),
):
    command.current_user_id = current_user_id
    return command_executor.execute(command)


@router.put("/transfer_ownership")
async def transfer_ownership(
    command: TransferOwnershipCommand,
    command_executor: TransferOwnershipCommandExecutor = Depends(create_transfer_ownership_command_executor),
):
    return command_executor.execute(command)
