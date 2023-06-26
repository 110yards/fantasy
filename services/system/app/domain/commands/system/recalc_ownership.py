

from services.system.app.domain.services.ownership_service import OwnershipService
from yards_py.core.firestore_proxy import Query
from yards_py.domain.entities.player_season import PlayerSeason
from yards_py.domain.repositories.player_game_repository import PlayerGameRepository, create_player_game_repository
from yards_py.domain.repositories.player_repository import PlayerRepository, create_player_repository
from yards_py.domain.repositories.player_season_repository import PlayerSeasonRepository, create_player_season_repository
from typing import List
from yards_py.domain.repositories.public_repository import PublicRepository, create_public_repository
from fastapi import Depends
from yards_py.core.annotate_args import annotate_args
from yards_py.core.base_command_executor import BaseCommand, BaseCommandResult, BaseCommandExecutor


def create_recalc_ownership_command_executor(
    player_repo: PlayerRepository = Depends(create_player_repository),
):
    return RecalcOwnershipCommandExecutor(
        player_repo=player_repo,
    )


@annotate_args
class RecalcOwnershipCommand(BaseCommand):
    completed_week_number: int


@annotate_args
class RecalcOwnershipResult(BaseCommandResult[RecalcOwnershipCommand]):
    updated_players: List[PlayerSeason]


class RecalcOwnershipCommandExecutor(BaseCommandExecutor[RecalcOwnershipCommand, RecalcOwnershipResult]):
    def __init__(
        self,
        player_repo: PlayerRepository,
        ownership_service: OwnershipService,
    ):
        self.player_repo = player_repo
        self.ownership_service = ownership_service

    def on_execute(self, command: RecalcOwnershipCommand) -> RecalcOwnershipResult:

        ownership = self.ownership_service.get_ownership()
        
        for k, v in ownership.items():
            self.player_repo.set
