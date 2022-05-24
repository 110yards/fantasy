
from api.app.domain.repositories.league_transaction_repository import LeagueTransactionRepository, create_league_transaction_repository
from api.app.domain.entities.league_transaction import LeagueTransaction
from api.app.domain.repositories.user_league_repository import UserLeagueRepository, create_user_league_repository
from api.app.domain.enums.draft_state import DraftState
from api.app.domain.repositories.league_config_repository import LeagueConfigRepository, create_league_config_repository
from api.app.domain.repositories.league_repository import LeagueRepository, create_league_repository
from api.app.domain.repositories.league_roster_repository import LeagueRosterRepository, create_league_roster_repository
from typing import Optional
from fastapi import Depends
from api.app.core.annotate_args import annotate_args
from api.app.core.base_command_executor import BaseCommand, BaseCommandResult, BaseCommandExecutor
from api.app.core.publisher import Publisher, create_publisher
from firebase_admin import firestore


def create_update_roster_name_command_executor(
    league_roster_repo: LeagueRosterRepository = Depends(create_league_roster_repository),
    league_config_repo: LeagueConfigRepository = Depends(create_league_config_repository),
    league_repo: LeagueRepository = Depends(create_league_repository),
    user_league_repo: UserLeagueRepository = Depends(create_user_league_repository),
    publisher: Publisher = Depends(create_publisher),
    league_transaction_repo: LeagueTransactionRepository = Depends(create_league_transaction_repository),
):
    return UpdateRosterNameCommandExecutor(
        league_config_repo=league_config_repo,
        league_repo=league_repo,
        league_roster_repo=league_roster_repo,
        user_league_repo=user_league_repo,
        publisher=publisher,
        league_transaction_repo=league_transaction_repo,
    )


@annotate_args
class UpdateRosterNameCommand(BaseCommand):
    league_id: str
    roster_id: str
    roster_name: str
    current_user_id: Optional[str]


@annotate_args
class UpdateRosterNameResult(BaseCommandResult[UpdateRosterNameCommand]):
    pass


class UpdateRosterNameCommandExecutor(BaseCommandExecutor[UpdateRosterNameCommand, UpdateRosterNameResult]):

    def __init__(
        self,
        league_repo: LeagueRepository,
        league_roster_repo: LeagueRosterRepository,
        league_config_repo: LeagueConfigRepository,
        user_league_repo: UserLeagueRepository,
        publisher: Publisher,
        league_transaction_repo: LeagueTransactionRepository,
    ):
        self.league_repo = league_repo
        self.league_roster_repo = league_roster_repo
        self.league_config_repo = league_config_repo
        self.user_league_repo = user_league_repo
        self.publisher = publisher
        self.league_transaction_repo = league_transaction_repo

    def on_execute(self, command: UpdateRosterNameCommand) -> UpdateRosterNameResult:

        @firestore.transactional
        def update(transaction):
            league = self.league_repo.get(command.league_id, transaction)

            if not league:
                return UpdateRosterNameResult(command=command, error="League not found")

            self_change = command.roster_id == command.current_user_id
            is_commissioner = league.commissioner_id == command.current_user_id

            if not self_change and not is_commissioner:
                return UpdateRosterNameResult(command=command, error="Forbidden")

            commissioner_override = is_commissioner and not self_change

            if league.draft_state == DraftState.IN_PROGRESS:
                return UpdateRosterNameResult(command=command, error="You cannot change your roster name while the draft is in progress")

            roster = self.league_roster_repo.get(command.league_id, command.roster_id, transaction)

            if self_change and roster.name_changes_banned:
                return UpdateRosterNameResult(command=command, error="The commissioner has disabled name changes for your team")

            old_name = roster.copy().name

            if not roster:
                return UpdateRosterNameResult(command=command, error="Roster not found")

            if league.schedule_generated:
                schedule = self.league_config_repo.get_schedule_config(command.league_id, transaction)

            league_preview = self.user_league_repo.get(command.roster_id, command.league_id, transaction)

            if league.schedule_generated:
                for week in schedule.weeks:
                    for matchup in week.matchups:
                        if matchup.away and matchup.away.id == command.roster_id:
                            matchup.away.name = command.roster_name
                            # Issue #151 - weeks aren't created until after waivers are processed and only matter for waiver bids now
                            # updates = {"away.name": command.roster_name}
                            # self.league_week_matchup_repo.partial_update(command.league_id, week.week_number, matchup.id, updates, transaction)

                        if matchup.home and matchup.home.id == command.roster_id:
                            matchup.home.name = command.roster_name
                            # Issue #151 - weeks aren't created until after waivers are processed and only matter for waiver bids now
                            # updates = {"home.name": command.roster_name}
                            # self.league_week_matchup_repo.partial_update(command.league_id, week.week_number, matchup.id, updates, transaction)

                self.league_config_repo.set_schedule_config(command.league_id, schedule, transaction)

            if league_preview and league_preview.matchup:
                if league_preview.matchup.away and league_preview.matchup.away.id == command.roster_id:
                    updates = {"matchup.away.name": command.roster_name}
                    self.user_league_repo.partial_update(command.roster_id, command.league_id, updates, transaction)

                if league_preview.matchup.home and league_preview.matchup.home.id == command.roster_id:
                    updates = {"matchup.home.name": command.roster_name}
                    self.user_league_repo.partial_update(command.roster_id, command.league_id, updates, transaction)

            updates = {"name": command.roster_name}
            self.league_roster_repo.partial_update(command.league_id, command.roster_id, updates, transaction)

            league_transaction = LeagueTransaction.change_roster_name(
                command.league_id, command.roster_id, command.roster_name, old_name, commissioner_override)
            self.league_transaction_repo.create(command.league_id, league_transaction, transaction)

            return UpdateRosterNameResult(command=command)

        transaction = self.league_roster_repo.firestore.create_transaction()
        return update(transaction)
