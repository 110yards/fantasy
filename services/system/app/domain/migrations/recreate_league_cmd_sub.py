

from app.domain.commands.league.create_league_subscriptions import (
    CreateLeagueSubscriptionsCommand, CreateLeagueSubscriptionsCommandExecutor,
    create_league_subscriptions_command_executor)
from app.yards_py.domain.repositories.league_config_repository import LeagueConfigRepository, create_league_config_repository
from app.yards_py.domain.repositories.league_repository import (
    LeagueRepository, create_league_repository)
from fastapi.param_functions import Depends
from firebase_admin.firestore import firestore

from app.yards_py.domain.repositories.state_repository import StateRepository, create_state_repository


class LeagueCommandSubMigration:
    '''Adds the League Command subscription to all leagues'''

    def __init__(
            self,
            league_repo: LeagueRepository,
            league_config_repo: LeagueConfigRepository,
            command_executor: CreateLeagueSubscriptionsCommandExecutor,
            state_repo: StateRepository,
    ):
        self.league_repo = league_repo
        self.league_config_repo = league_config_repo
        self.command_executor = command_executor
        self.state_repo = state_repo

    def run(self, league_id: str = None) -> str:

        state = self.state_repo.get()
        if league_id:
            leagues = [self.league_repo.get(league_id)]
        else:
            leagues = self.league_repo.get_all(season=state.current_season)

        fixed_count = 0


        for league in leagues:

            if not league.is_active_for_season(state.current_season):
                continue

            @firestore.transactional
            def mark_incomplete(transaction):
                league_state = self.league_config_repo.get_state(league.id, transaction)
                league_state.league_command_subscription = False
                self.league_config_repo.set_state(league.id, league_state, transaction)

            transaction = self.league_config_repo.firestore.create_transaction()
            # mark them as not having the sub first, so they can be identified as problem leagues
            mark_incomplete(transaction)

            command = CreateLeagueSubscriptionsCommand(league_id=league.id)
            self.command_executor.execute(command)
            fixed_count += 1

        return f"Created league command subscription for {fixed_count} leagues"


def create_league_cmd_sub_migration(
    league_repo=Depends(create_league_repository),
    league_config_repo=Depends(create_league_config_repository),
    command_executor=Depends(create_league_subscriptions_command_executor),
    state_repo=Depends(create_state_repository),
):
    return LeagueCommandSubMigration(
        league_repo=league_repo,
        league_config_repo=league_config_repo,
        command_executor=command_executor,
        state_repo=state_repo,
    )
