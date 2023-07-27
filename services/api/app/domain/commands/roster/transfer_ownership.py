
from services.api.app.domain.repositories.league_transaction_repository import LeagueTransactionRepository, create_league_transaction_repository
from yards_py.domain.entities.league_transaction import LeagueTransaction
from services.api.app.domain.repositories.league_repository import LeagueRepository, create_league_repository
from services.api.app.domain.repositories.league_roster_repository import LeagueRosterRepository, create_league_roster_repository
from fastapi import Depends
from yards_py.core.base_command_executor import BaseCommand, BaseCommandResult, BaseCommandExecutor
from firebase_admin import firestore
from yards_py.domain.repositories.league_config_repository import LeagueConfigRepository, create_league_config_repository
from yards_py.domain.repositories.league_owned_player_repository import LeagueOwnedPlayerRepository, create_league_owned_player_repository
from yards_py.domain.repositories.league_week_matchup_repository import LeagueWeekMatchupRepository, create_league_week_matchup_repository
from yards_py.domain.repositories.public_repository import PublicRepository, create_public_repository
from yards_py.domain.repositories.user_league_repository import UserLeagueRepository, create_user_league_repository

from yards_py.domain.repositories.user_repository import UserRepository, create_user_repository


class TransferOwnershipCommand(BaseCommand):
    league_id: str
    roster_id: str
    new_owner_email: str


class TransferOwnershipResult(BaseCommandResult[TransferOwnershipCommand]):
    pass


class TransferOwnershipCommandExecutor(BaseCommandExecutor[TransferOwnershipCommand, TransferOwnershipResult]):

    def __init__(
        self,
        league_repo: LeagueRepository,
        league_roster_repo: LeagueRosterRepository,
        league_transaction_repo: LeagueTransactionRepository,
        user_repo: UserRepository,
        league_config_repo: LeagueConfigRepository,
        league_matchup_repo: LeagueWeekMatchupRepository,
        user_league_repo: UserLeagueRepository,
        owned_player_repo: LeagueOwnedPlayerRepository,
        public_repo: PublicRepository,
    ):
        self.league_repo = league_repo
        self.league_roster_repo = league_roster_repo
        self.league_transaction_repo = league_transaction_repo
        self.user_repo = user_repo
        self.league_config_repo = league_config_repo
        self.league_matchup_repo = league_matchup_repo
        self.user_league_repo = user_league_repo
        self.owned_player_repo = owned_player_repo
        self.public_repo = public_repo

    def on_execute(self, command: TransferOwnershipCommand) -> TransferOwnershipResult:

        new_owner = self.user_repo.get_by_email(command.new_owner_email)
        state = self.public_repo.get_state()

        if not new_owner:
            return TransferOwnershipResult(command=command, error="User not found")

        @firestore.transactional
        def update(transaction):

            league = self.league_repo.get(command.league_id, transaction)

            if not league:
                return TransferOwnershipResult(command=command, error="League not found")

            if not league.is_active_for_season(state.current_season):
                return TransferOwnershipResult(command=command, error="League is not active, remove roster and let new owner join instead")

            is_commissioner = league.commissioner_id == command.request_user_id

            if not is_commissioner:
                return TransferOwnershipResult(command=command, error="Forbidden")

            roster = self.league_roster_repo.get(command.league_id, command.roster_id, transaction)

            if not roster:
                return TransferOwnershipResult(command=command, error="Roster not found")

            # make sure user is not already in league
            rosters = self.league_roster_repo.get_all(command.league_id, transaction)
            for r in rosters:
                if r.id == new_owner.id:
                    return TransferOwnershipResult(command=command, error="User already in league")

            # assign new owner to roster
            roster.id = new_owner.id

            old_owner_leagues = self.user_league_repo.get_leagues(command.roster_id, transaction)
            league_preview = next((x for x in old_owner_leagues if x.id == command.league_id))

            if league_preview.matchup:
                if league_preview.matchup.away and league_preview.matchup.away.id == command.roster_id:
                    league_preview.matchup.away.id = new_owner.id
                elif league_preview.matchup.home and league_preview.matchup.home.id == command.roster_id:
                    league_preview.matchup.home.id = new_owner.id

            schedule = self.league_config_repo.get_schedule_config(command.league_id, transaction)

            matchups_to_update_by_week = {}
            for week in schedule.weeks:
                for schedule_matchup in week.matchups:
                    if (schedule_matchup.away and schedule_matchup.away.id == command.roster_id) or (schedule_matchup.home and schedule_matchup.home.id == command.roster_id):  # noqa
                        matchup = self.league_matchup_repo.get(command.league_id, week.week_number, schedule_matchup.id, transaction)

                        if schedule_matchup.away.id == command.roster_id:
                            schedule_matchup.away.id = new_owner.id
                            matchup.away.id = new_owner.id
                        else:
                            schedule_matchup.home.id = new_owner.id
                            matchup.home.id = new_owner.id

                        matchups_to_update_by_week[week.week_number] = matchup

            owned_players = []
            for spot in roster.positions.values():
                if spot.player:
                    owned_player = self.owned_player_repo.get(command.league_id, spot.player.id, transaction)
                    owned_player.owner_id = new_owner.id
                    owned_players.append(owned_player)

            # have to delete and re-add to correct the id
            self.league_roster_repo.delete(command.league_id, command.roster_id, transaction)
            self.league_roster_repo.set(command.league_id, roster, transaction)
            self.league_config_repo.set_schedule_config(command.league_id, schedule, transaction)
            for week_number, matchup in matchups_to_update_by_week.items():
                self.league_matchup_repo.set(command.league_id, week_number, matchup, transaction)

            for player in owned_players:
                self.owned_player_repo.set(command.league_id, player, transaction)

            # remove preview from old owner
            self.user_league_repo.delete(command.roster_id, command.league_id, transaction)

            # add new preview to new owner
            self.user_league_repo.set(new_owner.id, league_preview, transaction)

            league_transaction = LeagueTransaction.transfer_roster_ownership(command.league_id, command.roster_id, roster.name, new_owner.email)
            self.league_transaction_repo.create(command.league_id, league_transaction, transaction)

            return TransferOwnershipResult(command=command)

        transaction = self.league_roster_repo.firestore.create_transaction()
        return update(transaction)


def create_transfer_ownership_command_executor(
    league_roster_repo: LeagueRosterRepository = Depends(create_league_roster_repository),
    league_repo: LeagueRepository = Depends(create_league_repository),
    league_transaction_repo: LeagueTransactionRepository = Depends(create_league_transaction_repository),
    user_repo: UserRepository = Depends(create_user_repository),
    league_config_repo: LeagueConfigRepository = Depends(create_league_config_repository),
    league_matchup_repo: LeagueWeekMatchupRepository = Depends(create_league_week_matchup_repository),
    user_league_repo: UserLeagueRepository = Depends(create_user_league_repository),
    owned_player_repo: LeagueOwnedPlayerRepository = Depends(create_league_owned_player_repository),
    public_repo: PublicRepository = Depends(create_public_repository),
):
    return TransferOwnershipCommandExecutor(
        league_repo=league_repo,
        league_roster_repo=league_roster_repo,
        league_transaction_repo=league_transaction_repo,
        user_repo=user_repo,
        league_config_repo=league_config_repo,
        league_matchup_repo=league_matchup_repo,
        user_league_repo=user_league_repo,
        owned_player_repo=owned_player_repo,
        public_repo=public_repo,
    )
