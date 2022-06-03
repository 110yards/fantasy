

from typing import Dict, List, Optional

from fastapi import Depends
from pydantic import BaseModel
from api.app.core.logging import Logger
from api.app.core.rtdb_client import RTDBClient, create_rtdb_client
from api.app.domain.entities.player import Player
from api.app.domain.entities.player_league_season_score import PlayerLeagueSeasonScore, rank_player_seasons
from api.app.domain.entities.player_season import PlayerSeason
from api.app.domain.entities.scoring_settings import ScoringSettings
from api.app.domain.entities.stats import Stats
from api.app.domain.enums.draft_state import DraftState
from api.app.domain.repositories.league_config_repository import LeagueConfigRepository, create_league_config_repository
from api.app.domain.repositories.league_repository import LeagueRepository, create_league_repository
from api.app.domain.repositories.player_league_season_score_repository import PlayerLeagueSeasonScoreRepository, create_player_league_season_score_repository
from api.app.domain.repositories.player_repository import PlayerRepository, create_player_repository
from api.app.domain.repositories.player_season_repository import PlayerSeasonRepository, create_player_season_repository
from api.app.domain.repositories.public_repository import PublicRepository, create_public_repository


def create_player_list_service(
    league_repo: LeagueRepository = Depends(create_league_repository),
    player_season_repo: PlayerSeasonRepository = Depends(create_player_season_repository),
    league_config_repo: LeagueConfigRepository = Depends(create_league_config_repository),
    public_repo: PublicRepository = Depends(create_public_repository),
    player_repo: PlayerRepository = Depends(create_player_repository),
    player_season_score_repo: PlayerLeagueSeasonScoreRepository = Depends(create_player_league_season_score_repository),
    rtdb_client: RTDBClient = Depends(create_rtdb_client)
):
    return PlayerListService(
        league_repo=league_repo,
        player_season_repo=player_season_repo,
        league_config_repo=league_config_repo,
        public_repo=public_repo,
        player_repo=player_repo,
        player_season_score_repo=player_season_score_repo,
        rtdb_client=rtdb_client,
    )


class RankedPlayer(Player):
    rank: Optional[int]
    average: float = 0
    points: float = 0
    games_played: int = 0
    last_week_score: Optional[float]
    season_stats: Optional[Stats]


class CacheData(BaseModel):
    league_id: str
    season: int
    week: Optional[int]
    scoring_settings_hash: str
    players: List[RankedPlayer]


class PlayerListService:
    def __init__(
        self,
        league_repo: LeagueRepository,
        player_season_repo: PlayerSeasonRepository,
        league_config_repo: LeagueConfigRepository,
        public_repo: PublicRepository,
        player_repo: PlayerRepository,
        player_season_score_repo: PlayerLeagueSeasonScoreRepository,
        rtdb_client: RTDBClient,
    ):
        self.league_repo = league_repo
        self.player_season_repo = player_season_repo
        self.league_config_repo = league_config_repo
        self.public_repo = public_repo
        self.player_repo = player_repo
        self.player_season_score_repo = player_season_score_repo
        self.rtdb_client = rtdb_client

    def get_players_ref(self, league_id: str) -> str:
        league = self.league_repo.get(league_id)
        state = self.public_repo.get_state()

        if league.draft_state == DraftState.COMPLETE and league.season == state.current_season:
            return self.setup_current_ref(league_id, state.current_season, state.current_week)
        else:
            # last year, or old league
            return self.setup_draft_reference(league_id, state.current_season)

    def setup_draft_reference(self, league_id: str, current_season: int) -> str:
        current_season = current_season
        score_season = current_season

        score_season = current_season - 1
        if score_season == 2020:
            score_season = 2019  # :(

        scoring = self.league_config_repo.get_scoring_config(league_id)

        valid_cache = self._check_cache_scoring_hash(league_id, score_season)

        if valid_cache:
            return self._get_players_path(league_id, score_season)

        player_seasons = self._get_player_seasons(score_season)
        player_scores = self._calculate_scores(league_id, player_seasons, scoring)

        ranked_players = self._combine_result(current_season, player_seasons, player_scores)

        return self._save_result(league_id, score_season, None, ranked_players, scoring.hash)

    def setup_current_ref(self, league_id: str, current_season: int, current_week: int) -> List[PlayerLeagueSeasonScore]:

        # check cache for week first, it's going to change more often.
        valid_week_cache = self._check_cache_week(league_id, current_season, current_week)
        valid_scoring_cache = False
        scoring: ScoringSettings = None

        if valid_week_cache:
            scoring = self.league_config_repo.get_scoring_config(league_id)
            valid_scoring_cache = self._check_cache_scoring_hash(league_id, current_season, scoring)

        if valid_week_cache and valid_scoring_cache:
            return self._get_players_path(league_id, current_season)

        player_seasons = self._get_player_seasons(current_season)
        player_scores = self.player_season_score_repo.get_all(league_id)
        player_scores = {x.id: x for x in player_scores}

        ranked_players = self._combine_result(current_season, player_seasons, player_scores)

        if not scoring:
            scoring = self.league_config_repo.get_scoring_config(league_id)

        return self._save_result(league_id, current_season, current_week, ranked_players, scoring.hash)

    def _check_cache_scoring_hash(self, league_id: str, season: int, scoring: ScoringSettings) -> bool:
        path = f"{self._get_data_path(league_id, season)}/scoring_settings_hash"
        cache_hash = self.rtdb_client.get(path)

        if cache_hash:
            Logger.debug("Cached scoring hash found")
            if cache_hash == scoring.hash:
                Logger.debug("Valid cache hit")
                return True
            else:
                Logger.debug("Scoring has changed, cache is invalid")
        else:
            Logger.debug("No cached scoring hash found")

        return False

    def _check_cache_week(self, league_id: str, season: int, current_week: int) -> bool:
        path = f"{self._get_data_path(league_id, season)}/week"
        cache_week = self.rtdb_client.get(path)

        if cache_week:
            Logger.debug(f"Cache found for week {cache_week}")
            if cache_week == current_week:
                Logger.debug("Cache is valid for week")
                return True
            else:
                Logger.debug("Week has changed, cache is invalid")
        else:
            Logger.debug("No player cache for league")

        return False

    def _get_data_path(self, league_id: str, season: int) -> str:
        return f"player_lists/{season}/{league_id}"

    def _get_players_path(self, league_id: str, season: int) -> str:
        return f"{self._get_data_path(league_id, season)}/players"

    def _save_result(
            self,
            league_id: str,
            season: int,
            week: Optional[int],
            ranked_players: List[RankedPlayer],
            scoring_hash: str,
    ) -> str:
        data = CacheData(league_id=league_id, season=season, week=week, players=ranked_players, scoring_settings_hash=scoring_hash)

        path = self._get_data_path(league_id, season)
        self.rtdb_client.set(path, data.dict())
        return f"{path}/players"

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

    def _calculate_scores(self, league_id: str, player_seasons: Dict[str, PlayerSeason], scoring: ScoringSettings) -> Dict[str, PlayerLeagueSeasonScore]:

        if not scoring:
            Logger.error(f"No scoring configuration found for league '{league_id}'")
            return None

        player_season_scores: List[PlayerLeagueSeasonScore] = []

        for player_season in player_seasons.values():
            player_season_score = PlayerLeagueSeasonScore.create(player_season.id, player_season, scoring, 0)
            player_season_scores.append(player_season_score)

        rank_player_seasons(player_season_scores)

        return {x.id: x for x in player_season_scores}
