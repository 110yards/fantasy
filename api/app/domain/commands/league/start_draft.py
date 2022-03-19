
from api.app.domain.entities.league import League
from api.app.domain.services.notification_service import NotificationService, create_notification_service
from api.app.domain.services.schedule_service import ScheduledMatchup
from typing import Dict
from api.app.domain.entities.user_league_preview import UserLeaguePreview
from api.app.domain.entities.matchup_preview import MatchupPreview
from api.app.domain.entities.schedule import ScheduleWeek
from copy import deepcopy
from api.app.domain.entities.draft import Draft, generate_draft
from api.app.domain.enums.draft_state import DraftState
from api.app.domain.repositories.league_week_matchup_repository import LeagueWeekMatchupRepository, create_league_week_matchup_repository
from api.app.domain.repositories.state_repository import StateRepository, create_state_repository
from api.app.domain.repositories.league_roster_repository import LeagueRosterRepository, create_league_roster_repository
from api.app.domain.repositories.league_config_repository import LeagueConfigRepository, create_league_config_repository
from api.app.domain.repositories.user_league_repository import UserLeagueRepository, create_user_league_repository
from api.app.domain.repositories.league_repository import LeagueRepository, create_league_repository
from fastapi import Depends
from api.app.core.annotate_args import annotate_args
from api.app.core.base_command_executor import BaseCommand, BaseCommandResult, BaseCommandExecutor
from firebase_admin import firestore


def create_start_draft_command_executor(
    league_repo: LeagueRepository = Depends(create_league_repository),
    league_config_repo: LeagueConfigRepository = Depends(create_league_config_repository),
    user_league_repo: UserLeagueRepository = Depends(create_user_league_repository),
    league_roster_repo: LeagueRosterRepository = Depends(create_league_roster_repository),
    state_repo: StateRepository = Depends(create_state_repository),
    league_week_matchup_repo: LeagueWeekMatchupRepository = Depends(create_league_week_matchup_repository),
    notification_service: NotificationService = Depends(create_notification_service),
):
    return StartDraftCommandExecutor(
        league_repo,
        league_config_repo,
        user_league_repo,
        league_roster_repo,
        state_repo,
        league_week_matchup_repo,
        notification_service,
    )


@annotate_args
class StartDraftCommand(BaseCommand):
    league_id: str


@annotate_args
class StartDraftResult(BaseCommandResult[StartDraftCommand]):
    draft: Draft
    league: League


class StartDraftCommandExecutor(BaseCommandExecutor[StartDraftCommand, StartDraftResult]):

    def __init__(self,
                 league_repo: LeagueRepository,
                 league_config_repo: LeagueConfigRepository,
                 user_league_repo: UserLeagueRepository,
                 league_roster_repo: LeagueRosterRepository,
                 state_repo: StateRepository,
                 league_week_matchup_repo: LeagueWeekMatchupRepository,
                 notification_service: NotificationService,
                 ):
        self.league_repo = league_repo
        self.league_config_repo = league_config_repo
        self.user_league_repo = user_league_repo
        self.league_roster_repo = league_roster_repo
        self.state_repo = state_repo
        self.league_week_matchup_repo = league_week_matchup_repo
        self.notification_service = notification_service

    def on_execute(self, command: StartDraftCommand) -> StartDraftResult:

        current_week = self.state_repo.get().current_week

        @firestore.transactional
        def start_draft(transaction):
            league = self.league_repo.get(command.league_id, transaction)

            if not league:
                return StartDraftResult(command=command, error="League not found")

            if not league.draft_state == DraftState.NOT_STARTED:
                return StartDraftResult(command=command, error="Draft is already in progress")

            if not league.draft_type:
                return StartDraftResult(command=command, error="Draft type not set")

            rosters = self.league_roster_repo.get_all(command.league_id, transaction)
            user_league_previews: Dict[str, UserLeaguePreview] = {}

            for roster in rosters:
                preview = self.user_league_repo.get(roster.id, command.league_id, transaction)
                user_league_previews[roster.id] = preview

            roster_config = self.league_config_repo.get_positions_config(command.league_id, transaction)

            draft_order = deepcopy(league.draft_order)
            draft = generate_draft(league.commissioner_id, league.draft_type, rosters, roster_config, draft_order)
            schedule = self.league_config_repo.get_schedule_config(league.id, transaction)

            league.draft_state = DraftState.IN_PROGRESS
            league.registration_closed = True

            self.league_repo.update(league, transaction)
            self.league_config_repo.set_draft(league.id, draft, transaction)

            current_schedule_week: ScheduleWeek

            for week in schedule.weeks:
                for matchup in week.matchups:
                    new_matchup = self.league_week_matchup_repo.create(league.id, week.week_number, matchup, transaction)
                    if week.week_number == current_week:
                        current_schedule_week = week
                        for roster in rosters:
                            if (matchup.away and roster.id == matchup.away.id) or (matchup.home and roster.id == matchup.home.id):
                                roster.current_matchup = new_matchup.id

            for roster in rosters:
                roster.positions.clear()
                for position_id in league.positions:
                    position = league.positions[position_id]
                    roster.positions[position_id] = position

                if draft.draft_order:
                    roster.draft_budget = draft.draft_order[roster.id].budget

                preview = user_league_previews[roster.id]
                matchup: ScheduledMatchup = next((m for m in current_schedule_week.matchups if m.id == roster.current_matchup), None)
                if matchup:
                    preview.matchup = MatchupPreview.from_matchup(matchup)
                    self.user_league_repo.set(roster.id, preview, transaction)

                self.league_roster_repo.set(league.id, roster, transaction)

            return StartDraftResult(command=command, draft=draft, league=league)

        transaction = self.league_repo.firestore.create_transaction()
        result = start_draft(transaction)

        if result.success:
            self.notification_service.send_draft_event(result.league, "The commissioner has started the draft")

        return result
