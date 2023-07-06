from datetime import datetime, timezone
from typing import Dict, List, Optional

from dateutil import parser
from fastapi import Depends
from pydantic import BaseModel

from app.domain.enums.draft_state import DraftState
from app.domain.repositories.league_config_repository import LeagueConfigRepository, create_league_config_repository
from app.domain.repositories.league_repository import LeagueRepository, create_league_repository
from app.domain.repositories.player_league_season_score_repository import PlayerLeagueSeasonScoreRepository, create_player_league_season_score_repository
from app.domain.repositories.player_repository import PlayerRepository, create_player_repository
from app.domain.repositories.player_season_repository import PlayerSeasonRepository, create_player_season_repository
from app.domain.repositories.public_repository import PublicRepository, create_public_repository
from app.yards_py.core.logging import Logger
from app.yards_py.core.rtdb_client import RTDBClient, create_rtdb_client
from app.yards_py.domain.entities.league import League
from app.yards_py.domain.entities.player import Player
from app.yards_py.domain.entities.player_league_season_score import PlayerLeagueSeasonScore, rank_player_seasons
from app.yards_py.domain.entities.player_season import PlayerSeason
from app.yards_py.domain.entities.scoring_settings import ScoringSettings
from app.yards_py.domain.entities.stats import Stats
from app.yards_py.domain.repositories.state_repository import StateRepository, create_state_repository


def create_player_list_service(
    league_repo: LeagueRepository = Depends(create_league_repository),
    player_season_repo: PlayerSeasonRepository = Depends(create_player_season_repository),
    league_config_repo: LeagueConfigRepository = Depends(create_league_config_repository),
    public_repo: PublicRepository = Depends(create_public_repository),
    player_repo: PlayerRepository = Depends(create_player_repository),
    player_season_score_repo: PlayerLeagueSeasonScoreRepository = Depends(create_player_league_season_score_repository),
    rtdb_client: RTDBClient = Depends(create_rtdb_client),
    state_repo: StateRepository = Depends(create_state_repository),
):
    return PlayerListService(
        league_repo=league_repo,
        player_season_repo=player_season_repo,
        league_config_repo=league_config_repo,
        public_repo=public_repo,
        player_repo=player_repo,
        player_season_score_repo=player_season_score_repo,
        rtdb_client=rtdb_client,
        state_repo=state_repo,
    )


class RankedPlayer(Player):
    rank: Optional[int]
    average: float = 0
    points: float = 0
    games_played: int = 0
    last_week_score: Optional[float] | Optional[int]
    season_stats: Optional[Stats]


class CacheData(BaseModel):
    league_id: str
    season: int
    scoring_settings_hash: str
    players: List[RankedPlayer]
    recalc_date: Optional[int]
    last_player_update: Optional[datetime]
    generated_at: datetime


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
        state_repo: StateRepository,
    ):
        self.league_repo = league_repo
        self.player_season_repo = player_season_repo
        self.league_config_repo = league_config_repo
        self.public_repo = public_repo
        self.player_repo = player_repo
        self.player_season_score_repo = player_season_score_repo
        self.rtdb_client = rtdb_client
        self.state_repo = state_repo

    def get_players_ref(self, league_id: str) -> Optional[str]:
        league = self.league_repo.get(league_id)

        if not league:
            return None

        state = self.public_repo.get_state()

        if league.draft_state == DraftState.COMPLETE and league.season == state.current_season:
            return self.setup_current_ref(league, state.current_season, league.last_season_recalc)
        else:
            # last year, or old league
            return self.setup_draft_reference(league, state.current_season)

    def setup_draft_reference(self, league: League, current_season: int) -> str:
        league_id = league.id
        current_season = current_season
        score_season = current_season

        score_season = current_season - 1
        if score_season == 2020:
            score_season = 2019  # :(

        scoring = self.league_config_repo.get_scoring_config(league_id)

        valid_cache = self._check_cache_validity(league, score_season, scoring)

        if valid_cache:
            return self._get_players_path(league_id, score_season)

        player_seasons = self._get_player_seasons(score_season)
        player_scores = self._calculate_draft_scores(league_id, player_seasons, scoring)

        ranked_players = self._combine_result(current_season, player_seasons, player_scores)

        return self._save_result(league_id, score_season, None, ranked_players, scoring.hash)

    def setup_current_ref(self, league: League, current_season: int, last_recalc_date: Optional[int]) -> List[PlayerLeagueSeasonScore]:
        league_id = league.id
        # weird bug from pydantic causes the recalc to be deserialized as a datetime instead of an int
        if isinstance(last_recalc_date, datetime):
            last_recalc_date = last_recalc_date.timestamp()

        scoring = self.league_config_repo.get_scoring_config(league_id)
        valid_cache = self._check_cache_validity(league, current_season, scoring)

        if valid_cache:
            return self._get_players_path(league_id, current_season)

        # TODO: combine players with seasons (which don't exist)
        player_seasons = self._get_player_seasons(current_season)
        player_scores = self.player_season_score_repo.get_all(league_id)
        player_scores = {x.id: x for x in player_scores}

        ranked_players = self._combine_result(current_season, player_seasons, player_scores)

        if not scoring:
            scoring = self.league_config_repo.get_scoring_config(league_id)

        return self._save_result(league_id, current_season, last_recalc_date, ranked_players, scoring.hash)

    def _check_cache_validity(self, league: League, season: int, scoring: ScoringSettings) -> bool:
        league_id = league.id

        path = f"{self._get_data_path(league_id, season)}/generated_at"

        generated_at = self.rtdb_client.get(path)

        if isinstance(generated_at, int):
            generated_at = datetime.fromtimestamp(generated_at)

        if isinstance(generated_at, str):
            generated_at = parser.isoparse(generated_at)

        if generated_at is None or league.last_season_recalc is None:
            Logger.debug("No cache found")
            return False

        last_season_recalc = league.last_season_recalc
        if isinstance(last_season_recalc, int):
            last_season_recalc = datetime.fromtimestamp(last_season_recalc).replace(tzinfo=timezone.utc)

        if generated_at < last_season_recalc:
            Logger.debug("Cache is out of date (recalc)")
            return False

        last_player_update = self.player_repo.get_last_updated()

        if last_player_update > generated_at:
            Logger.debug("Cache is out of date (player update)")
            return False

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

    def _check_current_cache(self, league_id: str, season: int, last_league_recalc: Optional[int]) -> bool:
        path = f"{self._get_data_path(league_id, season)}/recalc_date"
        recalc_date = self.rtdb_client.get(path)

        if recalc_date:
            Logger.debug(f"Cache found with recalc date {recalc_date}")
            if not last_league_recalc or last_league_recalc <= recalc_date:
                Logger.debug("Valid cache hit")
                return True
            else:
                Logger.debug("Scores have been recalced, cache is invalid")
        else:
            Logger.debug("No player cache for league")

        return False

    def _get_data_path(self, league_id: str, season: int) -> str:
        return f"league/{league_id}/player_list/{season}"

    def _get_players_path(self, league_id: str, season: int) -> str:
        return f"{self._get_data_path(league_id, season)}/players"

    def _save_result(self, league_id: str, season: int, last_recalc_date: Optional[datetime], ranked_players: List[RankedPlayer], scoring_hash: str) -> str:
        if not last_recalc_date:
            last_recalc_date = datetime.now().timestamp()

        data = CacheData(
            league_id=league_id,
            season=season,
            players=ranked_players,
            scoring_settings_hash=scoring_hash,
            recalc_date=last_recalc_date,
            generated_at=datetime.now().astimezone(tz=timezone.utc).isoformat(),
        )

        path = self._get_data_path(league_id, season)

        for player in ranked_players:
            player.birth_date = None
            player.last_updated = None

        data = data.dict()

        data["generated_at"] = data["generated_at"].isoformat()
        self.rtdb_client.set(path, data)
        return f"{path}/players"

    def _combine_result(
        self, current_season: int, player_seasons: Dict[str, PlayerSeason], player_scores: Dict[str, PlayerLeagueSeasonScore]
    ) -> List[RankedPlayer]:
        players = self.player_repo.get_all(current_season)  # for draft we still only care about the current player list

        ranked_players: List[RankedPlayer] = []

        last_rank = len(players)

        for player in players:
            ranked_player = RankedPlayer.parse_obj(player.dict())

            season = player_seasons.get(player.player_id, None)
            season_score = player_scores.get(player.player_id, None)
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

    def _calculate_draft_scores(self, league_id: str, player_seasons: Dict[str, PlayerSeason], scoring: ScoringSettings) -> Dict[str, PlayerLeagueSeasonScore]:
        if not scoring:
            Logger.error(f"No scoring configuration found for league '{league_id}'")
            return None

        player_season_scores: List[PlayerLeagueSeasonScore] = []

        for player_season in player_seasons.values():
            player_season_score = PlayerLeagueSeasonScore.create(player_season.id, player_season, scoring, 0)
            player_season_scores.append(player_season_score)

        rank_player_seasons(player_season_scores)

        return {x.id: x for x in player_season_scores}
