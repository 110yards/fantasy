

from datetime import datetime, timezone
from services.system.app.di import create_publisher
from yards_py.core.annotate_args import annotate_args
from yards_py.core.logging import Logger
from yards_py.domain.repositories.approval_player_repository import ApprovalPlayerRepository, create_approval_player_repository
from yards_py.domain.repositories.public_repository import PublicRepository, create_public_repository
from yards_py.domain.repositories.state_repository import StateRepository, create_state_repository
from yards_py.domain.repositories.game_repository import GameRepository, create_game_repository
from services.system.app.api_proxies.cfl_player_proxy import CflPlayerProxy, create_cfl_player_proxy
from yards_py.domain.enums.league_command_type import LeagueCommandType
from services.system.app.domain.services.league_command_push_data import LeagueCommandPushData
from services.system.app.domain.commands.league.update_league_player_details import UpdateLeaguePlayerDetailsCommand
from yards_py.domain.topics import LEAGUE_COMMAND_TOPIC
from yards_py.domain.repositories.player_repository import PlayerRepository, create_player_repository
from pydantic.class_validators import root_validator
from yards_py.domain.entities.team import Team
from typing import List, Optional
from yards_py.domain.entities.player import Player
from fastapi.param_functions import Depends
from yards_py.core.base_command_executor import BaseCommand, BaseCommandExecutor, BaseCommandResult
from services.system.app.api_proxies.cfl_roster_proxy import CflRosterProxy, cfl_roster_proxy
from yards_py.core.publisher import Publisher
from firebase_admin.firestore import firestore
from google.cloud.firestore import Transaction


class UpdateActivePlayersCommand(BaseCommand):
    team_id: Optional[int]
    force: Optional[bool] = False

    @root_validator
    def validate_all_teams(cls, values: dict):
        if values.get("team_id", None):
            values["all_teams"] = False

        return values


@annotate_args
class UpdateActivePlayersCommandResult(BaseCommandResult):
    updated: Optional[List[Player]]
    new: Optional[List[Player]]
    deactivated: Optional[List[Player]]


class UpdateActivePlayersCommandExecutor(BaseCommandExecutor[UpdateActivePlayersCommand, UpdateActivePlayersCommandResult]):

    def __init__(
        self,
        roster_proxy: CflRosterProxy,
        player_repo: PlayerRepository,
        publisher: Publisher,
        cfl_player_proxy: CflPlayerProxy,
        game_repo: GameRepository,
        state_repo: StateRepository,
        public_repo: PublicRepository,
        approval_repo: ApprovalPlayerRepository,
    ):
        self.roster_proxy = roster_proxy
        self.player_repo = player_repo
        self.publisher = publisher
        self.cfl_player_proxy = cfl_player_proxy
        self.game_repo = game_repo
        self.state_repo = state_repo
        self.public_repo = public_repo
        self.approval_repo = approval_repo

    def on_execute(self, command: UpdateActivePlayersCommand) -> UpdateActivePlayersCommandResult:
        season = self.state_repo.get().current_season
        self.current_season = season


        current_players = self.cfl_player_proxy.get_players_for_season()
        

        current_players = [Player.from_cfl_api(p) for p in current_players]
        current_players = {player.id: player for player in current_players}

        stored_players = self.player_repo.get_all(season)
        stored_players = {player.id: player for player in stored_players}

        players_with_alt_ids = {}
        for player in stored_players.values():
            for alt_id in player.alternate_computed_ids:
                players_with_alt_ids[alt_id] = player
        
        auto_accept_all = len(stored_players) == 0

        if auto_accept_all:
            Logger.info("No players found in database, accepting all players")
            

        # if self.public_repo.get_switches().enable_game_roster_status:
        #     self.update_status_from_game_rosters(season, current_players)

        # changed_players = get_changed_players(current_players, stored_players, command.force)
        # unrostered_players = self.get_unrostered_players(current_players, stored_players)
        # updates = changed_players + unrostered_players

        to_update = []
        new_players = []

        for player in current_players.values():
            existing_player = stored_players.get(player.id)

            if not existing_player:
                existing_player = players_with_alt_ids.get(player.id)

            if existing_player:
                stored_players.pop(existing_player.id, None) # Remove - anyone left is a free agent

                # if we found by alternate id, make sure we keep the original id
                player.player_id = existing_player.id
                player.id = existing_player.id
                player.alternate_computed_ids = existing_player.alternate_computed_ids

                if existing_player.computed_hash() != player.computed_hash():
                    Logger.info(f"Player changed: {player.display_name} ({player.team.abbr})")
                    to_update.append(player)
            else:
                Logger.info(f"New player: {player.display_name} ({player.team.abbr})")
                new_players.append(player)

                if auto_accept_all:
                    to_update.append(player)
                else:
                    new_players.append(player)
        
        # anyone left in stored_players is a free agent
        for player in stored_players.values():
            player.team = Team.free_agent()
            to_update.append(player)
            Logger.info(f"Player became free agent: {player.display_name}")
        
        # save updated players
        try:
            if to_update:
                Logger.info(f"Updating {len(to_update)} players")
                self.player_repo.set_all(season, to_update)
                self.publish_changed_players(to_update)
        except Exception as e:
            Logger.error("Error updating players", exc_info=e)
            return UpdateActivePlayersCommandResult(command, error="Error updating players")

        # save new players
        try:
            if new_players:
                Logger.info(f"Adding {len(new_players)} new players")
                self.approval_repo.set_all(new_players)
        except Exception as e:
            Logger.error("Error adding new players", exc_info=e)
            return UpdateActivePlayersCommandResult(command, error="Error adding new players")
        
        @firestore.transactional
        def update_state(transaction: Transaction):
            state = self.state_repo.get(transaction)
            state.last_player_update = datetime.now().astimezone(tz=timezone.utc)
            self.state_repo.set(state, transaction)

        transaction = self.state_repo.firestore.create_transaction()
        update_state(transaction)
        return UpdateActivePlayersCommandResult(
            command=command, 
            updated=to_update,
            new=new_players,
        )

#     def update_status_from_game_rosters(self, season, current_players: Dict[str, Player]):
#         current_week = self.state_repo.get().current_week
#         games = self.game_repo.for_week(season, current_week)

#         teams_with_rosters: List[int] = []
#         player_ids_on_game_roster: List[str] = []

#         for game in games:
#             if game.away_roster:
#                 teams_with_rosters.append(game.teams.away.id)
#                 ids = [p.id for p in game.away_roster.values()]
#                 player_ids_on_game_roster.extend(ids)

#             if game.home_roster:
#                 teams_with_rosters.append(game.teams.home.id)
#                 ids = [p.id for p in game.home_roster.values()]
#                 player_ids_on_game_roster.extend(ids)

#         for player in current_players.values():
#             scratched = player.team.abbr in teams_with_rosters and player.id not in player_ids_on_game_roster
#             if player.status_current == STATUS_ACTIVE and scratched:
#                 player.status_current = STATUS_INACTIVE

    def publish_changed_players(self, updated_players: List[Player]):
        for player in updated_players:
            command = UpdateLeaguePlayerDetailsCommand(player=player)
            payload = LeagueCommandPushData(command_type=LeagueCommandType.UPDATE_PLAYER, command_data=command.dict())
            self.publisher.publish(payload, LEAGUE_COMMAND_TOPIC)

#     def get_unrostered_players(self, rostered_players: Dict[str, Player], stored_players: Dict[str, Player]) -> List[Player]:
#         unrostered = []

#         for player in stored_players.values():
#             rostered = player.id in rostered_players

#             if not rostered and player.team.abbr != Team.free_agent().abbr:
#                 player.team = Team.free_agent()
#                 player.compute_hash()
#                 unrostered.append(player)
#                 Logger.debug("Player not found in CFL data, setting to free agent", extra={
#                     "player": {
#                         "player_id": player.id,
#                         "first_name": player.first_name,
#                         "last_name": player.last_name,
#                     }
#                 })

#         return unrostered


# def get_changed_players(current_players: Dict[str, Player], stored_players: Dict[str, Player], force: bool) -> List[Player]:
#     updates = []

#     for current in current_players.values():
#         stored = stored_players.get(current.id, None)

#         needs_update = False
#         current.compute_hash()

#         if stored:
#             needs_update = stored.hash != current.hash

#         if not stored or needs_update or force:
#             updates.append(current)

#     return updates



def update_active_players_command_executor(
    cfl_roster_proxy: CflRosterProxy = Depends(cfl_roster_proxy),
    player_repo: PlayerRepository = Depends(create_player_repository),
    publisher: Publisher = Depends(create_publisher),
    cfl_player_proxy: CflPlayerProxy = Depends(create_cfl_player_proxy),
    game_repo: GameRepository = Depends(create_game_repository),
    state_repo: StateRepository = Depends(create_state_repository),
    public_repo: PublicRepository = Depends(create_public_repository),
    approval_repo: ApprovalPlayerRepository = Depends(create_approval_player_repository),
):
    return UpdateActivePlayersCommandExecutor(
        cfl_roster_proxy,
        player_repo,
        publisher,
        cfl_player_proxy,
        game_repo,
        state_repo,
        public_repo,
        approval_repo,
    )
