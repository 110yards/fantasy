
from datetime import datetime
from services.api.app.domain.repositories.user_repository import UserRepository, create_user_repository
from fastapi import Depends
from yards_py.core.annotate_args import annotate_args
from yards_py.core.base_command_executor import BaseCommand, BaseCommandResult, BaseCommandExecutor
from yards_py.core.publisher import Publisher
from services.api.app.di import create_publisher


def create_record_sign_in_command_executor(
    user_repository: UserRepository = Depends(create_user_repository),
    publisher: Publisher = Depends(create_publisher),
):
    return RecordSignInCommandExecutor(user_repository, publisher)


@annotate_args
class RecordSignInCommand(BaseCommand):
    current_user_id: str


@annotate_args
class RecordSignInResult(BaseCommandResult[RecordSignInCommand]):
    pass


class RecordSignInCommandExecutor(BaseCommandExecutor[RecordSignInCommand, RecordSignInResult]):

    def __init__(self, user_repository: UserRepository, publisher: Publisher):
        self.user_repository = user_repository
        self.publisher = publisher

    def on_execute(self, command: RecordSignInCommand) -> RecordSignInResult:

        user = self.user_repository.get(command.current_user_id)

        if not user:
            return RecordSignInResult(command=command, error="User does not exist")

        updates = {
            "last_sign_in": datetime.now(),
            "event_data.emailVerified": True,
        }

        self.user_repository.partial_update(user.id, updates)

        return RecordSignInResult(command=command)
