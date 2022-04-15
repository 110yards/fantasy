

from api.app.domain.entities.state import State
from api.app.domain.repositories.public_repository import PublicRepository, create_public_repository
from fastapi import Depends
from api.app.core.annotate_args import annotate_args
from api.app.core.base_command_executor import BaseCommand, BaseCommandResult, BaseCommandExecutor
from firebase_admin.firestore import firestore
from google.cloud.firestore import Transaction


def create_end_system_waivers_command_executor(
    public_repo: PublicRepository = Depends(create_public_repository),
):
    return EndSystemWaiversCommandExecutor(
        public_repo=public_repo,
    )


@annotate_args
class EndSystemWaiversCommand(BaseCommand):
    pass


@annotate_args
class EndSystemWaiversResult(BaseCommandResult[EndSystemWaiversCommand]):
    state: State


class EndSystemWaiversCommandExecutor(BaseCommandExecutor[EndSystemWaiversCommand, EndSystemWaiversResult]):
    def __init__(
        self,
        public_repo: PublicRepository,
    ):
        self.public_repo = public_repo

    def on_execute(self, command: EndSystemWaiversCommand) -> EndSystemWaiversResult:

        @firestore.transactional
        def end_system_waivers(transaction: Transaction) -> EndSystemWaiversResult:
            state = self.public_repo.get_state(transaction)
            state.waivers_active = False
            state.waivers_end = None
            self.public_repo.set_state(state, transaction)

            return EndSystemWaiversResult(command=command, state=state)

        transaction = self.public_repo.firestore.create_transaction()
        return end_system_waivers(transaction)
