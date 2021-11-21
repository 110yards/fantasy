

from api.app.core.logging import Logger
from api.app.core.hash_dict import hash_dict
from api.app.domain.repositories.public_repository import PublicRepository, create_public_repository
from api.app.domain.repositories.state_repository import StateRepository, create_state_repository
from api.app.domain.repositories.game_repository import GameRepository, create_game_repository
from time import sleep
from api.app.cfl.cfl_player_proxy import CflPlayerProxy, create_cfl_player_proxy
from api.app.domain.enums.league_command_type import LeagueCommandType
from api.app.domain.services.league_command_push_data import LeagueCommandPushData
from api.app.domain.commands.league.update_league_player_details import UpdateLeaguePlayerDetailsCommand
from api.app.config.config import Settings, get_settings
from api.app.domain.topics import LEAGUE_COMMAND_TOPIC
from api.app.core.batch import create_batches
from api.app.domain.repositories.player_repository import PlayerRepository, create_player_repository
from pydantic.class_validators import root_validator
from api.app.domain.entities.team import Team
from typing import Dict, List, Optional
from api.app.domain.entities.player import Player, STATUS_ACTIVE, STATUS_INACTIVE, from_cfl
from fastapi.param_functions import Depends
from api.app.core.base_command_executor import BaseCommand, BaseCommandExecutor, BaseCommandResult
from api.app.cfl.cfl_roster_proxy import CflRosterProxy, cfl_roster_proxy
from firebase_admin import firestore
from api.app.core.publisher import Publisher, create_publisher


class UpdateActivePlayersCommand(BaseCommand):
    team_id: Optional[int]

    @root_validator
    def validate_all_teams(cls, values: dict):
        if values.get("team_id", None):
            values["all_teams"] = False

        return values


class UpdateActivePlayersCommandResult(BaseCommandResult):
    updated: Optional[List[Player]]
    deactivated: Optional[List[Player]]


def update_active_players_command_executor(
    cfl_roster_proxy: CflRosterProxy = Depends(cfl_roster_proxy),
    player_repo: PlayerRepository = Depends(create_player_repository),
    publisher: Publisher = Depends(create_publisher),
    settings: Settings = Depends(get_settings),
    cfl_player_proxy: CflPlayerProxy = Depends(create_cfl_player_proxy),
    game_repo: GameRepository = Depends(create_game_repository),
    state_repo: StateRepository = Depends(create_state_repository),
    public_repo: PublicRepository = Depends(create_public_repository),
):
    return UpdateActivePlayersCommandExecutor(
        settings,
        cfl_roster_proxy,
        player_repo,
        publisher,
        cfl_player_proxy,
        game_repo,
        state_repo,
        public_repo)


class UpdateActivePlayersCommandExecutor(BaseCommandExecutor[UpdateActivePlayersCommand, UpdateActivePlayersCommandResult]):

    def __init__(
        self,
        settings: Settings,
        roster_proxy: CflRosterProxy,
        player_repo: PlayerRepository,
        publisher: Publisher,
        cfl_player_proxy: CflPlayerProxy,
        game_repo: GameRepository,
        state_repo: StateRepository,
        public_repo: PublicRepository,
    ):
        self.season = settings.current_season
        self.settings = settings
        self.roster_proxy = roster_proxy
        self.player_repo = player_repo
        self.publisher = publisher
        self.cfl_player_proxy = cfl_player_proxy
        self.game_repo = game_repo
        self.state_repo = state_repo
        self.public_repo = public_repo

    def on_execute(self, command: UpdateActivePlayersCommand) -> UpdateActivePlayersCommandResult:

        rostered_players = []

        for team in Team.all():
            team_players = self.roster_proxy.get_roster(team.roster_id)
            rostered_players.extend(team_players)

        rostered_players = [from_cfl(player) for player in rostered_players]

        stored_players = self.player_repo.get_all(self.season)

        self.fix_bad_players(rostered_players, stored_players)

        stored_players = {player.id: player for player in stored_players}
        rostered_players = {player.id: player for player in rostered_players if player.cfl_central_id != 0}

        if self.public_repo.get_switches().enable_game_roster_status:
            self.update_status_from_game_rosters(rostered_players)

        changed_players = get_changed_players(rostered_players, stored_players)
        unrostered_players = get_unrostered_players(rostered_players, stored_players)
        updates = changed_players + unrostered_players

        batches = create_batches(updates, 500)

        for current_batch in batches:
            transaction = self.player_repo.firestore.create_transaction()

            @firestore.transactional
            def update_players(transaction, players):
                for player in players:
                    self.player_repo.set(self.season, player, transaction)

            update_players(transaction, current_batch)

        self.publish_changed_players(updates)

        return UpdateActivePlayersCommandResult(command=command, updated=changed_players, deactivated=unrostered_players)

    def update_status_from_game_rosters(self, rostered_players: Dict[str, Player]):
        current_week = self.state_repo.get().current_week
        games = self.game_repo.for_week(self.season, current_week)

        teams_with_rosters: List[int] = []
        player_ids_on_game_roster: List[str] = []

        for game in games:
            if game.away_roster:
                teams_with_rosters.append(game.teams.away.id)
                ids = [p.id for p in game.away_roster.values()]
                player_ids_on_game_roster.extend(ids)

            if game.home_roster:
                teams_with_rosters.append(game.teams.home.id)
                ids = [p.id for p in game.home_roster.values()]
                player_ids_on_game_roster.extend(ids)

        for rostered_player in rostered_players.values():
            scratched = rostered_player.team.id in teams_with_rosters and rostered_player.id not in player_ids_on_game_roster
            if rostered_player.status_current == STATUS_ACTIVE and scratched:
                rostered_player.status_current = STATUS_INACTIVE
                rostered_player.hash = hash_dict(rostered_player.dict())
                Logger.info(f"Scratched {rostered_player.display_name}")

    def publish_changed_players(self, updated_players: List[Player]):
        for player in updated_players:
            command = UpdateLeaguePlayerDetailsCommand(player=player)
            payload = LeagueCommandPushData(command_type=LeagueCommandType.UPDATE_PLAYER, command_data=command.dict())
            self.publisher.publish(payload, LEAGUE_COMMAND_TOPIC)

    def fix_bad_players(self, rostered_players: List[Player], stored_players: List[Player]):
        known_players_by_stats_id = {player.stats_inc_id: player for player in stored_players}

        request_count = 0
        for player in rostered_players:
            if player.cfl_central_id != 0 or not player.stats_inc_id:
                continue

            # have we seen and fixed this player before?
            if player.stats_inc_id in known_players_by_stats_id:
                player.cfl_central_id = known_players_by_stats_id[player.stats_inc_id].cfl_central_id
                player.id = str(player.cfl_central_id)
                continue

            # bummer
            page_size = 20
            page_number = 1
            found = False

            while True:
                request_count += 1
                if request_count > 30:
                    sleep(10)
                    request_count = 0

                response = self.cfl_player_proxy.get_players_by_last_name(player.last_name, page_number, page_size)
                for match in response["data"]:
                    if str(match["stats_inc_id"]) == player.stats_inc_id:
                        player.cfl_central_id = match["cfl_central_id"]
                        player.id = str(player.cfl_central_id)
                        found = True
                        break

                if found or len(response["data"]) < page_size:
                    break
                else:
                    page_number += 1


def get_changed_players(rostered_players: Dict[str, Player], stored_players: Dict[str, Player]) -> List[Player]:
    updates = []

    for player_id in rostered_players:
        current = rostered_players[player_id]
        exists = player_id in stored_players

        needs_update = False

        if exists:
            stored = stored_players[player_id]
            needs_update = stored.hash != current.hash

        if not exists or needs_update:
            updates.append(current)

    return updates


def get_unrostered_players(rostered_players: Dict[str, Player], stored_players: Dict[str, Player]) -> List[Player]:
    unrostered = []

    for player_id in stored_players:
        player = stored_players[player_id]
        rostered = player_id in rostered_players

        if not rostered and player.team.id != Team.free_agent().id:
            player.team = Team.free_agent()
            unrostered.append(player)

    return unrostered
