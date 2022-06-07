
from typing import Optional
from api.app.domain.enums.draft_type import DraftType
from yards_py.domain.entities.draft import DraftSlot
from api.app.domain.repositories.league_repository import LeagueRepository, create_league_repository
from api.app.domain.services.notification_service import NotificationService, create_notification_service
from api.app.domain.services.roster_player_service import RosterPlayerService, create_roster_player_service
from api.app.domain.repositories.league_roster_repository import LeagueRosterRepository, create_league_roster_repository
from api.app.domain.repositories.league_config_repository import LeagueConfigRepository, create_league_config_repository
from fastapi import Depends
from yards_py.core.annotate_args import annotate_args
from yards_py.core.base_command_executor import BaseCommand, BaseCommandResult, BaseCommandExecutor
from firebase_admin import firestore


def create_undo_last_draft_pick_command_executor(
    league_config_repo: LeagueConfigRepository = Depends(create_league_config_repository),
    league_roster_repo: LeagueRosterRepository = Depends(create_league_roster_repository),
    roster_player_service: RosterPlayerService = Depends(create_roster_player_service),
    notification_service: NotificationService = Depends(create_notification_service),
    league_repo: LeagueRepository = Depends(create_league_repository),
):
    return UndoLastDraftPickCommandExecutor(
        league_config_repo,
        league_roster_repo,
        roster_player_service,
        notification_service=notification_service,
        league_repo=league_repo
    )


@annotate_args
class UndoLastDraftPickCommand(BaseCommand):
    league_id: str


@annotate_args
class UndoLastDraftPickResult(BaseCommandResult[UndoLastDraftPickCommand]):
    draft_event: Optional[str]


class UndoLastDraftPickCommandExecutor(BaseCommandExecutor[UndoLastDraftPickCommand, UndoLastDraftPickResult]):

    def __init__(
            self,
            league_config_repo: LeagueConfigRepository,
            league_roster_repo: LeagueRosterRepository,
            roster_player_service: RosterPlayerService,
            league_repo: LeagueRepository,
            notification_service: NotificationService,
    ):
        self.league_config_repo = league_config_repo
        self.league_roster_repo = league_roster_repo
        self.roster_player_service = roster_player_service
        self.league_repo = league_repo
        self.notification_service = notification_service

    def on_execute(self, command: UndoLastDraftPickCommand) -> UndoLastDraftPickResult:
        @firestore.transactional
        def update(transaction):
            draft = self.league_config_repo.get_draft(command.league_id, transaction)

            last_slot_index = -1
            for slot in draft.slots:
                if slot.completed:
                    last_slot_index += 1
                else:
                    break

            if last_slot_index == -1:
                return UndoLastDraftPickResult(command=command, error="No picks have been completed yet")

            last_slot = draft.slots[last_slot_index]
            current_slot = draft.slots[last_slot_index + 1]  # afterlast pick issue? or will the draft just be done at that point?

            last_winner = self.league_roster_repo.get(command.league_id, last_slot.roster_id, transaction)

            if draft.draft_type == DraftType.AUCTION:
                last_winner.draft_budget += last_slot.bid

            self.roster_player_service.remove_player_from_roster(command.league_id, last_winner, last_slot.player.id, transaction)

            self.reset_slot(last_slot, draft.draft_type)
            self.reset_slot(current_slot, draft.draft_type)

            event = f"Commissioner undid pick #{last_slot.pick_number}"
            draft.draft_events.insert(0, event)

            self.league_roster_repo.set(command.league_id, last_winner, transaction)
            self.league_config_repo.set_draft(command.league_id, draft, transaction)

            return UndoLastDraftPickResult(command=command, draft_event=event)

        transaction = self.league_config_repo.firestore.create_transaction()
        result = update(transaction)

        if result.success:
            league = self.league_repo.get(command.league_id)
            self.notification_service.send_draft_event(league, result.draft_event)

        return result

    def reset_slot(self, slot: DraftSlot, draft_type: DraftType):
        slot.completed = False
        slot.player = None
        slot.bid = None
        slot.bidder_index = None
        slot.result = None

        if draft_type == DraftType.AUCTION:
            slot.roster_id = None

            for bidder in slot.bidders:
                bidder.outbid = False
                bidder.passed = False
                bidder.in_eligible = False
