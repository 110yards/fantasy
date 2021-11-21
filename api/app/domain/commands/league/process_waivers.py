
from api.app.domain.entities.league_week import LeagueWeek
from api.app.domain.repositories.state_repository import StateRepository, create_state_repository
from api.app.domain.repositories.league_week_repository import LeagueWeekRepository, create_league_week_repository
from api.app.domain.services.waiver_service import WaiverService, create_waiver_service
from api.app.domain.entities.waiver_bid import WaiverBidResult
from api.app.domain.repositories.league_repository import LeagueRepository, create_league_repository
from api.app.domain.repositories.league_roster_repository import LeagueRosterRepository, create_league_roster_repository
from typing import Optional
from fastapi import Depends
from api.app.core.annotate_args import annotate_args
from api.app.core.base_command_executor import BaseCommand, BaseCommandResult, BaseCommandExecutor
from firebase_admin import firestore


def create_process_waivers_command_executor(
    state_repo: StateRepository = Depends(create_state_repository),
    league_roster_repo: LeagueRosterRepository = Depends(create_league_roster_repository),
    league_repo: LeagueRepository = Depends(create_league_repository),
    waiver_service: WaiverService = Depends(create_waiver_service),
    league_week_repo: LeagueWeekRepository = Depends(create_league_week_repository),
):
    return ProcessWaiversCommandExecutor(
        state_repo=state_repo,
        league_roster_repo=league_roster_repo,
        league_repo=league_repo,
        waiver_service=waiver_service,
        league_week_repo=league_week_repo
    )


@annotate_args
class ProcessWaiversCommand(BaseCommand):
    league_id: Optional[str]


@annotate_args
class ProcessWaiversResult(BaseCommandResult[ProcessWaiversCommand]):
    pass


class ProcessWaiversCommandExecutor(BaseCommandExecutor[ProcessWaiversCommand, ProcessWaiversResult]):
    def __init__(
        self,
        state_repo: StateRepository,
        league_roster_repo: LeagueRosterRepository,
        league_repo: LeagueRepository,
        waiver_service: WaiverService,
        league_week_repo: LeagueWeekRepository,
    ):
        self.state_repo = state_repo
        self.league_roster_repo = league_roster_repo
        self.league_repo = league_repo
        self.waiver_service = waiver_service
        self.league_week_repo = league_week_repo

    def on_execute(self, command: ProcessWaiversCommand) -> ProcessWaiversResult:

        # don't lock the state
        state = self.state_repo.get()
        waiver_week = state.current_week - 1

        @firestore.transactional
        def process(transaction):
            league = self.league_repo.get(command.league_id, transaction)
            rosters = self.league_roster_repo.get_all(command.league_id, transaction)

            bids = self.waiver_service.process_bids(rosters)

            rosters = {roster.id: roster for roster in rosters}

            for bid in bids:
                if bid.result != WaiverBidResult.SuccessPending:
                    continue

                roster = rosters[bid.roster_id]
                self.waiver_service.apply_winning_bid(command.league_id, bid, roster, transaction)

            for roster in rosters.values():
                roster.processed_waiver_bids = roster.waiver_bids
                roster.waiver_bids = []

                self.league_roster_repo.set(command.league_id, roster, transaction)

            league_week = LeagueWeek(id=str(waiver_week), waiver_bids=bids)
            self.league_week_repo.set(command.league_id, league_week, transaction)

            league.waivers_active = False  # this is set to active in the calculate_results command executor
            self.league_repo.update(league, transaction)

        transaction = self.league_roster_repo.firestore.create_transaction()
        return process(transaction)
