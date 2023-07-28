from fastapi import Depends
from firebase_admin import firestore

from app.core.annotate_args import annotate_args
from app.core.base_command_executor import BaseCommand, BaseCommandExecutor, BaseCommandResult
from app.domain.repositories.user_repository import UserRepository, create_user_repository


@annotate_args
class UpdateModStatusCommand(BaseCommand):
    uid: str
    is_mod: bool


@annotate_args
class UpdateModStatusResult(BaseCommandResult[UpdateModStatusCommand]):
    pass


class UpdateModStatusExecutor(BaseCommandExecutor[UpdateModStatusCommand, UpdateModStatusResult]):
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def on_execute(self, command: UpdateModStatusCommand) -> UpdateModStatusResult:
        @firestore.transactional
        def update(transaction):
            user = self.user_repository.get(command.uid, transaction=transaction)

            if not user:
                return UpdateModStatusResult(command=command, error="User does not exist")

            user.is_mod = command.is_mod

            self.user_repository.update(user, transaction=transaction)

            return UpdateModStatusResult(command=command)

        return update(self.user_repository.firestore.create_transaction())


def create_update_mod_status_command_executor(
    user_repository: UserRepository = Depends(create_user_repository),
):
    return UpdateModStatusExecutor(user_repository)
