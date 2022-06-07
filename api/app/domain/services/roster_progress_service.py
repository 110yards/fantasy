

from yards_py.domain.entities.event_status import EVENT_STATUS_FINAL, EVENT_STATUS_IN_PROGRESS, EVENT_STATUS_PRE_GAME
from api.app.domain.repositories.public_repository import PublicRepository, create_public_repository

from fastapi.param_functions import Depends
from pydantic.main import BaseModel
from api.app.domain.repositories.league_roster_repository import LeagueRosterRepository, create_league_roster_repository


def create_roster_progress_service(
    roster_repo: LeagueRosterRepository = Depends(create_league_roster_repository),
    public_repo: PublicRepository = Depends(create_public_repository),
):
    return ProgressService(roster_repo, public_repo)


class ProgressRequest(BaseModel):
    league_id: str
    roster_id: str


class ProgressService:
    def __init__(
        self,
        roster_repo: LeagueRosterRepository,
        public_repo: PublicRepository
    ):
        self.roster_repo = roster_repo
        self.public_repo = public_repo

    def get_projection(self, league_id: str, roster_id: str) -> float:
        roster = self.roster_repo.get(league_id, roster_id)
        scoreboard = self.public_repo.get_scoreboard()

        total = 0
        in_progress = 0
        completed = 0

        for position in roster.positions.values():
            if position.position_type.is_starting_position_type() and position.player:

                game = scoreboard.get_game_for_team(position.player.team.id)

                if game and game.event_status.event_status_id == EVENT_STATUS_PRE_GAME:
                    total += 1

                if game and game.event_status.event_status_id == EVENT_STATUS_IN_PROGRESS:
                    total += 1
                    in_progress += 1

                if game and game.event_status.event_status_id == EVENT_STATUS_FINAL:
                    total += 1
                    completed += 1

        return {
            "total": total,
            "in_progress": in_progress,
            "completed": completed,
            "percent_complete": completed * 100 / total if total else 0,
            "remaining": total - completed
        }
