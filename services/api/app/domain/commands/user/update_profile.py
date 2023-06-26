
from typing import Optional
from app.domain.repositories.user_repository import UserRepository, create_user_repository
from fastapi import Depends
from app.yards_py.core.annotate_args import annotate_args
from app.yards_py.core.base_command_executor import BaseCommand, BaseCommandResult, BaseCommandExecutor
from app.yards_py.core.publisher import Publisher
from app.di import create_publisher


def create_update_profile_command_executor(
    user_repository: UserRepository = Depends(create_user_repository),
    publisher: Publisher = Depends(create_publisher),
):
    return UpdateProfileCommandExecutor(user_repository, publisher)


@annotate_args
class UpdateProfileCommand(BaseCommand):
    uid: str
    display_name: str
    current_user_id: Optional[str]


@annotate_args
class UpdateProfileResult(BaseCommandResult[UpdateProfileCommand]):
    pass


class UpdateProfileCommandExecutor(BaseCommandExecutor[UpdateProfileCommand, UpdateProfileResult]):

    def __init__(self, user_repository: UserRepository, publisher: Publisher):
        self.user_repository = user_repository
        self.publisher = publisher

    def on_execute(self, command: UpdateProfileCommand) -> UpdateProfileResult:

        user = self.user_repository.get(command.uid)

        if not user:
            return UpdateProfileResult(command=command, error="User does not exist")

        # TODO: admins should be able to update other users

        if command.uid != command.current_user_id:
            return UpdateProfileResult(command=command, error="Forbidden")

        user.display_name = command.display_name

        self.user_repository.update(user)

        return UpdateProfileResult(command=command)
