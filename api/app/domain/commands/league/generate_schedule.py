
from api.app.domain.enums.draft_state import DraftState
from api.app.domain.repositories.league_week_matchup_repository import LeagueWeekMatchupRepository, create_league_week_matchup_repository
from api.app.domain.repositories.state_repository import StateRepository, create_state_repository
from api.app.domain.services.schedule_service import generate_schedule
from api.app.domain.repositories.league_roster_repository import LeagueRosterRepository, create_league_roster_repository
from api.app.domain.repositories.league_config_repository import LeagueConfigRepository, create_league_config_repository
from api.app.domain.repositories.user_league_repository import UserLeagueRepository, create_user_league_repository
from api.app.domain.repositories.league_repository import LeagueRepository, create_league_repository
from api.app.domain.entities.schedule import PlayoffType, Schedule
from typing import Optional
from api.app.config.settings import Settings, get_settings
from fastapi import Depends
from api.app.core.annotate_args import annotate_args
from api.app.core.base_command_executor import BaseCommand, BaseCommandResult, BaseCommandExecutor
from firebase_admin import firestore


def create_generate_schedule_command_executor(
    settings: Settings = Depends(get_settings),
    league_repo: LeagueRepository = Depends(create_league_repository),
    league_config_repo: LeagueConfigRepository = Depends(create_league_config_repository),
    user_league_repo: UserLeagueRepository = Depends(create_user_league_repository),
    league_roster_repo: LeagueRosterRepository = Depends(create_league_roster_repository),
    state_repo: StateRepository = Depends(create_state_repository),
    league_week_matchup_repo: LeagueWeekMatchupRepository = Depends(create_league_week_matchup_repository),

):
    return GenerateScheduleCommandExecutor(
        settings.season_weeks,
        league_repo,
        league_config_repo,
        league_roster_repo,
    )


@annotate_args
class GenerateScheduleCommand(BaseCommand):
    league_id: Optional[str]
    first_playoff_week: int
    playoff_type: PlayoffType
    enable_loser_playoff: bool


@annotate_args
class GenerateScheduleResult(BaseCommandResult[GenerateScheduleCommand]):
    schedule: Optional[Schedule]


class GenerateScheduleCommandExecutor(BaseCommandExecutor[GenerateScheduleCommand, GenerateScheduleResult]):

    def __init__(self,
                 season_weeks: int,
                 league_repo: LeagueRepository,
                 league_config_repo: LeagueConfigRepository,
                 league_roster_repo: LeagueRosterRepository,
                 ):
        self.season_weeks = season_weeks
        self.league_repo = league_repo
        self.league_config_repo = league_config_repo
        self.league_roster_repo = league_roster_repo

    def on_execute(self, command: GenerateScheduleCommand) -> GenerateScheduleResult:

        @firestore.transactional
        def set_schedule(transaction):
            rosters = self.league_roster_repo.get_all(command.league_id, transaction)

            weeks = generate_schedule(
                self.season_weeks,
                rosters,
                command.first_playoff_week,
                command.playoff_type,
                command.enable_loser_playoff)

            schedule = Schedule(
                weeks=weeks,
                playoff_type=command.playoff_type,
                first_playoff_week=command.first_playoff_week,
                enable_loser_playoff=command.enable_loser_playoff
            )

            league = self.league_repo.get(command.league_id, transaction)

            if league.draft_state != DraftState.NOT_STARTED:
                return GenerateScheduleResult(command=command, error="Schedule cannot be changed after league has started")

            league.schedule_generated = True
            league.registration_closed = True

            self.league_repo.update(league, transaction)
            self.league_config_repo.set_schedule_config(command.league_id, schedule, transaction)

            return GenerateScheduleResult(command=command, schedule=schedule)

        transaction = self.league_repo.firestore.create_transaction()
        return set_schedule(transaction)

        pass
