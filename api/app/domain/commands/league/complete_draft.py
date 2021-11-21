
from api.app.domain.repositories.league_week_matchup_repository import LeagueWeekMatchupRepository, create_league_week_matchup_repository
from api.app.domain.repositories.state_repository import StateRepository, create_state_repository
# from api.app.domain.services.schedule_service import generate_schedule
from api.app.domain.repositories.league_roster_repository import LeagueRosterRepository, create_league_roster_repository
from api.app.domain.repositories.league_config_repository import LeagueConfigRepository, create_league_config_repository
from api.app.domain.repositories.user_league_repository import UserLeagueRepository, create_user_league_repository
from api.app.domain.repositories.league_repository import LeagueRepository, create_league_repository
from api.app.domain.entities.schedule import PlayoffType, Schedule
from typing import Optional
from api.app.config.config import Settings, get_settings
from fastapi import Depends
from api.app.core.annotate_args import annotate_args
from api.app.core.base_command_executor import BaseCommand, BaseCommandResult, BaseCommandExecutor
from firebase_admin import firestore


def create_complete_draft_command_executor(
    settings: Settings = Depends(get_settings),
    league_repo: LeagueRepository = Depends(create_league_repository),
    league_config_repo: LeagueConfigRepository = Depends(create_league_config_repository),
    user_league_repo: UserLeagueRepository = Depends(create_user_league_repository),
    league_roster_repo: LeagueRosterRepository = Depends(create_league_roster_repository),
    state_repo: StateRepository = Depends(create_state_repository),
    league_week_matchup_repo: LeagueWeekMatchupRepository = Depends(create_league_week_matchup_repository),

):
    return CompleteDraftCommandExecutor(
        settings.season_weeks,
        league_repo,
        league_config_repo,
        user_league_repo,
        league_roster_repo,
        state_repo,
        league_week_matchup_repo,
    )


@annotate_args
class CompleteDraftCommand(BaseCommand):
    league_id: Optional[str]
    first_playoff_week: int
    playoff_type: PlayoffType
    enable_loser_playoff: bool


@annotate_args
class CompleteDraftResult(BaseCommandResult[CompleteDraftCommand]):
    schedule: Schedule


class CompleteDraftCommandExecutor(BaseCommandExecutor[CompleteDraftCommand, CompleteDraftResult]):

    def __init__(self,
                 season_weeks: int,
                 league_repo: LeagueRepository,
                 league_config_repo: LeagueConfigRepository,
                 user_league_repo: UserLeagueRepository,
                 league_roster_repo: LeagueRosterRepository,
                 state_repo: StateRepository,
                 league_week_matchup_repo: LeagueWeekMatchupRepository,
                 ):
        self.season_weeks = season_weeks
        self.league_repo = league_repo
        self.league_config_repo = league_config_repo
        self.user_league_repo = user_league_repo
        self.league_roster_repo = league_roster_repo
        self.state_repo = state_repo
        self.league_week_matchup_repo = league_week_matchup_repo

    def on_execute(self, command: CompleteDraftCommand) -> CompleteDraftResult:

        # state = self.state_repo.get()

        @firestore.transactional
        def complete_draft(transaction):
            # copy schedule to matchups
            # copy schedule to user
            # copy players to rosters and matchups
            # update league to active
            # rosters = self.league_roster_repo.get_all(command.league_id, transaction)

            # implemented and removed code from generate schedule below: to be adjusted
            # weeks = generate_schedule(
            #     self.season_weeks,
            #     rosters,
            #     command.first_playoff_week,
            #     command.playoff_type,
            #     command.enable_loser_playoff)

            # schedule = Schedule(
            #     weeks=weeks,
            #     playoff_type=command.playoff_type,
            #     first_playoff_week=command.first_playoff_week,
            #     enable_loser_playoff=command.enable_loser_playoff
            # )

            # league = self.league_repo.get(command.league_id, transaction)
            # league.schedule_generated = True
            # league.registration_closed = True

            # # FUTURE: This could happen asynchronously
            # week = next((x for x in weeks if x.week_number == state.current_week), None)
            # if week:
            #     user_leagues = {}
            #     for roster in rosters:
            #         user_league = self.user_league_repo.get(roster.id, command.league_id, transaction)
            #         matchup = next((x for x in week.matchups if x.home.id == roster.id or x.away.id == roster.id), None)
            #         if matchup:
            #             user_league.matchup = matchup # TODO: needs to be a matchup preview for matchup
            #             user_leagues[roster.id] = user_league

            # self.league_repo.update(league, transaction)
            # self.league_config_repo.set_schedule_config(command.league_id, schedule, transaction)

            # for roster_id in user_leagues:
            #     user_league = user_leagues[roster_id]
            #     self.user_league_repo.set(roster_id, user_league, transaction)

            # # TODO: don't do this until the draft is started, to avoid deletes
            # for week in weeks:
            #     for matchup in week.matchups:
            #         self.league_week_matchup_repo.set(command.league_id, week.week_number, matchup, transaction)

            # return GenerateScheduleResult(command=command, schedule=schedule)

            # return CompleteDraftResult(command=command, schedule=schedule)
            pass

        transaction = self.league_repo.firestore.create_transaction()
        return complete_draft(transaction)
