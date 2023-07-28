from app.core.base_command_executor import BaseCommand, BaseCommandExecutor, BaseCommandResult
from app.domain.entities.scoring_info import ScoringInfo
from app.domain.repositories.public_repository import PublicRepository, create_public_repository
from fastapi import Depends


def create_insert_public_config_command_executor(
    public_repo: PublicRepository = Depends(create_public_repository),
):
    return InsertPublicConfigCommandExecutor(public_repo)


class InsertPublicConfigCommand(BaseCommand):
    pass


class InsertPublicConfigResult(BaseCommandResult[InsertPublicConfigCommand]):
    pass


class InsertPublicConfigCommandExecutor(BaseCommandExecutor[InsertPublicConfigCommand, InsertPublicConfigResult]):
    def __init__(
        self,
        public_repo: PublicRepository,
    ):
        self.public_repo = public_repo

    def on_execute(self, command: InsertPublicConfigCommand) -> InsertPublicConfigResult:
        self.public_repo.set_scoring_info(ScoringInfo())

        return InsertPublicConfigResult(command=command)
