from typing import Optional

from fastapi import Depends
from strivelogger import StriveLogger

from ....core.base_command_executor import BaseCommand, BaseCommandExecutor, BaseCommandResult
from ...entities.player_game import GameResult, PlayerGame
from ...entities.player_season import PlayerSeason
from ...entities.stats import Stats
from ...entities.system_schedule import SystemScheduleGame
from ...repositories.player_season_repository import PlayerSeasonRepository, create_player_season_repository
from ...repositories.public_repository import PublicRepository, create_public_repository
from ...stores.boxscore_store import BoxscoreStore, create_boxscore_store
from ...stores.system_schedule_store import SystemScheduleStore, create_system_schedule_store


class RecalcSeasonStatsCommand(BaseCommand):
    completed_week_number: Optional[int] = None
    full_season: bool = False


class RecalcSeasonStatsResult(BaseCommandResult[RecalcSeasonStatsCommand]):
    pass


class RecalcSeasonStatsCommandExecutor(BaseCommandExecutor[RecalcSeasonStatsCommand, RecalcSeasonStatsResult]):
    def __init__(
        self,
        public_repo: PublicRepository,
        player_season_repo: PlayerSeasonRepository,
        boxscore_store: BoxscoreStore,
        system_schedule_store: SystemScheduleStore,
    ):
        self.public_repo = public_repo
        self.player_season_repo = player_season_repo
        self.boxscore_store = boxscore_store
        self.system_schedule_store = system_schedule_store

    def on_execute(self, command: RecalcSeasonStatsCommand) -> RecalcSeasonStatsResult:
        if not command.completed_week_number and not command.full_season:
            raise Exception("Must provide either completed_week_number or full_season")

        state = self.public_repo.get_state()

        games = (
            self._get_full_season_games(state.current_season)
            if command.full_season
            else self._get_current_week_games(state.current_season, command.completed_week_number)
        )

        updated_players: dict[str, PlayerSeason] = {}

        for game in games:
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

                player_season = None
                if player_stats.player.player_id in updated_players:
                    player_season = updated_players[player_stats.player.player_id]

                if not player_season:
                    player_season = self.player_season_repo.get(state.current_season, player_stats.player.player_id)

                if not player_season:
                    player_season = PlayerSeason.create(state.current_season, player_stats.player.player_id, [player_game])
                else:
                    player_season.add_game(player_game)

                updated_players[player_stats.player.player_id] = player_season

        for player_season in updated_players.values():
            self.player_season_repo.set(state.current_season, player_season)

        return RecalcSeasonStatsResult(command=command)

    def _get_current_week_games(self, current_season: int, completed_week_number: int) -> list[SystemScheduleGame]:
        schedule_week = self.system_schedule_store.get_schedule_week(current_season, completed_week_number)

        if not schedule_week:
            StriveLogger.error(f"Could not find schedule week {completed_week_number} for season {current_season}")
            raise Exception(f"Could not find schedule week {completed_week_number} for season {current_season}")

        return schedule_week.games

    def _get_full_season_games(self, current_season: int) -> list[SystemScheduleGame]:
        schedule = self.system_schedule_store.get_schedule(current_season)

        games = list()

        for week in schedule.weeks.values():
            games.extend(week.games)

        return games


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
