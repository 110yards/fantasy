from datetime import datetime, timezone

from fastapi import Depends
from firebase_admin import firestore
from google.cloud.firestore_v1.transaction import Transaction

from yards_py.domain.entities.player import Player

from yards_py.domain.entities.system_transaction import SystemTransaction

from yards_py.domain.repositories.public_repository import PublicRepository, create_public_repository
from yards_py.domain.repositories.system_transaction_repository import SystemTransactionRepository, create_system_transaction_repository

from yards_py.domain.repositories.approval_player_repository import ApprovalPlayerRepository, create_approval_player_repository

from yards_py.core.base_command_executor import BaseCommand, BaseCommandExecutor, BaseCommandResult

from ...repositories.player_repository import PlayerRepository, create_player_repository


class MatchPlayerCommand(BaseCommand):
    approval_player_id: str
    match_player_id: str


class MatchPlayerResult(BaseCommandResult[MatchPlayerCommand]):
    pass


class MatchPlayerCommandExecutor(BaseCommandExecutor[MatchPlayerCommand, MatchPlayerResult]):
    def __init__(
        self,
        player_repo: PlayerRepository,
        approval_player_repo: ApprovalPlayerRepository,
        system_transaction_repo: SystemTransactionRepository,
        public_repo: PublicRepository,
    ):
        self.player_repo = player_repo
        self.approval_players_store = approval_player_repo
        self.system_transaction_repo = system_transaction_repo
        self.public_repo = public_repo

    def on_execute(self, command: MatchPlayerCommand) -> MatchPlayerResult:
        state = self.public_repo.get_state()
        season = state.current_season

        @firestore.transactional
        def add_player(trx: Transaction):
            updated_player = self.approval_players_store.get(command.approval_player_id, transaction=trx)
            if not updated_player:
                return MatchPlayerResult(command=command, error="Approval player not found.")

            original_player = self.player_repo.get(season, command.match_player_id, transaction=trx)
            if not original_player:
                return MatchPlayerResult(command=command, error="Match player not found.")

            system_transaction = SystemTransaction.match_player(user_id=command.request_user_id, updated_player=updated_player, original_player=original_player)

            merged_player = Player(**updated_player.dict())
            merged_player.player_id = original_player.player_id  # always retain the original id
            merged_player.id = original_player.player_id  # always retain the original firestore id
            merged_player.alternate_computed_ids.append(updated_player.player_id)  # add the new computed id to the alternate list for future matching
            # merged_player.last_updated = datetime.now(tz=timezone.utc)

            self.system_transaction_repo.create(system_transaction, transaction=trx)
            self.player_repo.set(season, merged_player, transaction=trx)
            self.approval_players_store.delete(updated_player.player_id, transaction=trx)

            return MatchPlayerResult(command=command)

        trx = self.player_repo.firestore.create_transaction()
        return add_player(trx)


def create_match_player_command_executor(
    player_repo: PlayerRepository = Depends(create_player_repository),
    approval_player_repo: ApprovalPlayerRepository = Depends(create_approval_player_repository),
    system_transaction_repo: SystemTransactionRepository = Depends(create_system_transaction_repository),
    public_repo: PublicRepository = Depends(create_public_repository),
) -> MatchPlayerCommandExecutor:
    return MatchPlayerCommandExecutor(
        player_repo=player_repo,
        approval_player_repo=approval_player_repo,
        system_transaction_repo=system_transaction_repo,
        public_repo=public_repo,
    )
