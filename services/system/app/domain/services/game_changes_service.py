

from typing import List, Optional
from fastapi import Depends
from pydantic import BaseModel
from api.app.cfl.cfl_game_proxy import CflGameProxy, create_cfl_game_proxy
from api.app.core.sim_state import SimState
from api.app.domain.entities.game import from_cfl
from api.app.domain.entities.player_game import PlayerGame

from api.app.domain.repositories.game_repository import GameRepository, create_game_repository


def create_game_changes_service(
    cfl_game_proxy: CflGameProxy = Depends(create_cfl_game_proxy),
    game_repository: GameRepository = Depends(create_game_repository),
):
    return GameChangesService(
        cfl_game_proxy=cfl_game_proxy,
        game_repository=game_repository,
    )


class GameChanges(BaseModel):
    game_changed: bool
    changed_players: Optional[List[PlayerGame]]


class GameChangesService:

    def __init__(
            self,
            cfl_game_proxy: CflGameProxy,
            game_repository: GameRepository,
    ):
        self.cfl_game_proxy = cfl_game_proxy
        self.game_repository = game_repository

    def get_changes(self, season: int, game_id: str, count_away_players: bool, count_home_players: bool, sim_state: Optional[SimState]) -> GameChanges:
        official_game = self.cfl_game_proxy.get_game(season, game_id)["data"][0]
        official_game = from_cfl(official_game, count_away_players, count_home_players, sim_state)

        cached_game = self.game_repository.get(season, game_id)
        is_new = cached_game is None

        if is_new:
            needs_update = True
        else:
            needs_update = cached_game.hash != official_game.hash

        if not needs_update:
            return GameChanges(game_changed=False)

        changed_player_stats = []
        if is_new:
            changed_player_stats.extend(official_game.player_stats.values())
        else:
            # initialize existing game stats, in case they were deleted to force an update
            if not cached_game.player_stats:
                cached_game.player_stats = {}

            for player_id in official_game.player_stats:

                if player_id not in cached_game.player_stats:
                    changed_player_stats.append(official_game.player_stats[player_id])
                else:
                    updated_player = official_game.player_stats[player_id]
                    existing_player = cached_game.player_stats[player_id]
                    if updated_player.hash != existing_player.hash:
                        changed_player_stats.append(updated_player)

        return GameChanges(game_changed=True, changed_players=changed_player_stats)
