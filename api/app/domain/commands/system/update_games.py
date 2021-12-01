from __future__ import annotations
from api.app.domain.entities.event_status import EVENT_STATUS_POSTPONED

from pydantic.main import BaseModel
from api.app.domain.entities.opponents import Opponents
from api.app.domain.entities.scoreboard import Scoreboard
from api.app.domain.entities.state import Locks
from api.app.domain.entities.team import Team
from api.app.domain.repositories.player_game_repository import PlayerGameRepository, create_player_game_repository
from api.app.domain.repositories.state_repository import StateRepository, create_state_repository


from api.app.domain.entities.player import PlayerGame
from api.app.domain.repositories.player_repository import PlayerRepository, create_player_repository
from api.app.domain.repositories.public_repository import PublicRepository, create_public_repository
from api.app.core.logging import Logger
from api.app.domain.commands.league.update_player_stats import UpdatePlayerStatsCommand
from api.app.domain.topics import UPDATE_PLAYERS_TOPIC

import time
import logging
from typing import Dict, List, Optional

from api.app.cfl.cfl_game_proxy import CflGameProxy, create_cfl_game_proxy
from api.app.core.base_command_executor import BaseCommand, BaseCommandExecutor, BaseCommandResult
from api.app.core.publisher import Publisher, create_publisher
from api.app.domain.entities.game import Game, from_cfl
from api.app.domain.entities.game_player_stats import GamePlayerStats
from api.app.domain.repositories.game_repository import GameRepository, create_game_repository
from fastapi.param_functions import Depends
from firebase_admin import firestore

logger = logging.getLogger()


def create_update_games_command_executor(
    cfl_proxy: CflGameProxy = Depends(create_cfl_game_proxy),
    game_repo: GameRepository = Depends(create_game_repository),
    publisher: Publisher = Depends(create_publisher),
    public_repo: PublicRepository = Depends(create_public_repository),
    player_repo: PlayerRepository = Depends(create_player_repository),
    state_repo: StateRepository = Depends(create_state_repository),
    player_game_repo: PlayerGameRepository = Depends(create_player_game_repository),
):
    return UpdateGamesCommandExecutor(cfl_proxy, game_repo, publisher, public_repo, player_repo, state_repo, player_game_repo)


class UpdateGamesCommand(BaseCommand):
    season: int
    week: Optional[int]


class UpdateGamesResult(BaseCommandResult):
    changed_games: Optional[List[Game]]
    changed_players: Optional[List[UpdatePlayerStatsCommand]]


class UpdateGamesCommandExecutor(BaseCommandExecutor[UpdateGamesCommand, UpdateGamesResult]):

    def __init__(
        self,
        cfl_proxy: CflGameProxy,
        game_repo: GameRepository,
        publisher: Publisher,
        public_repo: PublicRepository,
        player_repo: PlayerRepository,
        state_repo: StateRepository,
        player_game_repo: PlayerGameRepository,
    ):
        self.cfl_proxy = cfl_proxy
        self.game_repo = game_repo
        self.publisher = publisher
        self.public_repo = public_repo
        self.player_repo = player_repo
        self.state_repo = state_repo
        self.player_game_repo = player_game_repo

    def on_execute(self, command: UpdateGamesCommand) -> UpdateGamesResult:
        Logger.info(f"Updating games for week {command.week}")

        season = command.season

        if self.public_repo.get_switches().enable_score_testing:
            season = 2019
            Logger.warn("SCORE TESTING SWITCH IS ENABLED")

        current_games = self.get_current_games(season, command.week)
        stored_games = self.get_stored_games(season, command.week)

        roster_added = False
        for game_id in current_games:
            current_game = current_games[game_id]
            stored_game = stored_games.get(game_id, None)
            if current_game.away_roster and (not stored_game or not stored_game.away_roster):
                roster_added = True

            if current_game.home_roster and (not stored_game or not stored_game.home_roster):
                roster_added = True

        # we filter down the list of games and players in those games to only the ones which have changed since last update.
        game_updates = get_changed_games(current_games, stored_games)
        player_updates = get_changed_players(game_updates, stored_games)

        transaction = self.game_repo.firestore.create_transaction()

        locked_teams: List[str] = []
        active_games_count = 0

        opponents: Dict[str, str] = {}

        for game in current_games.values():
            if game.event_status.event_status_id == EVENT_STATUS_POSTPONED:
                continue

            opponents[game.teams.away.abbreviation] = game.teams.home.abbreviation
            opponents[game.teams.home.abbreviation] = game.teams.away.abbreviation

            if game.event_status.has_started():
                active_games_count += 1
                locked_teams.append(game.teams.away.abbreviation)
                locked_teams.append(game.teams.home.abbreviation)

        all_games_active = active_games_count == len(current_games)

        new_locks_state = Locks.create(locked_teams, all_games_active)

        new_scoreboard = Scoreboard.create(current_games.values())
        new_opponents = Opponents.create(opponents)

        @firestore.transactional
        def update_games(transaction, games: Dict[str, Game], players: List[GamePlayerStats]):
            state = self.state_repo.get()

            new_state = state.copy()
            new_state.locks = new_locks_state

            current_scoreboard = self.public_repo.get_scoreboard()
            current_opponents = self.public_repo.get_opponents()

            pending_player_updates = []

            for player_update in players:
                # player = self.player_repo.get(season, player_update.player.id, transaction)
                # game_id = player_update.game_id
                # if not player:
                #     player = from_game_player(player_update.player, player_update.team)

                # if not player.game_stats:
                #     player.game_stats = {}

                # player.game_stats[game_id] = PlayerGameStats(team=player.team, **player_update.stats.dict())
                # pending_player_updates.append(player)
                player_game = PlayerGame(
                    id=player_update.player.id,
                    game_id=player_update.game_id,
                    player_id=player_update.player.id,
                    team=player_update.team,
                    opponent=player_update.opponent
                )
                self.player_game_repo.set(season, player_game, transaction)

            for game_id in games:
                game = game_updates[game_id]
                self.game_repo.set(season, game, transaction)

            # for player in pending_player_updates:
            #     self.player_repo.set(season, player, transaction)

            if new_state.changed(state):
                self.state_repo.set(new_state, transaction)

            if new_scoreboard.changed(current_scoreboard):
                self.public_repo.set_scoreboard(new_scoreboard, transaction)

            if new_opponents.changed(current_opponents):
                self.public_repo.set_opponents(new_opponents, transaction)

            return pending_player_updates

        update_games(transaction, game_updates, player_updates)
        # payloads = self.publish_changed_players(player_updates)

        if roster_added:
            self.publisher.publish(BaseModel(), UPDATE_PLAYERS_TOPIC)

        return UpdateGamesResult(
            command=command,
            changed_games=[game_updates[game_id] for game_id in game_updates],
            # changed_players=payloads
        )

    def get_current_games(self, season, week) -> Dict[str, Game]:
        response = self.cfl_proxy.get_game_summaries_for_week(season, week)

        game_ids = [str(game["game_id"]) for game in response["data"]]
        games = {}

        game_count_for_team: List[int, int] = {
            Team.bc().id: 0,
            Team.cgy().id: 0,
            Team.edm().id: 0,
            Team.ssk().id: 0,
            Team.wpg().id: 0,
            Team.ham().id: 0,
            Team.tor().id: 0,
            Team.ott().id: 0,
            Team.mtl().id: 0,
        }

        for game_id in game_ids:
            game = self.cfl_proxy.get_game(season, game_id)["data"][0]

            game_count_for_team[game["team_1"]["team_id"]] += 1
            game_count_for_team[game["team_2"]["team_id"]] += 1

            count_away_players = game_count_for_team[game["team_1"]["team_id"]] <= 1
            count_home_players = game_count_for_team[game["team_2"]["team_id"]] <= 1

            games[game_id] = from_cfl(game, count_away_players, count_home_players)
            if len(game_ids) > 20:
                time.sleep(2.5)  # sleep 1 second to avoid rate limiting from the API

        return games

    def get_stored_games(self, season: int, week: int) -> Dict[str, Game]:
        if week is not None:
            games = self.game_repo.for_week(season, week)
        else:
            games = self.game_repo.get_all(season)

        return {game.id: game for game in games}

    # def publish_changed_players(self, updated_players: List[GamePlayerStats]):
    #     payloads = []
    #     for updated_player in updated_players:
    #         command = UpdatePlayerStatsCommand(game_id=updated_player.game_id, player_stats=updated_player)
    #         payload = LeagueCommandPushData(command_type=LeagueCommandType.UPDATE_PLAYER_STATS, command_data=command.dict())
    #         self.publisher.publish(payload, LEAGUE_COMMAND_TOPIC)

    #         payloads.append(command)

    #     return payloads


def get_changed_games(current_games: Dict[str, Game], stored_games: Dict[str, Game]) -> Dict[str, Game]:
    updates = []

    for game_id in current_games:
        current = current_games[game_id]
        exists = game_id in stored_games

        needs_update = False

        if exists:
            stored = stored_games[game_id]
            needs_update = stored.hash != current.hash

        if not exists or needs_update:
            updates.append(current)

    return {game.id: game for game in updates}


def get_changed_players(updated_games: Dict[str, Game], stored_games: Dict[str, Game]) -> List[GamePlayerStats]:
    changed_player_stats = []

    for game_id in updated_games:
        game = updated_games[game_id]

        is_new = game_id not in stored_games

        if is_new:
            changed_player_stats.extend(game.player_stats.values())
        else:
            existing_game = stored_games[game_id]

            # initialize existing game stats, in case they were deleted to force an update
            if not existing_game.player_stats:
                existing_game.player_stats = {}

            for player_id in game.player_stats:

                if player_id not in existing_game.player_stats:
                    changed_player_stats.append(game.player_stats[player_id])
                else:
                    updated_player = game.player_stats[player_id]
                    existing_player = existing_game.player_stats[player_id]
                    if updated_player.hash != existing_player.hash:
                        changed_player_stats.append(updated_player)

    return changed_player_stats
