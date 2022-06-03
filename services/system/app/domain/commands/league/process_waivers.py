
from yards_py.domain.entities.league import League
from yards_py.domain.entities.league_transaction import LeagueTransaction
from yards_py.domain.entities.league_week import LeagueWeek
from yards_py.domain.repositories.league_config_repository import LeagueConfigRepository, create_league_config_repository
from yards_py.domain.repositories.state_repository import StateRepository, create_state_repository
from yards_py.domain.repositories.league_week_repository import LeagueWeekRepository, create_league_week_repository
from yards_py.domain.services.notification_service import NotificationService, create_notification_service
from services.system.app.domain.services.waiver_service import WaiverService, create_waiver_service
from yards_py.domain.entities.waiver_bid import WaiverBid, WaiverBidResult
from yards_py.domain.repositories.league_repository import LeagueRepository, create_league_repository
from yards_py.domain.repositories.league_roster_repository import LeagueRosterRepository, create_league_roster_repository
from typing import List, Optional
from fastapi import Depends
from yards_py.core.base_command_executor import BaseCommand, BaseCommandResult, BaseCommandExecutor
from firebase_admin import firestore


def create_process_waivers_command_executor(
    state_repo: StateRepository = Depends(create_state_repository),
    league_roster_repo: LeagueRosterRepository = Depends(create_league_roster_repository),
    league_repo: LeagueRepository = Depends(create_league_repository),
    waiver_service: WaiverService = Depends(create_waiver_service),
    league_week_repo: LeagueWeekRepository = Depends(create_league_week_repository),
    notification_service: NotificationService = Depends(create_notification_service),
    league_config_repo: LeagueConfigRepository = Depends(create_league_config_repository),
):
    return ProcessWaiversCommandExecutor(
        state_repo=state_repo,
        league_roster_repo=league_roster_repo,
        league_repo=league_repo,
        waiver_service=waiver_service,
        league_week_repo=league_week_repo,
        notification_service=notification_service,
        league_config_repo=league_config_repo,
    )


class ProcessWaiversCommand(BaseCommand):
    league_id: Optional[str]


class ProcessWaiversResult(BaseCommandResult[ProcessWaiversCommand]):
    league: Optional[League]
    bids: Optional[List[WaiverBid]]
    transactions: Optional[List[LeagueTransaction]]


class ProcessWaiversCommandExecutor(BaseCommandExecutor[ProcessWaiversCommand, ProcessWaiversResult]):
    def __init__(
        self,
        state_repo: StateRepository,
        league_roster_repo: LeagueRosterRepository,
        league_repo: LeagueRepository,
        waiver_service: WaiverService,
        league_week_repo: LeagueWeekRepository,
        notification_service: NotificationService,
        league_config_repo: LeagueConfigRepository,
    ):
        self.state_repo = state_repo
        self.league_roster_repo = league_roster_repo
        self.league_repo = league_repo
        self.waiver_service = waiver_service
        self.league_week_repo = league_week_repo
        self.notification_service = notification_service
        self.league_config_repo = league_config_repo

    def on_execute(self, command: ProcessWaiversCommand) -> ProcessWaiversResult:

        # don't lock the state
        state = self.state_repo.get()
        waiver_week = state.current_week - 1

        @firestore.transactional
        def process(transaction) -> ProcessWaiversResult:
            league = self.league_repo.get(command.league_id, transaction)
            rosters = self.league_roster_repo.get_all(command.league_id, transaction)

            bids = self.waiver_service.process_bids(rosters)

            rosters = {roster.id: roster for roster in rosters}

            league_transactions = []

            for bid in bids:
                if bid.result != WaiverBidResult.SuccessPending:
                    continue

                roster = rosters[bid.roster_id]
                trx = self.waiver_service.apply_winning_bid(command.league_id, bid, roster, transaction)
                if trx:
                    league_transactions.extend(trx)

            for roster in rosters.values():
                roster.processed_waiver_bids = roster.waiver_bids
                roster.waiver_bids = []

                self.league_roster_repo.set(command.league_id, roster, transaction)

            league_week = LeagueWeek(id=str(waiver_week), waiver_bids=bids)
            self.league_week_repo.set(command.league_id, league_week, transaction)

            league.waivers_active = False  # this is set to active in the calculate_results command executor
            self.league_repo.update(league, transaction)

            return ProcessWaiversResult(command=command, league=league, bids=bids, transactions=league_transactions)

        transaction = self.league_roster_repo.firestore.create_transaction()
        result = process(transaction)

        if not result.success:
            return result

        message = ""
        for trx in result.transactions:
            message += f"{trx.message}\n"

        if message:
            message = f"Week {state.current_week} waivers complete\n\n" + message
        else:
            message = f"Waivers complete: no waiver claims made in week {state.current_week}."

        league_config = self.league_config_repo.get_schedule_config(command.league_id)
        last_playoff_week = league_config.first_playoff_week + league_config.playoff_type.weeks
        if state.current_week < last_playoff_week:
            self.notification_service.send_waiver_results(result.league, message)

        return result
