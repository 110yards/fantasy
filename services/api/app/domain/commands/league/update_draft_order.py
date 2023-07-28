from typing import List, Optional

from fastapi import Depends
from firebase_admin import firestore

from app.core.annotate_args import annotate_args
from app.core.base_command_executor import BaseCommand, BaseCommandExecutor, BaseCommandResult
from app.domain.entities.draft import DraftOrder
from app.domain.entities.league import League
from app.domain.enums.draft_state import DraftState
from app.domain.repositories.league_repository import LeagueRepository, create_league_repository
from app.domain.repositories.league_roster_repository import LeagueRosterRepository, create_league_roster_repository


def create_update_draft_order_command_executor(
    league_repo: LeagueRepository = Depends(create_league_repository),
    league_roster_repo: LeagueRosterRepository = Depends(create_league_roster_repository),
):
    return UpdateDraftOrderCommandExecutor(league_repo, league_roster_repo)


@annotate_args
class UpdateDraftOrderCommand(BaseCommand):
    league_id: Optional[str]
    draft_order: List[DraftOrder]


@annotate_args
class UpdateDraftOrderResult(BaseCommandResult[UpdateDraftOrderCommand]):
    league: Optional[League]


class UpdateDraftOrderCommandExecutor(BaseCommandExecutor[UpdateDraftOrderCommand, UpdateDraftOrderResult]):
    def __init__(self, league_repo: LeagueRepository, league_roster_repo: LeagueRosterRepository):
        self.league_repo = league_repo
        self.league_roster_repo = league_roster_repo

    def on_execute(self, command: UpdateDraftOrderCommand) -> UpdateDraftOrderResult:
        @firestore.transactional
        def update(transaction):
            league = self.league_repo.get(command.league_id, transaction)

            if league.draft_state != DraftState.NOT_STARTED:
                return UpdateDraftOrderResult(command=command, error="Draft has already started")

            rosters = self.league_roster_repo.get_all(command.league_id)
            roster_ids = [roster.id for roster in rosters]

            # this resolve a bug caused by removing and re-adding rosters
            added = set()
            draft_order = []
            for item in command.draft_order:
                if item.roster_id not in added and item.roster_id in roster_ids:
                    draft_order.append(item)
                    added.add(item.roster_id)

            league.draft_order = draft_order

            self.league_repo.update(league, transaction)

            return UpdateDraftOrderResult(command=command, league=league)

        transaction = self.league_repo.firestore.create_transaction()
        return update(transaction)
