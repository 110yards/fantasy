from typing import Dict, List

from fastapi.param_functions import Depends

from app.domain.repositories.player_league_season_score_repository import PlayerLeagueSeasonScoreRepository, create_player_league_season_score_repository
from app.domain.repositories.player_repository import PlayerRepository, create_player_repository
from app.domain.repositories.public_repository import PublicRepository, create_public_repository
from app.domain.repositories.state_repository import StateRepository, create_state_repository
from app.yards_py.core.batch import create_batches
from app.yards_py.core.firestore_proxy import Query
from app.yards_py.domain.entities.player import Player
from app.yards_py.domain.entities.player_league_season_score import PlayerLeagueSeasonScore

from ...yards_py.domain.entities.scoreboard import Scoreboard


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
        player = self.player_repo.get(player_id)

        if not player:
            return 0.0

        projections = self.get_projections(league_id, [player])
        return projections.get(player.player_id, 0.0)

    def get_projections(self, league_id: str, players: List[Player]) -> Dict[str, float]:
        scoreboard = self.public_repo.get_scoreboard()

        player_ids = [p.player_id for p in players if p]
        batches = create_batches(player_ids, 10)

        player_scores: Dict[str, PlayerLeagueSeasonScore] = {}
        for batch in batches:
            query = Query("id", "in", batch)
            batch_scores = self.player_score_repo.where(league_id, query)
            for score in batch_scores:
                player_scores[score.id] = score

        projections = {}
        for player in players:
            player_score = player_scores.get(player.player_id, None)  # TODO: last year's average if week 1
            projections[player.player_id] = self.calculate(scoreboard, player, player_score)

        return projections

    def calculate(self, scoreboard: Scoreboard, player: Player, player_score: PlayerLeagueSeasonScore) -> float:
        if player.likely_out_for_game():
            return 0.0

        if player.is_free_agent():
            return 0.0

        if scoreboard.is_team_on_bye(player.team_abbr):
            return 0.0

        if not player_score:
            return 0.0

        projection = player_score.average_score if player_score else 0.0  # TODO: apply some opponent adjustments to this

        return round(projection, 2)
