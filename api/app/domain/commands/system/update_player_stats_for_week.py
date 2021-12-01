from __future__ import annotations

from api.app.domain.repositories.state_repository import StateRepository, create_state_repository


from api.app.domain.entities.player import PlayerGame, from_game_player
from api.app.domain.repositories.player_repository import PlayerRepository, create_player_repository
from api.app.domain.repositories.public_repository import PublicRepository, create_public_repository
from api.app.core.logging import Logger

import time
import logging
from typing import Dict, List

from api.app.cfl.cfl_game_proxy import CflGameProxy, create_cfl_game_proxy
from api.app.core.base_command_executor import BaseCommand, BaseCommandExecutor, BaseCommandResult
from api.app.core.publisher import Publisher, create_publisher
from api.app.domain.entities.game import Game, from_cfl
from api.app.domain.entities.game_player_stats import GamePlayerStats
from api.app.domain.repositories.game_repository import GameRepository, create_game_repository
from fastapi.param_functions import Depends
from firebase_admin import firestore

logger = logging.getLogger()


def create_update_player_stats_for_week_command_executor(
    cfl_proxy: CflGameProxy = Depends(create_cfl_game_proxy),
    game_repo: GameRepository = Depends(create_game_repository),
    publisher: Publisher = Depends(create_publisher),
    public_repo: PublicRepository = Depends(create_public_repository),
    player_repo: PlayerRepository = Depends(create_player_repository),
    state_repo: StateRepository = Depends(create_state_repository),
):
    return UpdatePlayerStatsForWeekCommandExecutor(cfl_proxy, game_repo, publisher, public_repo, player_repo, state_repo)


class UpdatePlayerStatsForWeekCommand(BaseCommand):
    season: int
    week: int


class UpdatePlayerStatsForWeekResult(BaseCommandResult):
    pass


class UpdatePlayerStatsForWeekCommandExecutor(BaseCommandExecutor[UpdatePlayerStatsForWeekCommand, UpdatePlayerStatsForWeekResult]):

    def __init__(
        self,
        cfl_proxy: CflGameProxy,
        game_repo: GameRepository,
        publisher: Publisher,
        public_repo: PublicRepository,
        player_repo: PlayerRepository,
        state_repo: StateRepository,
    ):
        self.cfl_proxy = cfl_proxy
        self.game_repo = game_repo
        self.publisher = publisher
        self.public_repo = public_repo
        self.player_repo = player_repo
        self.state_repo = state_repo

    def on_execute(self, command: UpdatePlayerStatsForWeekCommand) -> UpdatePlayerStatsForWeekResult:
        Logger.info(f"Updating player stats for week {command.week}")

        season = command.season

        if self.public_repo.get_switches().enable_score_testing:
            season = 2019
            Logger.warn("SCORE TESTING SWITCH IS ENABLED")

        current_games = self.get_current_games(season, command.week)
        player_updates = get_players(current_games)

        transaction = self.game_repo.firestore.create_transaction()

        @firestore.transactional
        def update(transaction, players: List[GamePlayerStats]):

            pending_player_updates = []

            for player_update in players:
                player = self.player_repo.get(season, player_update.player.id, transaction)
                game_id = player_update.game_id
                if not player:
                    player = from_game_player(player_update.player, player_update.team)

                if not player.game_stats:
                    player.game_stats = {}

                player.game_stats[game_id] = PlayerGame(team=player.team, **player_update.stats.dict())
                pending_player_updates.append(player)

            for player in pending_player_updates:
                self.player_repo.set(season, player, transaction)

            return pending_player_updates

        update(transaction, player_updates)

        return UpdatePlayerStatsForWeekResult(
            command=command,
        )

    def get_current_games(self, season, week) -> Dict[str, Game]:
        if week is not None:
            response = self.cfl_proxy.get_game_summaries_for_week(season, week)
        else:
            response = self.cfl_proxy.get_game_summaries_for_season(season)

        game_ids = [str(game["game_id"]) for game in response["data"]]
        games = {}

        for game_id in game_ids:
            game = self.cfl_proxy.get_game(season, game_id)["data"][0]
            games[game_id] = from_cfl(game)
            if len(game_ids) > 20:
                time.sleep(2.5)  # sleep 1 second to avoid rate limiting from the API

        return games


def get_players(games: Dict[str, Game]) -> List[GamePlayerStats]:
    player_stats = []

    for game_id in games:
        game = games[game_id]
        player_stats.extend(game.player_stats.values())

    return player_stats
