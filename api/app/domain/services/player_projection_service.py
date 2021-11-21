

from api.app.domain.entities.team import Team
from api.app.domain.repositories.public_repository import PublicRepository, create_public_repository
from api.app.domain.entities.player import STATUS_ACTIVE
from api.app.config.config import Settings, get_settings
from api.app.domain.repositories.player_repository import PlayerRepository, create_player_repository

from fastapi.param_functions import Depends
from api.app.domain.repositories.league_player_score_repository import LeaguePlayerScoreRepository, create_league_player_score_repository


def create_player_projection_service(
    settings: Settings = Depends(get_settings),
    player_repo: PlayerRepository = Depends(create_player_repository),
    player_score_repo: LeaguePlayerScoreRepository = Depends(create_league_player_score_repository),
    public_repo: PublicRepository = Depends(create_public_repository),
):
    return PlayerProjectionService(settings.current_season, player_repo, player_score_repo, public_repo)


class PlayerProjectionService:
    def __init__(
        self,
        season: int,
        player_repo: PlayerRepository,
        player_score_repo: LeaguePlayerScoreRepository,
        public_repo: PublicRepository,
    ):
        self.season = season
        self.player_repo = player_repo
        self.player_score_repo = player_score_repo
        self.public_repo = public_repo

    def get_projection(self, league_id: str, player_id: str) -> float:
        player = self.player_repo.get(self.season, player_id)

        if (player.status_current != STATUS_ACTIVE):
            return 0.0

        if (player.team.id == Team.free_agent().id):
            return 0.0

        opponents = self.public_repo.get_opponents()
        if opponents.is_team_on_bye(player.team):
            return 0.0

        player_score = self.player_score_repo.get(league_id, player_id)
        projection = player_score.average if player_score else 0.0  # TODO: apply some opponent adjustments to this

        return round(projection, 2)
