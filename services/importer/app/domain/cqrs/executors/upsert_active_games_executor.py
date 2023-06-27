# from datetime import datetime

# from fastapi import Depends
# from strivelogger import StriveLogger

# from app.config.settings import Settings, get_settings
# from app.domain.cqrs.command_result import CommandResult
# from app.domain.cqrs.commands.upsert_active_games_command import (
#     UpsertActiveGamesCommand,
# )
# from app.domain.models.game import Game
# from app.domain.services.active_games_service import (
#     ActiveGamesService,
#     create_active_games_service,
# )
# from app.domain.store.boxscore_store import BoxscoreStore, create_boxscore_store


# class UpsertActiveGamesExecutor:
#     def __init__(self, settings: Settings, service: ActiveGamesService, store: BoxscoreStore):
#         self.settings = settings
#         self.service = service
#         self.store = store

#     def execute(self, command: UpsertActiveGamesCommand) -> CommandResult:
#         try:
#             games = self.service.get_games(command.hours)
#         except Exception as e:
#             StriveLogger.error("Failed to load games", exc_info=e)
#             return CommandResult.failure_result("Failed to load games")

#         if len(games) == 0:
#             StriveLogger.info("No games found")
#             return CommandResult.success()

#         to_update: list[Game] = []

#         for game in games:
#             existing_game = self.store.get_boxscore(datetime.now().year, game.game_id)
#             if existing_game is None or existing_game.hash() != game.hash():
#                 to_update.append(game)

#         if not to_update:
#             StriveLogger.info("No games have changed")
#             return CommandResult.success()

#         try:
#             StriveLogger.info(f"Saving {len(to_update)} games")
#             for game in to_update:
#                 self.store.save_boxscore(datetime.now().year, game)
#         except Exception as e:
#             StriveLogger.error("Failed to save game(s)", exc_info=e)
#             return CommandResult.failure_result("Failed to save game(s)")

#         StriveLogger.info("Games saved")
#         return CommandResult.success()


# def create_upsert_active_games_executor(
#     settings: Settings = Depends(get_settings),
#     service: ActiveGamesService = Depends(create_active_games_service),
#     store: BoxscoreStore = Depends(create_boxscore_store),
# ) -> UpsertActiveGamesExecutor:
#     return UpsertActiveGamesExecutor(
#         settings=settings,
#         store=store,
#         service=service,
#     )
