from fastapi import Depends, Request

from app.core.auth import get_current_user_id, require_role
from app.domain.commands.user.record_sign_in import RecordSignInCommand, RecordSignInCommandExecutor, create_record_sign_in_command_executor
from app.domain.commands.user.register_email import RegisterCommandExecutor, RegisterEmailCommand, create_register_email_command_executor
from app.domain.commands.user.update_profile import UpdateProfileCommand, UpdateProfileCommandExecutor, create_update_profile_command_executor
from app.domain.services.user_existence_service import UserExistenceRequest, UserExistenceService, create_user_existence_service

from ..core.role import Role
from ..domain.commands.user.update_mod_status import UpdateModStatusCommand, UpdateModStatusExecutor, create_update_mod_status_command_executor
from .api_router import APIRouter

router = APIRouter(prefix="/user")


@router.post("/register/email")
async def register_with_email(command: RegisterEmailCommand, cmd_ex: RegisterCommandExecutor = Depends(create_register_email_command_executor)):
    return cmd_ex.execute(command)


@router.post("/signin")
async def signin(
    current_user_id: str = Depends(get_current_user_id),
    cmd_ex: RecordSignInCommandExecutor = Depends(create_record_sign_in_command_executor),
):
    command = RecordSignInCommand(current_user_id=current_user_id)
    return cmd_ex.execute(command)


@router.put("/profile")
async def update_profile(
    command: UpdateProfileCommand,
    current_user_id: str = Depends(get_current_user_id),
    cmd_ex: UpdateProfileCommandExecutor = Depends(create_update_profile_command_executor),
):
    command.current_user_id = current_user_id
    return cmd_ex.execute(command)


@router.post("/exists")
async def does_user_exist(request: UserExistenceRequest, service: UserExistenceService = Depends(create_user_existence_service)):
    return service.does_user_exist(request.email)


@router.put("/{user_id}/mod")
@require_role(Role.admin)
async def make_mod(user_id: str, request: Request, executor: UpdateModStatusExecutor = Depends(create_update_mod_status_command_executor)):
    command = UpdateModStatusCommand(uid=user_id, is_mod=True)
    return executor.execute(command)


@router.delete("/{user_id}/mod")
@require_role(Role.admin)
async def remove_mod(user_id: str, request: Request, executor: UpdateModStatusExecutor = Depends(create_update_mod_status_command_executor)):
    command = UpdateModStatusCommand(uid=user_id, is_mod=False)
    return executor.execute(command)
