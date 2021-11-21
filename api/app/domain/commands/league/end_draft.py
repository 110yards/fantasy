
from api.app.domain.services.draft_service import DraftService, create_draft_service
from api.app.domain.enums.draft_state import DraftState
from api.app.domain.repositories.league_config_repository import LeagueConfigRepository, create_league_config_repository
from api.app.domain.repositories.league_repository import LeagueRepository, create_league_repository
from fastapi import Depends
from api.app.core.annotate_args import annotate_args
from api.app.core.base_command_executor import BaseCommand, BaseCommandResult, BaseCommandExecutor
from firebase_admin import firestore


def create_end_draft_command_executor(
    league_repo: LeagueRepository = Depends(create_league_repository),
    league_config_repo: LeagueConfigRepository = Depends(create_league_config_repository),
    draft_service: DraftService = Depends(create_draft_service),

):
    return EndDraftCommandExecutor(
        league_repo,
        league_config_repo,
        draft_service=draft_service,
    )


@annotate_args
class EndDraftCommand(BaseCommand):
    league_id: str


@annotate_args
class EndDraftResult(BaseCommandResult[EndDraftCommand]):
    pass


class EndDraftCommandExecutor(BaseCommandExecutor[EndDraftCommand, EndDraftResult]):

    def __init__(self,
                 league_repo: LeagueRepository,
                 league_config_repo: LeagueConfigRepository,
                 draft_service: DraftService,
                 ):
        self.league_repo = league_repo
        self.league_config_repo = league_config_repo
        self.draft_service = draft_service

    def on_execute(self, command: EndDraftCommand) -> EndDraftResult:

        @firestore.transactional
        def end_draft(transaction):
            league = self.league_repo.get(command.league_id, transaction)

            if not league:
                return EndDraftResult(command=command, error="League not found")

            if league.draft_state == DraftState.COMPLETE:
                return EndDraftResult(command=command, error="Draft is already complete")

            if not league.draft_state == DraftState.IN_PROGRESS:
                return EndDraftResult(command=command, error="Draft has not started yet")

            if not command.request_user_id == league.commissioner_id:
                return EndDraftResult(command=command, error="Only the commissioner can do that")

            draft = self.league_config_repo.get_draft(league.id)

            self.draft_service.complete(draft, league, transaction)

            return EndDraftResult(command=command, draft=draft)

        transaction = self.league_repo.firestore.create_transaction()
        result = end_draft(transaction)

        return result
