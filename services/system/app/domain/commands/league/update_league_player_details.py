
from typing import List, Optional

from yards_py.domain.entities.league_position import LeaguePosition
from yards_py.domain.repositories.league_roster_repository import LeagueRosterRepository, create_league_roster_repository
from yards_py.core.logging import Logger
from yards_py.domain.repositories.league_owned_player_repository import LeagueOwnedPlayerRepository, create_league_owned_player_repository
from yards_py.domain.entities.player import Player

from yards_py.core.base_command_executor import (BaseCommand, BaseCommandExecutor,
                                                 BaseCommandResult)
from fastapi import Depends
from firebase_admin import firestore


def create_update_league_player_details_command_executor(
    league_owned_player_repo: LeagueOwnedPlayerRepository = Depends(create_league_owned_player_repository),
    league_roster_repo: LeagueRosterRepository = Depends(create_league_roster_repository),
):
    return UpdateLeaguePlayerDetailsCommandExecutor(
        league_roster_repo=league_roster_repo,
        league_owned_player_repo=league_owned_player_repo
    )


class UpdateLeaguePlayerDetailsCommand(BaseCommand):
    league_id: Optional[str]
    player: Player


class UpdateLeaguePlayerDetailsResult(BaseCommandResult[UpdateLeaguePlayerDetailsCommand]):
    pass


class UpdateLeaguePlayerDetailsCommandExecutor(BaseCommandExecutor[UpdateLeaguePlayerDetailsCommand, UpdateLeaguePlayerDetailsResult]):

    def __init__(
        self,
        league_owned_player_repo: LeagueOwnedPlayerRepository,
        league_roster_repo: LeagueRosterRepository,
    ):
        self.league_owned_player_repo = league_owned_player_repo
        self.league_roster_repo = league_roster_repo

    def on_execute(self, command: UpdateLeaguePlayerDetailsCommand) -> UpdateLeaguePlayerDetailsResult:

        @firestore.transactional
        def update(transaction):
            owner = self.league_owned_player_repo.get(command.league_id, command.player.id, transaction)
            if not owner:
                # ignore and ack message, no one owns this player
                return UpdateLeaguePlayerDetailsResult(command=command)

            roster = self.league_roster_repo.get(command.league_id, owner.owner_id, transaction)

            positions: List[LeaguePosition] = []

            for position_id in roster.positions:
                position = roster.positions[position_id]
                if position.player and position.player.id == command.player.id:
                    positions.append(position)

            if len(positions) == 0:
                # something is messed up, the owned players list says someone owns this guy,
                # but we couldn't find him in that roster
                Logger.error("League owned player list / league roster mismatch", extra={
                    "league_id": command.league_id,
                    "player_id": command.player.id,
                    "owner_id": owner.id,
                })
                # but, I don't want this message to stick around forever.
                return UpdateLeaguePlayerDetailsResult(command=command)

            if len(positions) > 1:
                # how is this guy in two spots at once?
                Logger.error("League owned player list / duplicate on league roster", extra={
                    "league_id": command.league_id,
                    "player_id": command.player.id,
                    "owner_id": owner.id,
                })
                # should probably make this a really visible error - the players may let me know too though.
                # I'll still update this player since I'll use a loop

            for position in positions:
                position.player = command.player

            self.league_roster_repo.set(command.league_id, roster, transaction)

            return UpdateLeaguePlayerDetailsResult(command=command)

        transaction = self.league_owned_player_repo.firestore.create_transaction()
        return update(transaction)
