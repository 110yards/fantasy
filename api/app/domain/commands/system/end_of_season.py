

# from api.app.domain.entities.season_summary import SeasonSummary
# from api.app.domain.enums.draft_state import DraftState
# from api.app.domain.repositories.game_repository import GameRepository, create_game_repository
# from api.app.domain.commands.league.calculate_season_score import CalculateSeasonScoreCommand
# from api.app.core.logging import Logger
# from api.app.domain.entities.player import Player
# from api.app.config.config import Settings, get_settings
# from api.app.domain.repositories.league_config_repository import LeagueConfigRepository, create_league_config_repository
# from api.app.domain.repositories.league_repository import LeagueRepository, create_league_repository
# from api.app.domain.repositories.league_roster_repository import LeagueRosterRepository, create_league_roster_repository
# from api.app.domain.repositories.player_repository import PlayerRepository, create_player_repository
# from api.app.domain.enums.league_command_type import LeagueCommandType
# from api.app.domain.services.league_command_push_data import LeagueCommandPushData
# from api.app.domain.topics import LEAGUE_COMMAND_TOPIC
# from typing import List, Optional
# from api.app.core.publisher import Publisher, create_publisher
# from api.app.domain.repositories.public_repository import PublicRepository, create_public_repository
# from fastapi import Depends
# from api.app.core.annotate_args import annotate_args
# from api.app.core.base_command_executor import BaseCommand, BaseCommandResult, BaseCommandExecutor


# def create_end_of_season_command_executor(
#     publisher: Publisher = Depends(create_publisher),
#     settings: Settings = Depends(get_settings),
#     league_repo: LeagueRepository = Depends(create_league_repository),
#     league_config_repo: LeagueConfigRepository = Depends(create_league_config_repository),
#     league_roster_repo: LeagueRosterRepository = Depends(create_league_roster_repository),
# ):
#     return EndOfSeasonCommandExecutor(
#         publisher=publisher,
#         settings=settings,
#         league_repo=league_repo,
#         league_config_repo=league_config_repo,
#         league_roster_repo=league_roster_repo,
#     )


# @annotate_args
# class EndOfSeasonCommand(BaseCommand):
#     league_id: Optional[str]


# @annotate_args
# class EndOfSeasonResult(BaseCommandResult[EndOfSeasonCommand]):
#     updated_players: List[Player]


# class EndOfSeasonCommandExecutor(BaseCommandExecutor[EndOfSeasonCommand, EndOfSeasonResult]):
#     def __init__(
#         self,
#         publisher: Publisher,
#         settings: Settings,
#         league_repo: LeagueRepository,
#         league_config_repo: LeagueConfigRepository,
#         league_roster_repo: LeagueRosterRepository,
#     ):
#         self.publisher = publisher
#         self.settings = settings
#         self.league_repo = league_repo
#         self.league_config_repo = league_config_repo
#         self.league_roster_repo = league_roster_repo

#     def on_execute(self, command: EndOfSeasonCommand) -> EndOfSeasonResult:

#         if command.league_id:
#             leagues = [self.league_repo.get(command.league_id)]
#         else:
#             leagues = self.league_repo.get_all()

#         season = self.settings.current_season

#         # For all leagues which have drafted
#         for league in leagues:
#             if league.draft_state != DraftState.COMPLETE:
#                 continue

#             schedule = self.league_config_repo.get_schedule_config(league.id)
#             rosters = self.league_roster_repo.get_all(league.id)
#             summary = SeasonSummary.create_from_schedule(season, schedule, rosters)
#             # TODO: save it
#             return summary

#         return EndOfSeasonResult(command=command)
