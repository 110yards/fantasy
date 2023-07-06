from typing import List

from app.yards_py.core.base_command_executor import BaseCommand, BaseCommandExecutor, BaseCommandResult
from app.yards_py.domain.entities.player_season import PlayerSeason
from app.yards_py.domain.repositories.player_season_repository import PlayerSeasonRepository, create_player_season_repository
from app.yards_py.domain.repositories.public_repository import PublicRepository, create_public_repository
from fastapi import Depends
from strivelogger import StriveLogger

from ....yards_py.domain.entities.player_game import GameResult, PlayerGame
from ....yards_py.domain.entities.stats import Stats
from ....yards_py.domain.stores.boxscore_store import BoxscoreStore, create_boxscore_store
from ....yards_py.domain.stores.system_schedule_store import SystemScheduleStore, create_system_schedule_store


class RecalcSeasonStatsCommand(BaseCommand):
    completed_week_number: int


class RecalcSeasonStatsResult(BaseCommandResult[RecalcSeasonStatsCommand]):
    updated_players: List[PlayerSeason]


class RecalcSeasonStatsCommandExecutor(BaseCommandExecutor[RecalcSeasonStatsCommand, RecalcSeasonStatsResult]):
    def __init__(
        self,
        public_repo: PublicRepository,
        # player_game_repo: PlayerGameRepository,
        player_season_repo: PlayerSeasonRepository,
        boxscore_store: BoxscoreStore,
        system_schedule_store: SystemScheduleStore,
    ):
        self.public_repo = public_repo
        # self.player_game_repo = player_game_repo
        self.player_season_repo = player_season_repo
        self.boxscore_store = boxscore_store
        self.system_schedule_store = system_schedule_store

    def on_execute(self, command: RecalcSeasonStatsCommand) -> RecalcSeasonStatsResult:
        state = self.public_repo.get_state()
        schedule_week = self.system_schedule_store.get_schedule_week(state.current_season, command.completed_week_number)

        if not schedule_week:
            StriveLogger.error(f"Could not find schedule week {command.completed_week_number} for season {state.current_season}")
            raise Exception(f"Could not find schedule week {command.completed_week_number} for season {state.current_season}")

        updated_players = list()

        for game in schedule_week.games:
            boxscore = self.boxscore_store.get_boxscore(state.current_season, game.game_id)

            if not boxscore:
                raise Exception(f"Could not find boxscore for game {game.game_id}")

            for player_stats in boxscore.player_stats.values():
                game_stats = Stats(**player_stats.model_dump())
                player_game = PlayerGame(
                    player_id=player_stats.player.player_id,
                    game_id=game.game_id,
                    week_number=game.week,
                    stats=game_stats,
                    game_result=GameResult.create(boxscore.game, player_stats.player.team_abbr),
                )

                player_season = self.player_season_repo.get(state.current_season, player_stats.player.player_id)

                if not player_season:
                    player_season = PlayerSeason.create(state.current_season, player_stats.player.player_id, [player_game])

                updated_players.append(player_season)
                self.player_season_repo.set(state.current_season, player_season)

        return RecalcSeasonStatsResult(command=command, updated_players=updated_players)


def create_recalc_season_stats_command_executor(
    public_repo: PublicRepository = Depends(create_public_repository),
    player_season_repo: PlayerSeasonRepository = Depends(create_player_season_repository),
    boxscore_store: BoxscoreStore = Depends(create_boxscore_store),
    system_schedule_store: SystemScheduleStore = Depends(create_system_schedule_store),
):
    return RecalcSeasonStatsCommandExecutor(
        public_repo=public_repo,
        player_season_repo=player_season_repo,
        boxscore_store=boxscore_store,
        system_schedule_store=system_schedule_store,
    )
