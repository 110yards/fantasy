from api.app.domain.entities.league_player_score import LeaguePlayerScore
from api.app.domain.repositories.league_player_score_repository import LeaguePlayerScoreRepository, create_league_player_score_repository
from api.app.config.settings import Settings, get_settings
from api.app.domain.repositories.public_repository import PublicRepository, create_public_repository
from typing import Dict

from api.app.core.firestore_proxy import Query
from api.app.core.batch import create_batches
from fastapi.param_functions import Depends
from api.app.domain.repositories.league_roster_repository import LeagueRosterRepository, create_league_roster_repository


def create_roster_score_service(
    settings: Settings = Depends(get_settings),
    roster_repo: LeagueRosterRepository = Depends(create_league_roster_repository),
    score_repo: LeaguePlayerScoreRepository = Depends(create_league_player_score_repository),
    public_repo: PublicRepository = Depends(create_public_repository),
):
    return RosterScoreService(settings.current_season, roster_repo, score_repo, public_repo,)


class RosterScoreService:
    def __init__(
        self,
        season: int,
        roster_repo: LeagueRosterRepository,
        score_repo: LeaguePlayerScoreRepository,
        public_repo: PublicRepository,
    ):
        self.season = season
        self.roster_repo = roster_repo
        self.score_repo = score_repo
        self.public_repo = public_repo

    def get_score(self, league_id: str, roster_id: str) -> Dict[str, float]:
        roster = self.roster_repo.get(league_id, roster_id)
        if not roster:
            return {
                "projection": 0,
                "score": 0,
            }
        scoreboard = self.public_repo.get_scoreboard()

        player_ids = [p.player.id for p in roster.positions.values() if p.position_type.is_starting_position_type() and p.player]

        batches = create_batches(player_ids, 10)

        player_scores: Dict[str, LeaguePlayerScore] = {}
        for batch in batches:
            query = Query("id", "in", batch)
            batch_scores = self.score_repo.where(league_id, query)
            for score in batch_scores:
                player_scores[score.id] = score

        projection = 0.0
        score = 0.0
        for position in roster.positions.values():
            if position.position_type.is_starting_position_type() and position.player:
                player_score: LeaguePlayerScore = player_scores.get(position.player.id, None)

                if player_score:
                    for game_id in scoreboard.games:
                        if game_id in player_score.game_scores:
                            score += player_score.game_scores[game_id].total_score
                    projection += player_score.average if player_score else 0

        return {
            "projection": round(projection, 2),
            "score": round(score, 2),
        }
