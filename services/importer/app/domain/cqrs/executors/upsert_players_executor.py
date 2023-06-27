from fastapi import Depends
from strivelogger import StriveLogger

from app.config.settings import Settings, get_settings
from app.domain.cqrs.command_result import CommandResult
from app.domain.cqrs.commands.upsert_players_command import UpsertPlayersCommand
from app.domain.models.player import Player
from app.domain.services.player_service import PlayerService, create_player_service
from app.domain.store.player_store import PlayerStore, create_player_store


class UpsertPlayersExecutor:
    def __init__(self, settings: Settings, store: PlayerStore, service: PlayerService):
        self.settings = settings
        self.service = service
        self.store = store

    def execute(self, command: UpsertPlayersCommand) -> CommandResult:
        try:
            players = self.service.get_players()
        except Exception as e:
            StriveLogger.error("Failed to load players", exc_info=e)
            return CommandResult.failure_result("Failed to load schedule")

        if len(players) == 0:
            StriveLogger.error("No players found")
            return CommandResult.failure_result("No players found")

        StriveLogger.info("Getting existing players")
        existing_players = self.store.get_players()

        auto_accept_all = len(existing_players) == 0
        if auto_accept_all:
            StriveLogger.info("No existing players, auto accepting all")

        to_update: list[Player] = []
        new_players: list[Player] = []

        for player in players:
            existing_player = existing_players.get(player.player_id)
            if existing_player:
                existing_players.pop(player.player_id)  # remove from existing so we know anyone left is a free agent now
                if existing_player.hash() != player.hash():
                    StriveLogger.info(f"Player changed: {player.full_name} ({player.team_abbr or 'FA'})")
                    to_update.append(player)
            else:
                StriveLogger.info(f"New player: {player.full_name} ({player.team_abbr or 'FA'})")
                if auto_accept_all:
                    to_update.append(player)
                else:
                    new_players.append(player)

        # anyone left in existing_players is now a free agent
        for player in existing_players.values():
            if player.team_abbr is not None:
                player.team_abbr = None
                StriveLogger.info(f"Player became free agent: {player.full_name}")
                to_update.append(player)

        try:
            if len(to_update) == 0:
                StriveLogger.info("No players to update")
            else:
                StriveLogger.info(f"Updating {len(to_update)} players")
                for player in to_update:
                    self.store.save_player(player)
        except Exception as e:
            StriveLogger.error("Failed to update players", exc_info=e)
            return CommandResult.failure_result("Failed to save players")

        try:
            if len(new_players) == 0:
                StriveLogger.info("No new players to approve")
            else:
                StriveLogger.info(f"Adding {len(new_players)} new players for approval")
                self.store.save_players_for_approval(new_players)
        except Exception as e:
            StriveLogger.error("Failed to save new players for approval", exc_info=e)
            return CommandResult.failure_result("Failed to save new players for approval")

        message = f"Updated {len(to_update)} players, added {len(new_players)} players for approval"
        return CommandResult.success_result(message=message, data=to_update)


def create_upsert_players_executor(
    settings: Settings = Depends(get_settings),
    service: PlayerService = Depends(create_player_service),
    store: PlayerStore = Depends(create_player_store),
) -> UpsertPlayersExecutor:
    return UpsertPlayersExecutor(
        settings=settings,
        service=service,
        store=store,
    )
