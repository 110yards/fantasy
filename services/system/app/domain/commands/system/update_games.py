from __future__ import annotations
from yards_py.core.sim_state import SimState
from yards_py.domain.entities.event_status import EVENT_STATUS_POSTPONED

from pydantic.main import BaseModel
from yards_py.domain.entities.opponents import Opponents
from yards_py.domain.entities.scoreboard import Scoreboard
from yards_py.domain.entities.state import Locks
from yards_py.domain.entities.team import Team
from yards_py.domain.repositories.player_game_repository import PlayerGameRepository, create_player_game_repository
from yards_py.domain.repositories.scheduled_game_repository import ScheduledGameRepository, create_scheduled_game_repository
from yards_py.domain.repositories.state_repository import StateRepository, create_state_repository


from yards_py.domain.entities.player_game import PlayerGame
from yards_py.domain.repositories.player_repository import PlayerRepository, create_player_repository
from yards_py.domain.repositories.public_repository import PublicRepository, create_public_repository
from yards_py.core.logging import Logger
from yards_py.domain.topics import UPDATE_PLAYERS_TOPIC

import time
import logging
from typing import Dict, List, Optional

from services.system.app.api_proxies.cfl_game_proxy import CflGameProxy, create_cfl_game_proxy
from yards_py.core.base_command_executor import BaseCommand, BaseCommandExecutor, BaseCommandResult
from yards_py.core.publisher import Publisher
from services.system.app.di import create_publisher
from yards_py.domain.entities.game import Game, from_cfl
from yards_py.domain.repositories.game_repository import GameRepository, create_game_repository
from fastapi.param_functions import Depends
from firebase_admin import firestore
from timeit import default_timer as timer


logger = logging.getLogger()


def create_update_games_command_executor(
    cfl_proxy: CflGameProxy = Depends(create_cfl_game_proxy),
    game_repo: GameRepository = Depends(create_game_repository),
    publisher: Publisher = Depends(create_publisher),
    public_repo: PublicRepository = Depends(create_public_repository),
    player_repo: PlayerRepository = Depends(create_player_repository),
    state_repo: StateRepository = Depends(create_state_repository),
    player_game_repo: PlayerGameRepository = Depends(create_player_game_repository),
    scheduled_game_repo: ScheduledGameRepository = Depends(create_scheduled_game_repository),
):
    return UpdateGamesCommandExecutor(cfl_proxy, game_repo, publisher, public_repo, player_repo, state_repo, player_game_repo, scheduled_game_repo)


class UpdateGamesCommand(BaseCommand):
    week: Optional[int]
    season: Optional[int]
    sim_state: Optional[SimState]
    commit_changes: Optional[bool] = True


class UpdateGamesResult(BaseCommandResult):
    changed_games: Optional[List[Game]]
    changed_players: Optional[List[PlayerGame]]


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
        scheduled_game_repo: ScheduledGameRepository,
    ):
        self.cfl_proxy = cfl_proxy
        self.game_repo = game_repo
        self.publisher = publisher
        self.public_repo = public_repo
        self.player_repo = player_repo
        self.state_repo = state_repo
        self.player_game_repo = player_game_repo
        self.scheduled_game_repo = scheduled_game_repo

    def on_execute(self, command: UpdateGamesCommand) -> UpdateGamesResult:
        start = timer()

        state = self.public_repo.get_state()

        season = command.season or state.current_season
        week = command.week or state.current_week

        updating_current_season = season == state.current_season
        updating_current_week = week == state.current_week

        update_state = updating_current_season and updating_current_week

        Logger.info(f"Updating games for week {week}")

        Logger.debug(f"Loading games from CFL ({timer() - start})")
        current_games = self.get_current_games(season, week, command.sim_state)
        Logger.debug(f"Done loading games from CFL ({timer() - start})")
        Logger.debug(f"Loading games from DB ({timer() - start})")
        stored_games = self.get_stored_games(season, week)

        Logger.debug(f"Checking if any game rosters have been added ({timer() - start})")
        roster_added = False
        for game_id in current_games:
            current_game = current_games[game_id]
            stored_game = stored_games.get(game_id, None)
            if current_game.away_roster and (not stored_game or not stored_game.away_roster):
                roster_added = True

            if current_game.home_roster and (not stored_game or not stored_game.home_roster):
                roster_added = True

        # we filter down the list of games and players in those games to only the ones which have changed since last update.
        Logger.debug(f"Checking for updated games ({timer() - start})")
        game_updates = get_changed_games(current_games, stored_games)
        Logger.debug(f"Checking for changed players ({timer() - start})")
        player_updates = get_changed_players(game_updates, stored_games)

        locked_teams: List[str] = []
        active_games_count = 0

        opponents: Dict[str, str] = {}

        Logger.debug(f"Initializing locks ({timer() - start})")
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

        Logger.debug(f"Initializing scoreboard ({timer() - start})")
        new_scoreboard = Scoreboard.create(current_games.values())
        Logger.debug(f"Initializing opponents ({timer() - start})")
        new_opponents = Opponents.create(opponents)

        @firestore.transactional
        def update_games(transaction, games: Dict[str, Game], players: List[PlayerGame]):
            Logger.debug(f"Saving changes ({timer() - start})")

            new_state = state.copy()
            new_state.locks = new_locks_state

            current_scoreboard = self.public_repo.get_scoreboard(transaction)
            current_opponents = self.public_repo.get_opponents(transaction)

            pending_player_updates = []

            Logger.debug(f"Saving {len(players)} player changes ({timer() - start})")
            for player_game in players:
                self.player_game_repo.set(season, player_game, transaction)

            Logger.debug(f"Saving game changes ({timer() - start})")
            for game_id in games:
                game = game_updates[game_id]
                self.game_repo.set(season, game, transaction)

            if new_state.changed(state) and update_state:
                Logger.debug(f"Saving state ({timer() - start})")
                self.state_repo.set(new_state, transaction)

            if new_scoreboard.changed(current_scoreboard) and update_state:
                Logger.debug(f"Saving scoreboard ({timer() - start})")
                self.public_repo.set_scoreboard(new_scoreboard, transaction)

            if new_opponents.changed(current_opponents) and update_state:
                Logger.debug(f"Saving opponents ({timer() - start})")
                self.public_repo.set_opponents(new_opponents, transaction)

            return pending_player_updates

        if command.commit_changes:
            Logger.debug(f"Creating transaction ({timer() - start})")
            transaction = self.game_repo.firestore.create_transaction()
            update_games(transaction, game_updates, player_updates)

        if roster_added and command.commit_changes:
            Logger.debug(f"Sending UPDATE_PLAYERS event ({timer() - start})")
            self.publisher.publish(BaseModel(), UPDATE_PLAYERS_TOPIC)

        Logger.info(f"Games update complete ({timer() - start})")
        return UpdateGamesResult(
            command=command,
            changed_games=[game_updates[game_id] for game_id in game_updates],
            changed_players=player_updates,
        )

    def get_current_games(self, season: int, week: int, sim_state: Optional[SimState]) -> Dict[str, Game]:
        games_for_week = self.scheduled_game_repo.get_for_week(season, week)

        game_ids = [game.id for game in games_for_week]
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

            games[game_id] = from_cfl(game, count_away_players, count_home_players, sim_state)
            if len(game_ids) > 20:
                time.sleep(2.5)  # sleep to avoid rate limiting from the API

        return games

    def get_stored_games(self, season: int, week: int) -> Dict[str, Game]:
        if week is not None:
            games = self.game_repo.for_week(season, week)
        else:
            games = self.game_repo.get_all(season)

        return {game.id: game for game in games}


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


def get_changed_players(updated_games: Dict[str, Game], stored_games: Dict[str, Game]) -> List[PlayerGame]:
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
