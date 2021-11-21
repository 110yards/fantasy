
from api.app.domain.entities.scoring_info import ScoringInfo
from api.app.domain.repositories.public_repository import PublicRepository, create_public_repository
from fastapi import Depends
from api.app.core.annotate_args import annotate_args
from api.app.core.base_command_executor import BaseCommand, BaseCommandResult, BaseCommandExecutor


def create_insert_public_config_command_executor(
    public_repo: PublicRepository = Depends(create_public_repository),
):
    return InsertPublicConfigCommandExecutor(public_repo)


@annotate_args
class InsertPublicConfigCommand(BaseCommand):
    pass


@annotate_args
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
