

from services.system.app.domain.commands.league.create_league_subscriptions import (
    CreateLeagueSubscriptionsCommand, CreateLeagueSubscriptionsCommandExecutor,
    create_league_subscriptions_command_executor)
from yards_py.domain.repositories.league_repository import (
    LeagueRepository, create_league_repository)
from fastapi.param_functions import Depends
from firebase_admin.firestore import firestore

from yards_py.domain.repositories.state_repository import StateRepository, create_state_repository


def create_league_cmd_sub_migration(
    league_repo=Depends(create_league_repository),
    command_executor=Depends(create_league_subscriptions_command_executor),
    state_repo=Depends(create_state_repository),
):
    return LeagueCommandSubMigration(league_repo, command_executor, state_repo)


class LeagueCommandSubMigration:
    '''Adds the League Command subscription to all leagues'''

    def __init__(
            self,
            league_repo: LeagueRepository,
            command_executor: CreateLeagueSubscriptionsCommandExecutor,
            state_repo: StateRepository,
    ):
        self.league_repo = league_repo
        self.command_executor = command_executor
        self.state_repo = state_repo

    def run(self, league_id: str = None) -> str:

        if league_id:
            leagues = [self.league_repo.get(league_id)]
        else:
            leagues = self.league_repo.get_all()

        fixed_count = 0

        state = self.state_repo.get()

        for league in leagues:

            if not league.is_active_for_season(state.current_season):
                continue

            @firestore.transactional
            def mark_incomplete(transaction):
                league.league_command_subscription = False
                self.league_repo.update(league, transaction)

            transaction = self.league_repo.firestore.create_transaction()
            # mark them as not having the sub first, so they can be identified as problem leagues
            mark_incomplete(transaction)

            command = CreateLeagueSubscriptionsCommand(league_id=league.id)
            self.command_executor.execute(command)
            fixed_count += 1

        return f"Created league command subscription for {fixed_count} leagues"
