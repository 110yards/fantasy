from datetime import datetime, timezone
from typing import List, Optional

from app.core.annotate_args import annotate_args
from app.core.base_command_executor import BaseCommand, BaseCommandExecutor, BaseCommandResult
from app.domain.entities.player_league_season_score import PlayerLeagueSeasonScore, rank_player_seasons
from app.domain.repositories.league_config_repository import LeagueConfigRepository, create_league_config_repository
from app.domain.repositories.league_repository import LeagueRepository, create_league_repository
from app.domain.repositories.player_league_season_score_repository import (
    PlayerLeagueSeasonScoreRepository,
    create_player_league_season_score_repository,
)
from app.domain.repositories.player_repository import PlayerRepository, create_player_repository
from app.domain.repositories.player_season_repository import PlayerSeasonRepository, create_player_season_repository
from app.domain.repositories.public_repository import PublicRepository, create_public_repository
from fastapi import Depends
from firebase_admin import firestore


def create_calculate_season_score_command_executor(
    league_config_repo: LeagueConfigRepository = Depends(create_league_config_repository),
    player_score_repo: PlayerLeagueSeasonScoreRepository = Depends(create_player_league_season_score_repository),
    player_repo: PlayerRepository = Depends(create_player_repository),
    public_repo: PublicRepository = Depends(create_public_repository),
    player_season_repo: PlayerSeasonRepository = Depends(create_player_season_repository),
    league_repo: LeagueRepository = Depends(create_league_repository),
):
    return CalculateSeasonScoreCommandExecutor(league_config_repo, player_score_repo, player_repo, public_repo, player_season_repo, league_repo)


@annotate_args
class CalculateSeasonScoreCommand(BaseCommand):
    league_id: Optional[str] = None
    season: Optional[int] = None


@annotate_args
class CalculateSeasonScoreResult(BaseCommandResult[CalculateSeasonScoreCommand]):
    pass


class CalculateSeasonScoreCommandExecutor(BaseCommandExecutor[CalculateSeasonScoreCommand, CalculateSeasonScoreResult]):
    def __init__(
        self,
        league_config_repo: LeagueConfigRepository,
        player_score_repo: PlayerLeagueSeasonScoreRepository,
        player_repo: PlayerRepository,
        public_repo: PublicRepository,
        player_season_repo: PlayerSeasonRepository,
        league_repo: LeagueRepository,
    ):
        self.league_config_repo = league_config_repo
        self.player_score_repo = player_score_repo
        self.player_repo = player_repo
        self.public_repo = public_repo
        self.player_season_repo = player_season_repo
        self.league_repo = league_repo

    def on_execute(self, command: CalculateSeasonScoreCommand) -> CalculateSeasonScoreResult:
        league = self.league_repo.get(command.league_id)
        if not league:
            return CalculateSeasonScoreResult(command=command)

        state = self.public_repo.get_state()
        season = command.season or state.current_season
        completed_week = state.current_week - 1

        players_seasons = self.player_season_repo.get_all(season)

        scoring = self.league_config_repo.get_scoring_config(command.league_id)

        if not scoring:
            return CalculateSeasonScoreResult(command=command, error="League not found")

        player_season_scores: List[PlayerLeagueSeasonScore] = list()

        for player_season in players_seasons:
            player_season_score = PlayerLeagueSeasonScore.create(player_season, scoring, completed_week)
            player_season_scores.append(player_season_score)

        rank_player_seasons(player_season_scores)

        for player_score in player_season_scores:
            self.player_score_repo.set(command.league_id, player_score)

        @firestore.transactional
        def update_state(transaction):
            league_state = self.league_config_repo.get_state(command.league_id, transaction=transaction)
            league_state.last_season_recalc = datetime.now(tz=timezone.utc)
            self.league_config_repo.set_state(command.league_id, league_state, transaction=transaction)

        transaction = self.league_config_repo.firestore.create_transaction()
        update_state(transaction)

        return CalculateSeasonScoreResult(command=command)
