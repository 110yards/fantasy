from datetime import datetime, timedelta, timezone

from fastapi import Depends
from firebase_admin.firestore import firestore
from google.cloud.firestore import Transaction

from app.di import create_publisher

from .....core.publisher import Publisher
from ....store.state_store import StateStore, create_state_store
from ...command_result import CommandResult
from ...commands.system.start_system_waivers_command import StartSystemWaiversCommand


class StartSystemWaiversExecutor:
    def __init__(
        self,
        state_store: StateStore,
        publisher: Publisher,
    ):
        self.state_store = state_store
        self.publisher = publisher

    def execute(self, command: StartSystemWaiversCommand) -> CommandResult:
        @firestore.transactional
        def enable_waivers(transaction: Transaction):
            state = self.state_store.get(transaction)
            state.waivers_active = True
            state.waivers_end = datetime.now(tz=timezone.utc).today() + timedelta(days=1)
            completed_week_number = command.current_week_number
            state.current_week = completed_week_number + 1

            self.state_store.set(state, transaction)

            return CommandResult.success_result(f"Started waivers for {completed_week_number}")

        transaction = self.state_store.firestore_client.create_transaction()
        return enable_waivers(transaction)


def create_start_system_waivers_command_executor(
    state_store: StateStore = Depends(create_state_store),
    publisher: Publisher = Depends(create_publisher),
):
    return StartSystemWaiversExecutor(
        state_store=state_store,
        publisher=publisher,
    )
