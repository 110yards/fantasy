from fastapi import Depends

from yards_py.core.base_command_executor import BaseCommand, BaseCommandExecutor, BaseCommandResult
from api.app.domain.repositories.public_repository import PublicRepository, create_public_repository


def create_reset_week_end_command_executor(
    public_repo: PublicRepository = Depends(create_public_repository)
):
    return ResetWeekEndCommandExecutor(public_repo)


class ResetWeekEndCommand(BaseCommand):
    pass


class ResetWeekEndResult(BaseCommandResult[ResetWeekEndCommand]):
    pass


class ResetWeekEndCommandExecutor(BaseCommandExecutor[ResetWeekEndCommand, ResetWeekEndResult]):
    def __init__(
        self,
        public_repo: PublicRepository
    ):
        self.public_repo = public_repo

    def on_execute(self, _: ResetWeekEndCommand) -> ResetWeekEndResult:

        state = self.public_repo.get_state()

        state.current_week -= 1
        state.waivers_active = False

        self.public_repo.set_state(state)
