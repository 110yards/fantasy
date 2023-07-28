from datetime import datetime, timezone

from fastapi import Depends
from firebase_admin import firestore
from google.cloud.firestore_v1.transaction import Transaction

from ....core.base_command_executor import BaseCommand, BaseCommandExecutor, BaseCommandResult
from ...entities.system_transaction import SystemTransaction
from ...repositories.approval_player_repository import ApprovalPlayerRepository, create_approval_player_repository
from ...repositories.player_repository import PlayerRepository, create_player_repository
from ...repositories.system_transaction_repository import SystemTransactionRepository, create_system_transaction_repository


class AddNewPlayerCommand(BaseCommand):
    approval_player_id: str


class AddNewPlayerResult(BaseCommandResult[AddNewPlayerCommand]):
    pass


class AddNewPlayerCommandExecutor(BaseCommandExecutor[AddNewPlayerCommand, AddNewPlayerResult]):
    def __init__(
        self,
        player_repo: PlayerRepository,
        approval_player_repo: ApprovalPlayerRepository,
        system_transaction_repo: SystemTransactionRepository,
    ):
        self.player_repo = player_repo
        self.approval_players_store = approval_player_repo
        self.system_transaction_repo = system_transaction_repo

    def on_execute(self, command: AddNewPlayerCommand) -> AddNewPlayerResult:
        @firestore.transactional
        def add_player(trx: Transaction):
            player = self.approval_players_store.get(command.approval_player_id, transaction=trx)

            if not player:
                return AddNewPlayerResult(command=command, error="Player not found.")

            system_transaction = SystemTransaction.add_player(user_id=command.request_user_id, player=player)
            player.id = player.player_id
            player.last_updated = datetime.now(tz=timezone.utc)

            self.system_transaction_repo.create(system_transaction, transaction=trx)
            self.player_repo.create(player, transaction=trx)
            self.approval_players_store.delete(player.player_id, transaction=trx)

            return AddNewPlayerResult(command=command)

        trx = self.player_repo.firestore.create_transaction()
        return add_player(trx)


def create_add_new_player_command_executor(
    player_repo: PlayerRepository = Depends(create_player_repository),
    approval_player_repo: ApprovalPlayerRepository = Depends(create_approval_player_repository),
    system_transaction_repo: SystemTransactionRepository = Depends(create_system_transaction_repository),
) -> AddNewPlayerCommandExecutor:
    return AddNewPlayerCommandExecutor(
        player_repo=player_repo,
        approval_player_repo=approval_player_repo,
        system_transaction_repo=system_transaction_repo,
    )
