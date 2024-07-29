from datetime import datetime, timezone

from fastapi import Depends
from firebase_admin import firestore
from google.cloud.firestore_v1.transaction import Transaction

from yards_py.domain.entities.player import Player
from yards_py.domain.repositories.user_repository import UserRepository, create_user_repository
from yards_py.domain.repositories.player_game_repository import PlayerGameRepository, create_player_game_repository

from yards_py.domain.entities.stats import Stats
from yards_py.domain.entities.system_transaction import SystemTransaction

from yards_py.domain.repositories.public_repository import PublicRepository, create_public_repository
from yards_py.domain.repositories.system_transaction_repository import SystemTransactionRepository, create_system_transaction_repository

from yards_py.domain.repositories.approval_player_repository import ApprovalPlayerRepository, create_approval_player_repository

from yards_py.core.base_command_executor import BaseCommand, BaseCommandExecutor, BaseCommandResult

from ...repositories.player_repository import PlayerRepository, create_player_repository


class UpdatePlayerGameCommand(BaseCommand):
    id: str
    season: int
    game_id: int
    stats: Stats


class UpdatePlayerGameResult(BaseCommandResult[UpdatePlayerGameCommand]):
    pass


class UpdatePlayerGameCommandExecutor(BaseCommandExecutor[UpdatePlayerGameCommand, UpdatePlayerGameResult]):
    def __init__(
        self,
        player_game_repo: PlayerGameRepository,
        player_repo: PlayerRepository,
        user_repo: UserRepository,
        system_transaction_repo: SystemTransactionRepository,
    ):
        self.player_game_repo = player_game_repo
        self.player_repo = player_repo
        self.user_repo = user_repo
        self.system_transaction_repo = system_transaction_repo

    def on_execute(self, command: UpdatePlayerGameCommand) -> UpdatePlayerGameResult:        

        @firestore.transactional
        def update(trx: Transaction):
            user = self.user_repo.get(command.request_user_id, transaction=trx)

            if not user:
                return UpdatePlayerGameResult(command=command, error="User not found.")

            player_game = self.player_game_repo.get(command.season, command.id, transaction=trx)
            
            if not player_game:
                return UpdatePlayerGameResult(command=command, error="Player game not found.")
            
            player = self.player_repo.get(command.season, player_game.player_id, transaction=trx)

            if not player:
                return UpdatePlayerGameResult(command=command, error="Player not found.")

            if not player_game.manual_override:
                # capture original stats to allow revert
                player_game.original_stats = player_game.stats
                
            player_game.stats = command.stats
            player_game.date_updated = datetime.now(tz=timezone.utc)
            player_game.manual_override = True

            system_transaction = SystemTransaction.update_player_game(user.id, player, command.game_id)

            self.system_transaction_repo.create(system_transaction, transaction=trx)
            self.player_game_repo.set(command.season, player_game, transaction=trx)

            return UpdatePlayerGameResult(command=command)

        trx = self.player_repo.firestore.create_transaction()
        return update(trx)


def create_update_player_game_command_executor(
    player_game_repo: PlayerGameRepository = Depends(create_player_game_repository),
    player_repo: PlayerRepository = Depends(create_player_repository),
    user_repo: UserRepository = Depends(create_user_repository),
    system_transaction_repo: SystemTransactionRepository = Depends(create_system_transaction_repository),
) -> UpdatePlayerGameCommandExecutor:
    return UpdatePlayerGameCommandExecutor(
        player_game_repo=player_game_repo,
        player_repo=player_repo,
        user_repo=user_repo,
        system_transaction_repo=system_transaction_repo,
    )
