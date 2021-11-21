

from api.app.domain.repositories.game_repository import GameRepository, create_game_repository
from api.app.domain.commands.league.calculate_season_score import CalculateSeasonScoreCommand
from api.app.core.logging import Logger
from api.app.domain.entities.player import Player
from api.app.config.config import Settings, get_settings
from api.app.domain.repositories.player_repository import PlayerRepository, create_player_repository
from api.app.domain.enums.league_command_type import LeagueCommandType
from api.app.domain.services.league_command_push_data import LeagueCommandPushData
from api.app.domain.topics import LEAGUE_COMMAND_TOPIC
from typing import List
from api.app.core.publisher import Publisher, create_publisher
from api.app.domain.repositories.public_repository import PublicRepository, create_public_repository
from fastapi import Depends
from api.app.core.annotate_args import annotate_args
from api.app.core.base_command_executor import BaseCommand, BaseCommandResult, BaseCommandExecutor


def create_end_of_week_command_executor(
    public_repo: PublicRepository = Depends(create_public_repository),
    publisher: Publisher = Depends(create_publisher),
    settings: Settings = Depends(get_settings),
    player_repo: PlayerRepository = Depends(create_player_repository),
    game_repo: GameRepository = Depends(create_game_repository),
):
    return EndOfWeekCommandExecutor(
        public_repo=public_repo,
        publisher=publisher,
        settings=settings,
        player_repo=player_repo,
        game_repo=game_repo
    )


@annotate_args
class EndOfWeekCommand(BaseCommand):
    pass


@annotate_args
class EndOfWeekResult(BaseCommandResult[EndOfWeekCommand]):
    updated_players: List[Player]


class EndOfWeekCommandExecutor(BaseCommandExecutor[EndOfWeekCommand, EndOfWeekResult]):
    def __init__(
        self,
        publisher: Publisher,
        settings: Settings,
        player_repo: PlayerRepository,
        public_repo: PublicRepository,
        game_repo: GameRepository,
    ):
        self.publisher = publisher
        self.settings = settings
        self.player_repo = player_repo
        self.public_repo = public_repo
        self.game_repo = game_repo

    def on_execute(self, command: EndOfWeekCommand) -> EndOfWeekResult:

        # @firestore.transactional
        # def end_of_week(transaction: Transaction) -> EndOfWeekResult:
        season = self.settings.current_season
        # current_week = self.public_repo.get_state().current_week
        # completed_week = current_week - 1
        # completed_games = self.game_repo.for_week(season, completed_week)
        # completed_game_ids = [g.id for g in completed_games]

        if self.public_repo.get_switches().enable_score_testing:
            season = 2019
            Logger.warn("SCORE TESTING SWITCH IS ENABLED")

        players = self.player_repo.get_all(season)
        # players = [self.player_repo.get(season, "111244")]

        updated_players = []
        for player in players:
            if not player.game_stats:
                continue

            # Not ideal - might need to be revisited, but this missed the players on bye.
            # Maybe can be restored after being run once?
            # player_games_ids = list(player.game_stats.keys())
            # player_games_ids.sort()

            # last_player_game_id = player_games_ids[-1]
            # if last_player_game_id not in completed_game_ids:
            #     continue

            player.recalc_season_stats()
            updated_players.append(player)
            self.player_repo.set(season, player)

        # return EndOfWeekResult(command=command, updated_players=updated_players)

        # transaction = self.player_repo.firestore.create_transaction()
        # result: EndOfWeekResult = end_of_week(transaction)

        # if result.success:
        command = CalculateSeasonScoreCommand()
        payload = LeagueCommandPushData(command_type=LeagueCommandType.CALCULATE_SEASON_SCORE, command_data=command.dict())
        self.publisher.publish(payload, LEAGUE_COMMAND_TOPIC)

        return EndOfWeekResult(command=command, updated_players=updated_players)
