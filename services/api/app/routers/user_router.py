from app.domain.services.user_existence_service import UserExistenceRequest, UserExistenceService, create_user_existence_service
from app.domain.commands.user.record_sign_in import RecordSignInCommand, RecordSignInCommandExecutor, create_record_sign_in_command_executor
from app.core.auth import get_current_user_id
from app.domain.commands.user.update_profile import UpdateProfileCommand, UpdateProfileCommandExecutor, create_update_profile_command_executor
from app.domain.commands.user.register_email import RegisterCommandExecutor, RegisterEmailCommand, create_register_email_command_executor
from fastapi import Depends
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
        cmd_ex: UpdateProfileCommandExecutor = Depends(create_update_profile_command_executor)):
    command.current_user_id = current_user_id
    return cmd_ex.execute(command)


@router.post("/exists")
async def does_user_exist(request: UserExistenceRequest, service: UserExistenceService = Depends(create_user_existence_service)):
    return service.does_user_exist(request.email)
