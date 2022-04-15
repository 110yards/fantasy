

from typing import Dict, List
from api.app.core.batch import create_batches
from api.app.core.firestore_proxy import Query
from api.app.domain.entities.opponents import Opponents
from api.app.domain.entities.team import Team
from api.app.domain.repositories.public_repository import PublicRepository, create_public_repository
from api.app.domain.entities.player import STATUS_ACTIVE, Player, PlayerLeagueSeasonScore
from api.app.domain.repositories.player_repository import PlayerRepository, create_player_repository

from fastapi.param_functions import Depends
from api.app.domain.repositories.player_league_season_score_repository import PlayerLeagueSeasonScoreRepository, create_player_league_season_score_repository
from api.app.domain.repositories.state_repository import StateRepository, create_state_repository


def create_player_projection_service(
    state_repo: StateRepository = Depends(create_state_repository),
    player_repo: PlayerRepository = Depends(create_player_repository),
    player_score_repo: PlayerLeagueSeasonScoreRepository = Depends(create_player_league_season_score_repository),
    public_repo: PublicRepository = Depends(create_public_repository),
):
    return PlayerProjectionService(state_repo, player_repo, player_score_repo, public_repo)


class PlayerProjectionService:
    def __init__(
        self,
        state_repo: StateRepository,
        player_repo: PlayerRepository,
        player_score_repo: PlayerLeagueSeasonScoreRepository,
        public_repo: PublicRepository,
    ):
        self.state_repo = state_repo
        self.player_repo = player_repo
        self.player_score_repo = player_score_repo
        self.public_repo = public_repo

    def get_projection(self, league_id: str, player_id: str) -> float:
        state = self.state_repo.get()

        player = self.player_repo.get(state.current_season, player_id)

        projections = self.get_projections(league_id, [player])
        return projections.get(player.id, 0.0)

    def get_projections(self, league_id: str, players: List[Player]) -> Dict[str, float]:
        opponents = self.public_repo.get_opponents()

        player_ids = [p.id for p in players]
        batches = create_batches(player_ids, 10)

        player_scores: Dict[str, PlayerLeagueSeasonScore] = {}
        for batch in batches:
            query = Query("id", "in", batch)
            batch_scores = self.player_score_repo.where(league_id, query)
            for score in batch_scores:
                player_scores[score.id] = score

        projections = {}
        for player in players:
            player_score = player_scores.get(player.id, None)  # TODO: last year's average if week 1
            projections[player.id] = self.calculate(opponents, player, player_score)

        return projections

    def calculate(self, opponents: Opponents, player: Player, player_score: PlayerLeagueSeasonScore) -> float:
        if (player.status_current != STATUS_ACTIVE):
            return 0.0

        if (player.team.id == Team.free_agent().id):
            return 0.0

        if opponents.is_team_on_bye(player.team):
            return 0.0

        if not player_score:
            return 0.0

        projection = player_score.average_score if player_score else 0.0  # TODO: apply some opponent adjustments to this

        return round(projection, 2)
