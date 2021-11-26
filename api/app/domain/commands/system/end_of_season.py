

from api.app.domain.entities.season_summary import SeasonSummary
from api.app.domain.enums.draft_state import DraftState
from api.app.domain.repositories.league_config_repository import LeagueConfigRepository, create_league_config_repository
from api.app.domain.repositories.league_repository import LeagueRepository, create_league_repository
from api.app.domain.repositories.league_roster_repository import LeagueRosterRepository, create_league_roster_repository
from api.app.domain.repositories.season_summary_repository import SeasonSummaryRepository, create_season_summary_repository
from api.app.domain.repositories.state_repository import StateRepository, create_state_repository
from typing import Optional
from api.app.core.publisher import Publisher, create_publisher
from fastapi import Depends
from api.app.core.annotate_args import annotate_args
from api.app.core.base_command_executor import BaseCommand, BaseCommandResult, BaseCommandExecutor


def create_end_of_season_command_executor(
    publisher: Publisher = Depends(create_publisher),
    state_repo: StateRepository = Depends(create_state_repository),
    league_repo: LeagueRepository = Depends(create_league_repository),
    league_config_repo: LeagueConfigRepository = Depends(create_league_config_repository),
    league_roster_repo: LeagueRosterRepository = Depends(create_league_roster_repository),
    season_summary_repo: SeasonSummaryRepository = Depends(create_season_summary_repository),
):
    return EndOfSeasonCommandExecutor(
        publisher=publisher,
        state_repo=state_repo,
        league_repo=league_repo,
        league_config_repo=league_config_repo,
        league_roster_repo=league_roster_repo,
        season_summary_repo=season_summary_repo,
    )


@annotate_args
class EndOfSeasonCommand(BaseCommand):
    league_id: Optional[str]


@annotate_args
class EndOfSeasonResult(BaseCommandResult[EndOfSeasonCommand]):
    pass


class EndOfSeasonCommandExecutor(BaseCommandExecutor[EndOfSeasonCommand, EndOfSeasonResult]):
    def __init__(
        self,
        publisher: Publisher,
        state_repo: StateRepository,
        league_repo: LeagueRepository,
        league_config_repo: LeagueConfigRepository,
        league_roster_repo: LeagueRosterRepository,
        season_summary_repo: SeasonSummaryRepository,
    ):
        self.publisher = publisher
        self.state_repo = state_repo
        self.league_repo = league_repo
        self.league_config_repo = league_config_repo
        self.league_roster_repo = league_roster_repo
        self.season_summary_repo = season_summary_repo

    def on_execute(self, command: EndOfSeasonCommand) -> EndOfSeasonResult:

        if command.league_id:
            leagues = [self.league_repo.get(command.league_id)]
        else:
            leagues = self.league_repo.get_all()

        state = self.state_repo.get()
        season = state.current_season

        # For all leagues which have drafted
        for league in leagues:
            if league.draft_state != DraftState.COMPLETE:
                continue

            schedule = self.league_config_repo.get_schedule_config(league.id)
            rosters = self.league_roster_repo.get_all(league.id)
            draft = self.league_config_repo.get_draft(league.id)
            summary = SeasonSummary.create_from_schedule(season, schedule, rosters, draft)

            self.season_summary_repo.set(league.id, summary)

        state.is_offseason = True
        self.state_repo.set(state)

        return EndOfSeasonResult(command=command)
