
from api.app.domain.enums.draft_state import DraftState
from api.app.domain.repositories.league_config_repository import LeagueConfigRepository, create_league_config_repository
from api.app.domain.repositories.league_roster_repository import LeagueRosterRepository, create_league_roster_repository
from api.app.domain.repositories.user_league_repository import UserLeagueRepository, create_user_league_repository
from typing import Optional

from api.app.core.annotate_args import annotate_args
from api.app.core.base_command_executor import (BaseCommand, BaseCommandExecutor,
                                                BaseCommandResult)
from api.app.domain.entities.league import League
from api.app.domain.enums.draft_type import DraftType
from api.app.domain.repositories.league_repository import (
    LeagueRepository, create_league_repository)
from fastapi import Depends
from firebase_admin import firestore


def create_update_league_command_executor(
    league_repo: LeagueRepository = Depends(create_league_repository),
    league_config_repo: LeagueConfigRepository = Depends(create_league_config_repository),
    league_roster_repo: LeagueRosterRepository = Depends(create_league_roster_repository),
    user_league_repo: UserLeagueRepository = Depends(create_user_league_repository),
):
    return UpdateLeagueCommandExecutor(
        league_repo,
        league_config_repo,
        league_roster_repo,
        user_league_repo)


@annotate_args
class UpdateLeagueCommand(BaseCommand):
    league_id: Optional[str]
    name: str
    private: bool
    password: Optional[str]
    draft_type: DraftType
    enable_discord_notifications: bool
    discord_webhook_url: Optional[str]
    notifications_draft: bool = False
    notifications_end_of_week: bool = False
    notifications_transactions: bool = False
    notifications_waivers: bool = False


@annotate_args
class UpdateLeagueResult(BaseCommandResult[UpdateLeagueCommand]):
    league: Optional[League]


class UpdateLeagueCommandExecutor(BaseCommandExecutor[UpdateLeagueCommand, UpdateLeagueResult]):

    def __init__(self,
                 league_repo: LeagueRepository,
                 league_config_repo: LeagueConfigRepository,
                 league_roster_repo: LeagueRosterRepository,
                 user_league_repo: UserLeagueRepository):
        self.league_repo = league_repo
        self.league_config_repo = league_config_repo
        self.league_roster_repo = league_roster_repo
        self.user_league_repo = user_league_repo

    def on_execute(self, command: UpdateLeagueCommand) -> UpdateLeagueResult:

        @firestore.transactional
        def update(transaction):
            league = self.league_repo.get(command.league_id, transaction)
            league.name = command.name
            league.enable_discord_notifications = command.enable_discord_notifications
            league.notifications_draft = command.notifications_draft
            league.notifications_end_of_week = command.notifications_end_of_week
            league.notifications_transactions = command.notifications_transactions
            league.notifications_waivers = command.notifications_waivers

            private_config = self.league_config_repo.get_private_config(command.league_id, transaction)
            private_config.discord_webhook_url = command.discord_webhook_url

            started = league.draft_state != DraftState.NOT_STARTED

            if not started:
                league.private = command.private
                league.draft_type = command.draft_type
                private_config.password = command.password

            rosters = self.league_roster_repo.get_all(command.league_id, transaction)
            user_leagues = {}
            for roster in rosters:
                user_league = self.user_league_repo.get(roster.id, command.league_id, transaction)
                user_league.update_league(league)
                user_leagues[roster.id] = user_league

            league = self.league_repo.update(league, transaction)

            self.league_config_repo.set_private_config(league.id, private_config, transaction)

            for roster_id in user_leagues:
                self.user_league_repo.set(roster_id, user_league, transaction)

            return UpdateLeagueResult(command=command, league=league)

        transaction = self.league_repo.firestore.create_transaction()
        return update(transaction)
