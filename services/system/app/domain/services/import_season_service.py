
from typing import Any, Dict, List

from fastapi import Depends
from services.system.app.cfl.cfl_game_proxy import CflGameProxy, create_cfl_game_proxy
from yards_py.core.logging import Logger
from yards_py.domain.entities.event_type import EVENT_TYPE_REGULAR
from yards_py.domain.entities.player_season import PlayerSeason
from yards_py.domain.entities.player_game import PlayerGame
from yards_py.domain.repositories.game_repository import GameRepository, create_game_repository
from yards_py.domain.repositories.player_season_repository import PlayerSeasonRepository, create_player_season_repository
from services.system.app.domain.services.game_changes_service import GameChangesService, create_game_changes_service


def create_previous_season_stats_service(
    cfl_game_proxy: CflGameProxy = Depends(create_cfl_game_proxy),
    game_changes_service: GameChangesService = Depends(create_game_changes_service),
    player_season_repo: PlayerSeasonRepository = Depends(create_player_season_repository),
    game_repo: GameRepository = Depends(create_game_repository),
):
    return ImportSeasonService(
        cfl_game_proxy=cfl_game_proxy,
        game_changes_service=game_changes_service,
        player_season_repo=player_season_repo,
        game_repo=game_repo,
    )


class ImportSeasonService:

    def __init__(
        self,
        cfl_game_proxy: CflGameProxy,
        game_changes_service: GameChangesService,
        player_season_repo: PlayerSeasonRepository,
        game_repo: GameRepository,
    ):
        self.cfl_game_proxy = cfl_game_proxy
        self.game_changes_service = game_changes_service
        self.player_season_repo = player_season_repo
        self.game_repo = game_repo

    def import_season(self, season: int, clean: bool) -> Any:

        if clean:
            self.game_repo.delete_all(season)

        result = self.cfl_game_proxy.get_game_summaries_for_season(season)
        games: List[Dict] = result["data"]

        game_ids = [g["game_id"] for g in games if g["event_type"]["event_type_id"] == EVENT_TYPE_REGULAR]

        players_with_stats: Dict[str, List[PlayerGame]] = {}

        count = 1
        total = len(game_ids)
        for game_id in game_ids:
            Logger.info(f"Processing {game_id} ({count}/{total})")
            changes = self.game_changes_service.get_changes(season, game_id, True, True, None)
            if changes.game_changed and changes.changed_players:
                for player_game in changes.changed_players:
                    if player_game.player_id not in players_with_stats:
                        players_with_stats[player_game.player_id] = []

                    players_with_stats[player_game.player_id].append(player_game)

            count += 1

        player_seasons: List[PlayerSeason] = []
        for player_id, games in players_with_stats.items():
            player_season = PlayerSeason.create(season, player_id, games)
            player_seasons.append(player_season)

        self.player_season_repo.set_all(season, player_seasons)
