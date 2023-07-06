from typing import Any, Optional

from app.yards_py.core.logging import Logger
from app.yards_py.domain.entities.league import League
from app.yards_py.domain.entities.state import State
from app.yards_py.domain.repositories.league_repository import LeagueRepository, create_league_repository
from app.yards_py.domain.repositories.public_repository import PublicRepository, create_public_repository
from app.yards_py.domain.repositories.user_archive_league_repository import UserArchiveLeagueRepository, create_user_archive_league_repository
from app.yards_py.domain.repositories.user_league_repository import UserLeagueRepository, create_user_league_repository
from app.yards_py.domain.repositories.user_repository import UserRepository, create_user_repository
from fastapi import Depends
from pydantic.main import BaseModel


class StartNextSeasonResult(BaseModel):
    success: bool
    error: Optional[str]
    state: Optional[State]
    # scoreboard: Optional[Scoreboard]
    # opponents: Optional[Opponents]


class StartNextSeasonService:
    def __init__(
        self,
        public_repo: PublicRepository,
        league_repo: LeagueRepository,
        user_league_repo: UserLeagueRepository,
        user_archive_league_repo: UserArchiveLeagueRepository,
        user_repo: UserRepository,
    ):
        self.public_repo = public_repo
        self.league_repo = league_repo
        self.user_league_repo = user_league_repo
        self.user_archive_league_repo = user_archive_league_repo
        self.user_repo = user_repo

    def run_workflow(self, target_season: Optional[int]) -> Any:
        Logger.info("Start next season workflow started")

        # update season / week (state)
        Logger.info("Fetching state")
        state = self.public_repo.get_state()

        if target_season:
            state.current_season = target_season
        else:
            state.current_season += 1

        completed_season = target_season - 1

        state.current_week = 1
        state.is_offseason = False
        state.waivers_end = None
        state.waivers_active = False

        # # update schedule
        # # not strictly necessary to include final, but maybe helpful for testing with old seasons
        # Logger.info("Updating schedule")
        # command = UpdateScheduleCommand(include_final=True, season=state.current_season)
        # schedule_result = self.update_schedule_command_executor.execute(command)

        # if not schedule_result.success:
        #     return StartNextSeasonResult(success=False, error=schedule_result.error)

        # # update scoreboard
        # Logger.info("Updating scoreboard")
        # week_one_games = [game for game in schedule_result.games if game.week == 1 and game.event_type.event_type_id == EVENT_TYPE_REGULAR]
        # scoreboard = Scoreboard.create(week_one_games)  # kinda sketchy, relies on ScheduledGame being similar enough to Game

        # # update opponents
        # opponents = Opponents.from_scheduled_games(week_one_games)

        # save state new state
        Logger.info("Saving state")
        self.public_repo.set_state(state)
        # self.public_repo.set_scoreboard(scoreboard)
        # self.public_repo.set_opponents(opponents)

        leagues = self.league_repo.get_all()
        Logger.info("Archiving leagues")
        for league in leagues:
            if (league.is_active or league.has_completed_season) and league.season == completed_season:
                self.archive_league(league)
            else:
                self.cleanup_league(league)

        # Erase all league previews
        Logger.info("Erasing league previews")
        for user in self.user_repo.get_all():
            for league in self.user_league_repo.get_leagues(user.id):
                self.user_league_repo.delete(user.id, league.id)

        return StartNextSeasonResult(
            success=True,
            state=state,
            # scoreboard=scoreboard,
            # opponents=opponents,
        )

    def archive_league(self, league: League):
        """Preserve a link to this link which the commissioner can access to renew for future seasons"""
        league_preview = self.user_league_repo.get(league.commissioner_id, league.id)
        self.user_archive_league_repo.set(league.commissioner_id, league_preview)

    def cleanup_league(self, league: League):
        """Remove an inactive league from the system (maybe in the future?)"""
        pass


def create_start_next_season_service(
    public_repo: PublicRepository = Depends(create_public_repository),
    league_repo: LeagueRepository = Depends(create_league_repository),
    user_league_repo: UserLeagueRepository = Depends(create_user_league_repository),
    user_archive_league_repo: UserArchiveLeagueRepository = Depends(create_user_archive_league_repository),
    user_repo: UserRepository = Depends(create_user_repository),
):
    return StartNextSeasonService(
        public_repo=public_repo,
        league_repo=league_repo,
        user_league_repo=user_league_repo,
        user_archive_league_repo=user_archive_league_repo,
        user_repo=user_repo,
    )
