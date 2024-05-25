

from datetime import datetime, timezone

from pydantic import BaseModel
from ....api_proxies.core.core_player_proxy import CorePlayerProxy, create_core_player_proxy
from yards_py.domain.entities.player_season import PlayerSeason
from yards_py.domain.entities.stats import Stats
from yards_py.domain.repositories.player_season_repository import PlayerSeasonRepository, create_player_season_repository
from yards_py.domain.repositories.state_repository import StateRepository, create_state_repository
from yards_py.domain.repositories.player_repository import PlayerRepository, create_player_repository
from fastapi.param_functions import Depends
from yards_py.core.base_command_executor import BaseCommand, BaseCommandExecutor, BaseCommandResult
from firebase_admin.firestore import firestore
from google.cloud.firestore import Transaction


class ImportPriorSeasonPlayerStatsCommand(BaseCommand):
    year: int


class ImportPriorSeasonPlayerStatsCommandResult(BaseCommandResult):
    pass

class ImportPriorSeasonPlayerStatsCommandExecutor(BaseCommandExecutor[ImportPriorSeasonPlayerStatsCommand, ImportPriorSeasonPlayerStatsCommandResult]):

    def __init__(
        self,
        player_repo: PlayerRepository,
        player_season_repo: PlayerSeasonRepository,
        state_repo: StateRepository,
        core_player_proxy: CorePlayerProxy,

    ):
        self.player_repo = player_repo
        self.player_season_repo = player_season_repo        
        self.state_repo = state_repo
        self.core_player_proxy = core_player_proxy

    def on_execute(self, command: ImportPriorSeasonPlayerStatsCommand) -> ImportPriorSeasonPlayerStatsCommandResult:
        
        season = command.year
        data = self.core_player_proxy.get_players_for_season(season, include_season_stats=True)

        # Note this import does not import players, only stats. if the player doesn't exist the stats will just be orphaned.
        # The assumption is that players are imported separately.

        players_with_stats = [ImportedPlayerWithStats(**x) for x in data]       

        player_seasons = [
            PlayerSeason(
                id=x.player.player_id,
                player_id=x.player.player_id,
                season=season,
                games_played=x.games_played,
                games = [], # only care about season totals
                stats = x.stats,
            )
            for x in players_with_stats
        ]

        self.player_season_repo.set_all(season, player_seasons)

        @firestore.transactional
        def update_state(transaction: Transaction):
            state = self.state_repo.get(transaction)
            state.last_player_update = datetime.now().astimezone(tz=timezone.utc)
            self.state_repo.set(state, transaction)

        transaction = self.state_repo.firestore.create_transaction()
        update_state(transaction)
        return ImportPriorSeasonPlayerStatsCommandResult(command=command)


class ImportedPlayer(BaseModel):
    player_id: str

class ImportedPlayerWithStats(BaseModel):
    player: ImportedPlayer
    games_played: int
    stats: Stats

def create_import_prior_season_player_stats_command_executor(
    player_repo: PlayerRepository = Depends(create_player_repository),
    player_season_repo: PlayerSeasonRepository = Depends(create_player_season_repository),
    state_repo: StateRepository = Depends(create_state_repository),
    core_player_proxy: CorePlayerProxy = Depends(create_core_player_proxy),
):
    return ImportPriorSeasonPlayerStatsCommandExecutor(
        player_repo=player_repo,
        player_season_repo=player_season_repo,
        state_repo=state_repo,
        core_player_proxy=core_player_proxy,
    )
