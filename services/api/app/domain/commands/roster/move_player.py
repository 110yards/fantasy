from fastapi import Depends
from firebase_admin import firestore

from app.core.annotate_args import annotate_args
from app.core.base_command_executor import BaseCommand, BaseCommandExecutor, BaseCommandResult
from app.domain.entities.league_transaction import LeagueTransaction
from app.domain.entities.player import Player
from app.domain.enums.position_type import PositionType
from app.domain.repositories.league_repository import LeagueRepository, create_league_repository
from app.domain.repositories.league_roster_repository import LeagueRosterRepository, create_league_roster_repository
from app.domain.repositories.league_transaction_repository import LeagueTransactionRepository, create_league_transaction_repository
from app.domain.repositories.public_repository import PublicRepository, create_public_repository
from app.domain.repositories.state_repository import StateRepository, create_state_repository


def create_move_player_command_executor(
    league_roster_repo: LeagueRosterRepository = Depends(create_league_roster_repository),
    state_repo: StateRepository = Depends(create_state_repository),
    public_repo: PublicRepository = Depends(create_public_repository),
    league_repo: LeagueRepository = Depends(create_league_repository),
    transaction_repo: LeagueTransactionRepository = Depends(create_league_transaction_repository),
):
    return MovePlayerCommandExecutor(
        league_roster_repo=league_roster_repo,
        state_repo=state_repo,
        public_repo=public_repo,
        league_repo=league_repo,
        transaction_repo=transaction_repo,
    )


@annotate_args
class MovePlayerCommand(BaseCommand):
    league_id: str
    roster_id: str
    player_id: str
    position_id: str


@annotate_args
class MovePlayerResult(BaseCommandResult[MovePlayerCommand]):
    pass


class MovePlayerCommandExecutor(BaseCommandExecutor[MovePlayerCommand, MovePlayerResult]):
    def __init__(
        self,
        league_roster_repo: LeagueRosterRepository,
        state_repo: StateRepository,
        public_repo: PublicRepository,
        league_repo: LeagueRepository,
        transaction_repo: LeagueTransactionRepository,
    ):
        self.league_roster_repo = league_roster_repo
        self.state_repo = state_repo
        self.public_repo = public_repo
        self.league_repo = league_repo
        self.transaction_repo = transaction_repo

    def on_execute(self, command: MovePlayerCommand) -> MovePlayerResult:
        scoreboard = self.public_repo.get_scoreboard()
        self.state_repo.get()

        @firestore.transactional
        def update(transaction):
            league = self.league_repo.get(command.league_id, transaction)

            if not league:
                return MovePlayerResult(command=command, error="League not found")

            self_change = command.roster_id == command.request_user_id
            is_commissioner = league.commissioner_id == command.request_user_id

            if not self_change and not is_commissioner:
                return MovePlayerResult(command=command, error="Forbidden")

            commissioner_override = not self_change and is_commissioner

            roster = self.league_roster_repo.get(command.league_id, command.roster_id, transaction)

            if not roster:
                return MovePlayerResult(command=command, error="Roster not found")

            current_position = roster.find_player_position(command.player_id)

            if not current_position:
                return MovePlayerResult(command=command, error="That player is not on your roster")

            if scoreboard.is_locked(current_position.player.team_abbr):
                return MovePlayerResult(command=command, error=f"{current_position.player.team_abbr} players are locked")

            target_position = roster.positions[command.position_id]
            if target_position.player and scoreboard.is_locked(target_position.player.team_abbr):
                return MovePlayerResult(command=command, error=f"{target_position.player.team_abbr} players are locked")

            player_to_move = current_position.player
            player_to_swap = target_position.player

            if not target_position.position_type.is_eligible_for(player_to_move.position):
                return MovePlayerResult(
                    command=command, error=f"{player_to_move.full_name} is not eligible for {target_position.position_type.display_name()} position"
                )

            if player_to_swap and not current_position.position_type.is_eligible_for(player_to_swap.position):
                return MovePlayerResult(
                    command=command, error=f"{player_to_swap.full_name} is not eligible for {current_position.position_type.display_name()} position"
                )

            if target_position.position_type == PositionType.bye and not scoreboard.is_team_on_bye(player_to_move.team_abbr):
                return MovePlayerResult(command=command, error=f"{player_to_move.team_abbr} is not on bye")

            if player_to_swap and current_position.position_type == PositionType.bye and not scoreboard.is_team_on_bye(player_to_swap.team_abbr):
                return MovePlayerResult(command=command, error=f"{player_to_swap.team_abbr} is not on bye")

            if target_position.position_type == PositionType.ir and not self.eligible_for_ir(player_to_move):
                return MovePlayerResult(command=command, error=f"{player_to_move.full_name} is not injured")

            if player_to_swap and current_position.position_type == PositionType.ir and not self.eligible_for_ir(player_to_swap):
                return MovePlayerResult(command=command, error=f"{player_to_swap.full_name} is not injured")

            target_position.player = player_to_move
            current_position.player = player_to_swap

            assert target_position.player.player_id == player_to_move.player_id

            if commissioner_override:
                trx = LeagueTransaction.commissioner_move_player(command.league_id, roster, player_to_move, current_position.name, target_position.name)
                self.transaction_repo.create(command.league_id, trx, transaction)

            if player_to_swap:
                assert current_position.player.player_id == player_to_swap.player_id

            if player_to_swap and commissioner_override:
                trx = LeagueTransaction.commissioner_move_player(command.league_id, roster, player_to_swap, target_position.name, current_position.name)
                self.transaction_repo.create(command.league_id, trx, transaction)

            self.league_roster_repo.update(command.league_id, roster, transaction)

            return MovePlayerResult(command=command)

        transaction = self.league_roster_repo.firestore.create_transaction()
        return update(transaction)

    def eligible_for_ir(self, player: Player) -> bool:
        enable_relaxed_ir = self.public_repo.get_switches().enable_relaxed_ir
        return enable_relaxed_ir or player.injury_status is not None
