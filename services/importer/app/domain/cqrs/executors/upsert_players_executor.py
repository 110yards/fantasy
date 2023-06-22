import uuid
from datetime import datetime

from fastapi import Depends
from strivelogger import StriveLogger

from app.config.settings import Settings, get_settings
from app.domain.cqrs.command_result import CommandResult
from app.domain.cqrs.commands.upsert_players_command import UpsertPlayersCommand
from app.domain.models.player import Player, Team
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
            return CommandResult.failure("Failed to load schedule")

        if len(players) == 0:
            StriveLogger.error("No players found")
            return CommandResult.failure("No players found")

        StriveLogger.info("Getting existing players")
        existing_players = self.store.get_players(datetime.now().year)
        existing_players = {player.tsn_id: player for player in existing_players.values()}

        to_save: list[Player] = []

        # tightly coupled to TSN here
        for player in players:
            existing_player = existing_players.get(player.tsn_id)
            if existing_player:
                player.player_id = existing_player.player_id
                existing_players.pop(player.tsn_id)  # remove from existing so we know anyone left is a free agent now
                if existing_player.hash() != player.hash():
                    StriveLogger.info(f"Player changed: {player.full_name()} ({player.team.abbreviation})")
                    to_save.append(player)
            else:
                player.player_id = uuid.uuid4().hex
                StriveLogger.info(f"New player: {player.full_name()} ({player.team.abbreviation})")
                to_save.append(player)

        for player in existing_players.values():
            if player.team != Team.free_agent():
                player.team = Team.free_agent()
                StriveLogger.info(f"Player became free agent: {player.full_name()}")
                to_save.append(player)

        if len(to_save) == 0:
            StriveLogger.info("No changes to players")
            return CommandResult.success(data=existing_players)

        try:
            for player in to_save:
                self.store.save_player(datetime.now().year, player)
        except Exception as e:
            StriveLogger.error("Failed to save players", exc_info=e)
            return CommandResult.failure("Failed to save players")

        message = f"Saved {len(to_save)} players"
        return CommandResult.success(message=message, data=to_save)


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
