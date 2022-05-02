

from typing import Dict, List, Optional

from fastapi import Depends
from api.app.core.logging import Logger
from api.app.domain.entities.player import Player
from api.app.domain.entities.player_league_season_score import PlayerLeagueSeasonScore, rank_player_seasons
from api.app.domain.entities.player_season import PlayerSeason
from api.app.domain.entities.stats import Stats
from api.app.domain.repositories.league_config_repository import LeagueConfigRepository, create_league_config_repository
from api.app.domain.repositories.player_league_season_score_repository import PlayerLeagueSeasonScoreRepository, create_player_league_season_score_repository
from api.app.domain.repositories.player_repository import PlayerRepository, create_player_repository
from api.app.domain.repositories.player_season_repository import PlayerSeasonRepository, create_player_season_repository
from api.app.domain.repositories.public_repository import PublicRepository, create_public_repository


def create_player_list_service(
    player_season_repo: PlayerSeasonRepository = Depends(create_player_season_repository),
    league_config_repo: LeagueConfigRepository = Depends(create_league_config_repository),
    public_repo: PublicRepository = Depends(create_public_repository),
    player_repo: PlayerRepository = Depends(create_player_repository),
    player_season_score_repo: PlayerLeagueSeasonScoreRepository = Depends(create_player_league_season_score_repository),
):
    return PlayerListService(
        player_season_repo=player_season_repo,
        league_config_repo=league_config_repo,
        public_repo=public_repo,
        player_repo=player_repo,
        player_season_score_repo=player_season_score_repo,
    )


class RankedPlayer(Player):
    rank: Optional[int]
    average: float = 0
    points: float = 0
    games_played: int = 0
    last_week_score: Optional[float]
    season_stats: Optional[Stats]


class PlayerListService:
    def __init__(
        self,
        player_season_repo: PlayerSeasonRepository,
        league_config_repo: LeagueConfigRepository,
        public_repo: PublicRepository,
        player_repo: PlayerRepository,
        player_season_score_repo: PlayerLeagueSeasonScoreRepository
    ):
        self.player_season_repo = player_season_repo
        self.league_config_repo = league_config_repo
        self.public_repo = public_repo
        self.player_repo = player_repo
        self.player_season_score_repo = player_season_score_repo

    def get_draft_player_list(self, league_id: str) -> List[RankedPlayer]:
        state = self.public_repo.get_state()
        current_season = state.current_season
        score_season = state.current_season

        score_season = state.current_season - 1
        if score_season == 2020:
            score_season = 2019  # :(

        player_seasons = self._get_player_seasons(score_season)
        player_scores = self._calculate_scores(league_id, player_seasons)

        return self._combine_result(current_season, player_seasons, player_scores)

    def get_current_player_list(self, league_id: str) -> List[PlayerLeagueSeasonScore]:
        state = self.public_repo.get_state()
        current_season = state.current_season

        player_seasons = self._get_player_seasons(current_season)
        player_scores = self.player_season_score_repo.get_all(league_id)
        player_scores = {x.id: x for x in player_scores}

        return self._combine_result(current_season, player_seasons, player_scores)

    def _combine_result(
        self,
        current_season: int,
        player_seasons: Dict[str, PlayerSeason],
        player_scores: Dict[str, PlayerLeagueSeasonScore]
    ) -> List[RankedPlayer]:

        players = self.player_repo.get_all(current_season)  # for draft we still only care about the current player list

        ranked_players: List[RankedPlayer] = []

        last_rank = len(players)

        for player in players:
            ranked_player = RankedPlayer.parse_obj(player.dict())

            season = player_seasons.get(player.id, None)
            season_score = player_scores.get(player.id, None)
            if season and season_score:
                ranked_player.rank = season_score.rank
                ranked_player.average = season_score.average_score
                ranked_player.points = season_score.total_score
                ranked_player.last_week_score = season_score.last_week_score
                ranked_player.games_played = season.games_played
                ranked_player.season_stats = season.stats
            else:
                ranked_player.rank = last_rank

            ranked_players.append(ranked_player)

        return ranked_players

    def _get_player_seasons(self, score_season: int) -> Dict[str, PlayerSeason]:
        player_seasons = self.player_season_repo.get_all(score_season)
        return {x.id: x for x in player_seasons}

    def _calculate_scores(self, league_id: str, player_seasons: Dict[str, PlayerSeason]) -> Dict[str, PlayerLeagueSeasonScore]:
        scoring = self.league_config_repo.get_scoring_config(league_id)

        if not scoring:
            Logger.error(f"No scoring configuration found for league '{league_id}'")
            return None

        player_season_scores: List[PlayerLeagueSeasonScore] = []

        for player_season in player_seasons.values():
            player_season_score = PlayerLeagueSeasonScore.create(player_season.id, player_season, scoring, 0)
            player_season_scores.append(player_season_score)

        rank_player_seasons(player_season_scores)

        return {x.id: x for x in player_season_scores}
