
from fastapi.param_functions import Depends
from api.app.domain.repositories.league_roster_repository import LeagueRosterRepository, create_league_roster_repository
from api.app.domain.repositories.state_repository import StateRepository, create_state_repository
from api.app.domain.services.player_projection_service import PlayerProjectionService, create_player_projection_service


def create_roster_projection_service(
    state_repo: StateRepository = Depends(create_state_repository),
    roster_repo: LeagueRosterRepository = Depends(create_league_roster_repository),
    player_projection_service: PlayerProjectionService = Depends(create_player_projection_service),
):
    return RosterProjectionService(state_repo, roster_repo, player_projection_service)


class RosterProjectionService:
    def __init__(
        self,
        state_repo: StateRepository,
        roster_repo: LeagueRosterRepository,
        player_projection_service: PlayerProjectionService,
    ):
        self.state_repo = state_repo
        self.roster_repo = roster_repo
        self.player_projection_service = player_projection_service

    def get_projection(self, league_id: str, roster_id: str) -> float:
        roster = self.roster_repo.get(league_id, roster_id)
        if not roster:
            return 0.0

        players = [p.player for p in roster.positions.values() if p.position_type.is_starting_position_type() and p.player]

        projections = self.player_projection_service.get_projections(league_id, players)

        projection = sum(projections.values())

        return projection
