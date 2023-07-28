from typing import Optional

from fastapi import Depends
from firebase_admin import firestore

from app.core.annotate_args import annotate_args
from app.core.base_command_executor import BaseCommand, BaseCommandExecutor, BaseCommandResult
from app.domain.entities.draft import Draft
from app.domain.entities.league import League
from app.domain.enums.draft_state import DraftState
from app.domain.repositories.league_config_repository import LeagueConfigRepository, create_league_config_repository
from app.domain.repositories.league_repository import LeagueRepository, create_league_repository
from app.domain.repositories.league_week_matchup_repository import LeagueWeekMatchupRepository, create_league_week_matchup_repository
from app.domain.services.notification_service import NotificationService, create_notification_service


def create_reset_draft_command_executor(
    league_repo: LeagueRepository = Depends(create_league_repository),
    league_config_repo: LeagueConfigRepository = Depends(create_league_config_repository),
    league_week_matchup_repo: LeagueWeekMatchupRepository = Depends(create_league_week_matchup_repository),
    notification_service: NotificationService = Depends(create_notification_service),
):
    return ResetDraftCommandExecutor(
        league_repo,
        league_config_repo,
        league_week_matchup_repo,
        notification_service=notification_service,
    )


@annotate_args
class ResetDraftCommand(BaseCommand):
    league_id: str


@annotate_args
class ResetDraftResult(BaseCommandResult[ResetDraftCommand]):
    draft: Draft
    league: Optional[League] = None


class ResetDraftCommandExecutor(BaseCommandExecutor[ResetDraftCommand, ResetDraftResult]):
    def __init__(
        self,
        league_repo: LeagueRepository,
        league_config_repo: LeagueConfigRepository,
        league_week_matchup_repo: LeagueWeekMatchupRepository,
        notification_service: NotificationService,
    ):
        self.league_repo = league_repo
        self.league_config_repo = league_config_repo
        self.league_week_matchup_repo = league_week_matchup_repo
        self.notification_service = notification_service

    def on_execute(self, command: ResetDraftCommand) -> ResetDraftResult:
        @firestore.transactional
        def start_draft(transaction):
            league = self.league_repo.get(command.league_id, transaction)

            if not league:
                return ResetDraftResult(command=command, error="League not found")

            if league.draft_state == DraftState.COMPLETE:
                return ResetDraftResult(command=command, error="Draft is already complete")

            if not league.draft_state == DraftState.IN_PROGRESS:
                return ResetDraftResult(command=command, error="Draft has not started yet")

            if not command.request_user_id == league.commissioner_id:
                return ResetDraftResult(command=command, error="Only the commissioner can do that")

            draft = self.league_config_repo.get_draft(league.id)
            schedule = self.league_config_repo.get_schedule_config(league.id)

            last_slot_index = -1
            for slot in draft.slots:
                if slot.completed:
                    last_slot_index += 1
                else:
                    break

            if last_slot_index > -1:
                return ResetDraftResult(command=command, error="All draft picks must be undone before the resetting the draft")

            for week in schedule.weeks:
                for matchup in week.matchups:
                    self.league_week_matchup_repo.delete(league.id, week.week_number, matchup.id, transaction)

            league.draft_state = DraftState.RESET

            self.league_repo.update(league, transaction)

            return ResetDraftResult(command=command, draft=draft, league=league)

        transaction = self.league_repo.firestore.create_transaction()
        result = start_draft(transaction)

        if result.success:
            self.league_repo.partial_update(command.league_id, {"draft_state": DraftState.NOT_STARTED})

            self.notification_service.send_draft_event(result.league, "The commissioner reset the draft")

        return result
