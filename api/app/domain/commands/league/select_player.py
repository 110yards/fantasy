
from typing import Optional
from yards_py.domain.entities.draft import DraftSlot
from yards_py.domain.entities.league import League
from api.app.domain.repositories.state_repository import StateRepository, create_state_repository
from api.app.domain.services.draft_service import DraftService, create_draft_service
from api.app.domain.repositories.league_repository import LeagueRepository, create_league_repository
from api.app.domain.enums.draft_type import DraftType
from api.app.domain.repositories.league_roster_repository import LeagueRosterRepository, create_league_roster_repository
from api.app.domain.services.notification_service import NotificationService, create_notification_service
from api.app.domain.services.roster_player_service import RosterPlayerService, create_roster_player_service
from api.app.domain.repositories.player_repository import PlayerRepository, create_player_repository
from api.app.domain.repositories.league_owned_player_repository import LeagueOwnedPlayerRepository, create_league_owned_player_repository
from api.app.domain.repositories.league_config_repository import LeagueConfigRepository, create_league_config_repository
from fastapi import Depends
from yards_py.core.annotate_args import annotate_args
from yards_py.core.base_command_executor import BaseCommand, BaseCommandResult, BaseCommandExecutor
from firebase_admin import firestore


def create_select_player_command_executor(
    state_repo: StateRepository = Depends(create_state_repository),
    league_config_repo: LeagueConfigRepository = Depends(create_league_config_repository),
    league_owned_player_repo: LeagueOwnedPlayerRepository = Depends(create_league_owned_player_repository),
    player_repo: PlayerRepository = Depends(create_player_repository),
    roster_player_service: RosterPlayerService = Depends(create_roster_player_service),
    league_roster_repo: LeagueRosterRepository = Depends(create_league_roster_repository),
    league_repo: LeagueRepository = Depends(create_league_repository),
    draft_service: DraftService = Depends(create_draft_service),
    notification_service: NotificationService = Depends(create_notification_service),
):
    return SelectPlayerCommandExecutor(
        state_repo,
        league_config_repo,
        league_owned_player_repo,
        player_repo,
        roster_player_service,
        league_roster_repo,
        league_repo,
        draft_service,
        notification_service,
    )


@annotate_args
class SelectPlayerCommand(BaseCommand):
    pick_number: int
    roster_id: str
    league_id: str
    player_id: str


@annotate_args
class SelectPlayerResult(BaseCommandResult[SelectPlayerCommand]):
    league: Optional[League]
    slot: Optional[DraftSlot]
    next_slot: Optional[DraftSlot]
    draft_complete: bool = False


class SelectPlayerCommandExecutor(BaseCommandExecutor[SelectPlayerCommand, SelectPlayerResult]):

    def __init__(
        self,
        state_repo: StateRepository,
        league_config_repo: LeagueConfigRepository,
        league_owned_player_repo: LeagueOwnedPlayerRepository,
        player_repo: PlayerRepository,
        roster_player_service: RosterPlayerService,
        league_roster_repo: LeagueRosterRepository,
        league_repo: LeagueRepository,
        draft_service: DraftService,
        notification_service: NotificationService,
    ):
        self.state_repo = state_repo
        self.league_config_repo = league_config_repo
        self.league_owned_player_repo = league_owned_player_repo
        self.player_repo = player_repo
        self.roster_player_service = roster_player_service
        self.league_roster_repo = league_roster_repo
        self.league_repo = league_repo
        self.draft_service = draft_service
        self.notification_service = notification_service

    def on_execute(self, command: SelectPlayerCommand) -> SelectPlayerResult:

        existing = self.league_owned_player_repo.get(command.league_id, command.player_id)

        if existing:
            return SelectPlayerResult(command=command, error="Player has already been drafted")

        state = self.state_repo.get()
        player = self.player_repo.get(state.current_season, command.player_id)

        if not player:
            return SelectPlayerResult(command=command, error="Player does not exist")

        pick_index = command.pick_number - 1

        @firestore.transactional
        def update(transaction):
            draft = self.league_config_repo.get_draft(command.league_id, transaction)

            if len(draft.slots) < command.pick_number:
                return SelectPlayerResult(command=command, error="Invalid draft slot")

            slot = draft.slots[pick_index]

            if slot.completed:
                return SelectPlayerResult(command=command, error="Draft slot has already been used")

            if draft.draft_type != DraftType.COMMISSONER and slot.roster_id != command.roster_id:
                return SelectPlayerResult(command=command, error="It's not your turn")

            roster = self.league_roster_repo.get(command.league_id, command.roster_id, transaction)
            potential_position = self.roster_player_service.find_position_for(player, roster)

            if not potential_position:
                return SelectPlayerResult(command=command, error=f"There is no space on roster for a {player.position.display_name()}")

            slot.player = player

            league = self.league_repo.get(command.league_id)
            slot.completed = True

            if draft.draft_type == DraftType.COMMISSONER:
                slot.roster_id = command.roster_id

            message = f"{roster.name} selected {player.display_name}"
            slot.result = message
            draft.draft_events.insert(0, f"Pick #{slot.pick_number} - {message}")

            success, error = self.roster_player_service.assign_player_to_roster(command.league_id, roster, player, transaction)
            if not success:
                return SelectPlayerResult(command=command, error=error)

            draft_complete = self.draft_service.was_last_pick(draft, command.pick_number)
            next_slot = None

            if draft_complete:
                self.draft_service.complete(draft, league, transaction)
            else:
                self.league_config_repo.set_draft(command.league_id, draft, transaction)
                next_slot = draft.slots[pick_index + 1]

            return SelectPlayerResult(command=command, league=league, slot=slot, next_slot=next_slot, draft_complete=draft_complete)

        transaction = self.league_config_repo.firestore.create_transaction()
        result = update(transaction)

        if result.success:
            message = f"Pick #{result.slot.pick_number}: {result.slot.result}."
            if result.draft_complete:
                message += "\n\nThe draft has ended. Good luck!"
            else:
                modifier = " "
                if result.next_slot.roster_id == command.roster_id:
                    modifier = " still "
                next_roster = self.league_roster_repo.get(command.league_id, result.next_slot.roster_id)

                if next_roster:
                    message += f" {next_roster.name} is{modifier}on the clock."

            self.notification_service.send_draft_event(result.league, message)

        return result
