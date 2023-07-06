

from app.di import create_publisher
from app.yards_py.domain.entities.scoreboard import Scoreboard
from app.yards_py.domain.entities.season_summary import SeasonSummary
from app.yards_py.domain.enums.draft_state import DraftState
from app.yards_py.domain.repositories.league_config_repository import LeagueConfigRepository, create_league_config_repository
from app.yards_py.domain.repositories.league_repository import LeagueRepository, create_league_repository
from app.yards_py.domain.repositories.league_roster_repository import LeagueRosterRepository, create_league_roster_repository
from app.yards_py.domain.repositories.public_repository import PublicRepository, create_public_repository
from app.yards_py.domain.repositories.season_summary_repository import SeasonSummaryRepository, create_season_summary_repository
from app.yards_py.domain.repositories.state_repository import StateRepository, create_state_repository
from typing import List, Optional
from app.yards_py.core.publisher import Publisher
from fastapi import Depends
from app.yards_py.core.annotate_args import annotate_args
from app.yards_py.core.base_command_executor import BaseCommand, BaseCommandResult, BaseCommandExecutor


def create_end_of_season_command_executor(
    publisher: Publisher = Depends(create_publisher),
    state_repo: StateRepository = Depends(create_state_repository),
    league_repo: LeagueRepository = Depends(create_league_repository),
    league_config_repo: LeagueConfigRepository = Depends(create_league_config_repository),
    league_roster_repo: LeagueRosterRepository = Depends(create_league_roster_repository),
    season_summary_repo: SeasonSummaryRepository = Depends(create_season_summary_repository),
    public_repo: PublicRepository = Depends(create_public_repository),
):
    return EndOfSeasonCommandExecutor(
        publisher=publisher,
        state_repo=state_repo,
        league_repo=league_repo,
        league_config_repo=league_config_repo,
        league_roster_repo=league_roster_repo,
        season_summary_repo=season_summary_repo,
        public_repo=public_repo,
    )


@annotate_args
class EndOfSeasonCommand(BaseCommand):
    league_id: Optional[str]


@annotate_args
class EndOfSeasonResult(BaseCommandResult[EndOfSeasonCommand]):
    failed: List[str]
    successful: List[str]


class EndOfSeasonCommandExecutor(BaseCommandExecutor[EndOfSeasonCommand, EndOfSeasonResult]):
    def __init__(
        self,
        publisher: Publisher,
        state_repo: StateRepository,
        league_repo: LeagueRepository,
        league_config_repo: LeagueConfigRepository,
        league_roster_repo: LeagueRosterRepository,
        season_summary_repo: SeasonSummaryRepository,
        public_repo: PublicRepository,
    ):
        self.publisher = publisher
        self.state_repo = state_repo
        self.league_repo = league_repo
        self.league_config_repo = league_config_repo
        self.league_roster_repo = league_roster_repo
        self.season_summary_repo = season_summary_repo
        self.public_repo = public_repo

    def on_execute(self, command: EndOfSeasonCommand) -> EndOfSeasonResult:

        if command.league_id:
            leagues = [self.league_repo.get(command.league_id)]
        else:
            leagues = self.league_repo.get_all()

        state = self.state_repo.get()
        season = state.current_season

        failed = []
        successful = []

        for league in leagues:
            if league.draft_state != DraftState.COMPLETE:
                continue

            try:
                schedule = self.league_config_repo.get_schedule_config(league.id)
                rosters = self.league_roster_repo.get_all(league.id)
                draft = self.league_config_repo.get_draft(league.id)
                summary = SeasonSummary.create_from_schedule(season, schedule, rosters, draft)

                self.season_summary_repo.set(league.id, summary)
                successful.append(league.id)
            except BaseException:
                failed.append(league.id)

        state.is_offseason = True

        scoreboard = Scoreboard(games={})
        self.public_repo.set_scoreboard(scoreboard)

        self.state_repo.set(state)

        return EndOfSeasonResult(command=command, failed=failed, successful=successful)
