from typing import Optional

from fastapi import Depends
from firebase_admin import firestore

from app.domain.enums.draft_state import DraftState
from app.domain.repositories.league_config_repository import LeagueConfigRepository, create_league_config_repository
from app.domain.repositories.league_repository import LeagueRepository, create_league_repository
from app.domain.repositories.league_roster_repository import LeagueRosterRepository, create_league_roster_repository
from app.yards_py.core.annotate_args import annotate_args
from app.yards_py.core.base_command_executor import BaseCommand, BaseCommandExecutor, BaseCommandResult
from app.yards_py.domain.entities.schedule import PlayoffType, Schedule
from app.yards_py.domain.services.schedule_service import generate_schedule

from ...repositories.public_repository import PublicRepository, create_public_repository
from ...stores.season_schedule_store import SeasonScheduleStore, create_season_schedule_store


def create_generate_schedule_command_executor(
    league_repo: LeagueRepository = Depends(create_league_repository),
    league_config_repo: LeagueConfigRepository = Depends(create_league_config_repository),
    league_roster_repo: LeagueRosterRepository = Depends(create_league_roster_repository),
    schedule_score: SeasonScheduleStore = Depends(create_season_schedule_store),
    public_repo: PublicRepository = Depends(create_public_repository),
):
    return GenerateScheduleCommandExecutor(
        league_repo,
        league_config_repo,
        league_roster_repo,
        schedule_store=schedule_score,
        public_repo=public_repo,
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
    def __init__(
        self,
        league_repo: LeagueRepository,
        league_config_repo: LeagueConfigRepository,
        league_roster_repo: LeagueRosterRepository,
        schedule_store: SeasonScheduleStore,
        public_repo: PublicRepository,
    ):
        self.league_repo = league_repo
        self.league_config_repo = league_config_repo
        self.league_roster_repo = league_roster_repo
        self.schedule_store = schedule_store
        self.public_repo = public_repo

    def on_execute(self, command: GenerateScheduleCommand) -> GenerateScheduleResult:
        state = self.public_repo.get_state()
        schedule = self.schedule_store.get_schedule(state.current_season)

        if not schedule:
            return GenerateScheduleResult(command=command, error="Schedule not found")

        season_weeks = len(schedule.weeks)

        scoreboard = self.public_repo.get_scoreboard()

        min_playoff_start_week = state.current_week + 1

        if scoreboard and scoreboard.any_locks():
            min_playoff_start_week += 1

        first_playoff_week = command.first_playoff_week
        if first_playoff_week < min_playoff_start_week:
            first_playoff_week = min_playoff_start_week

        @firestore.transactional
        def set_schedule(transaction):
            rosters = self.league_roster_repo.get_all(command.league_id, transaction)
            if command.playoff_type > len(rosters):
                return GenerateScheduleResult(command=command, error="Invalid playoff type (not enough teams)")

            weeks = generate_schedule(season_weeks, rosters, first_playoff_week, command.playoff_type, command.enable_loser_playoff)

            schedule = Schedule(
                weeks=weeks, playoff_type=command.playoff_type, first_playoff_week=first_playoff_week, enable_loser_playoff=command.enable_loser_playoff
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
