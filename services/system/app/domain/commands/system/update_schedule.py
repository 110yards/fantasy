from __future__ import annotations
from yards_py.domain.entities.event_status import EVENT_STATUS_FINAL
from yards_py.domain.entities.event_type import EVENT_TYPE_REGULAR
from yards_py.domain.entities.scheduled_game import ScheduledGame


from yards_py.domain.repositories.public_repository import PublicRepository, create_public_repository
from yards_py.core.logging import Logger

import logging
from typing import Dict, List, Optional

from services.system.app.api_proxies.cfl_game_proxy import CflGameProxy, create_cfl_game_proxy
from yards_py.core.base_command_executor import BaseCommand, BaseCommandExecutor, BaseCommandResult

from fastapi.param_functions import Depends
from timeit import default_timer as timer

from yards_py.domain.repositories.scheduled_game_repository import ScheduledGameRepository, create_scheduled_game_repository


logger = logging.getLogger()


def create_update_schedule_command_executor(
    cfl_proxy: CflGameProxy = Depends(create_cfl_game_proxy),
    game_repo: ScheduledGameRepository = Depends(create_scheduled_game_repository),
    public_repo: PublicRepository = Depends(create_public_repository),
):
    return UpdateScheduleCommandExecutor(
        cfl_proxy=cfl_proxy,
        scheduled_game_repo=game_repo,
        public_repo=public_repo)


class UpdateScheduleCommand(BaseCommand):
    include_final: bool = False
    season: Optional[int]


class UpdateScheduleResult(BaseCommandResult):
    games: Optional[List[ScheduledGame]]


class UpdateScheduleCommandExecutor(BaseCommandExecutor[UpdateScheduleCommand, UpdateScheduleResult]):

    def __init__(
        self,
        cfl_proxy: CflGameProxy,
        scheduled_game_repo: ScheduledGameRepository,
        public_repo: PublicRepository,
    ):
        self.cfl_proxy = cfl_proxy
        self.scheduled_game_repo = scheduled_game_repo
        self.public_repo = public_repo

    def on_execute(self, command: UpdateScheduleCommand) -> UpdateScheduleResult:
        start = timer()

        if not command.season:
            state = self.public_repo.get_state()
            season = state.current_season
        else:
            season = command.season

        Logger.info("Updating schedule")

        Logger.debug(f"Loading games from CFL ({timer() - start})")
        future_games = self.get_future_games(season, command.include_final)
        Logger.debug(f"Loading games from DB ({timer() - start})")
        stored_games = self.get_stored_games(season)

        updated_games = []

        for game in future_games:
            stored_game = stored_games.get(game.id, None)
            if not stored_game or stored_game.hash != game.hash:
                self.scheduled_game_repo.set(season, game)
                updated_games.append(game)

        Logger.info(f"Schedule update complete ({timer() - start})")
        return UpdateScheduleResult(
            command=command,
            games=future_games
        )

    def get_future_games(self, season: int, include_final: bool) -> List[ScheduledGame]:
        response = self.cfl_proxy.get_game_summaries_for_season(season)

        games = [ScheduledGame.from_cfl(game) for game in response["data"]]
        games = [game for game in games if game.event_type.event_type_id == EVENT_TYPE_REGULAR]

        if not include_final:
            games = [game for game in games if game.event_status.event_status_id != EVENT_STATUS_FINAL]

        return games

    def get_stored_games(self, season: int) -> Dict[str, ScheduledGame]:
        games = self.scheduled_game_repo.get_all(season)
        return {game.id: game for game in games}
