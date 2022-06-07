
from services.api.app.domain.repositories.league_config_repository import LeagueConfigRepository, create_league_config_repository
from fastapi import Depends
from yards_py.core.annotate_args import annotate_args
from yards_py.core.base_command_executor import BaseCommand, BaseCommandResult, BaseCommandExecutor
from firebase_admin import firestore


def create_pause_resume_draft_command_executor(league_config_repo: LeagueConfigRepository = Depends(create_league_config_repository)):
    return PauseResumeDraftCommandExecutor(league_config_repo)


@annotate_args
class PauseResumeDraftCommand(BaseCommand):
    league_id: str
    pause: bool


@annotate_args
class PauseResumeDraftResult(BaseCommandResult[PauseResumeDraftCommand]):
    pass


class PauseResumeDraftCommandExecutor(BaseCommandExecutor[PauseResumeDraftCommand, PauseResumeDraftResult]):

    def __init__(self, league_config_repo: LeagueConfigRepository):
        self.league_config_repo = league_config_repo

    def on_execute(self, command: PauseResumeDraftCommand) -> PauseResumeDraftResult:
        @firestore.transactional
        def update(transaction):
            draft = self.league_config_repo.get_draft(command.league_id, transaction)
            draft.is_paused = command.pause

            if command.pause:
                message = "The commissioner paused the draft"
            else:
                message = "The commissioner resumed the draft"

            draft.draft_events.insert(0, message)

            self.league_config_repo.set_draft(command.league_id, draft, transaction)

            return PauseResumeDraftResult(command=command)

        transaction = self.league_config_repo.firestore.create_transaction()
        return update(transaction)
