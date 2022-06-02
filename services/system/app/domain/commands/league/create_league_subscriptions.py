from typing import List, Optional

from services.system.app.config.settings import Settings, get_settings
from yards_py.core.annotate_args import annotate_args
from yards_py.core.base_command_executor import (BaseCommand, BaseCommandExecutor,
                                                 BaseCommandResult)
from yards_py.core.logging import Logger
from yards_py.core.publisher import Publisher, create_publisher
from yards_py.domain.entities.league import League
from yards_py.domain.repositories.league_repository import (
    LeagueRepository, create_league_repository)
from yards_py.domain.topics import LEAGUE_COMMAND_TOPIC
from fastapi.param_functions import Depends
from firebase_admin import firestore


def create_league_subscriptions_command_executor(
    settings: Settings = Depends(get_settings),
    league_repo: LeagueRepository = Depends(create_league_repository),
    publisher: Publisher = Depends(create_publisher)
):
    return CreateLeagueSubscriptionsCommandExecutor(settings, league_repo, publisher)


@annotate_args
class CreateLeagueSubscriptionsCommand(BaseCommand):
    league: Optional[League]
    league_id: Optional[str]


@annotate_args
class CreateLeagueSubscriptionsResult(BaseCommandResult[CreateLeagueSubscriptionsCommand]):
    subscriptions: List[str]


class CreateLeagueSubscriptionsCommandExecutor(BaseCommandExecutor[CreateLeagueSubscriptionsCommand, CreateLeagueSubscriptionsResult]):

    def __init__(self,
                 settings: Settings,
                 league_repo: LeagueRepository,
                 publisher: Publisher):
        self.settings = settings
        self.league_repo = league_repo
        self.publisher = publisher

    def on_execute(self, command: CreateLeagueSubscriptionsCommand) -> CreateLeagueSubscriptionsResult:
        league_id = command.league.id if command.league else command.league_id

        if not league_id:
            Logger.warn("CreateLeagueSubscriptions - No league ID")
            return CreateLeagueSubscriptionsResult(command=command, error="Missing league id")

        api_key = self.settings.api_key
        league_command_sub_id = f"league_{league_id}-commands"
        league_command_endpoint = f"{self.settings.endpoint}/system/league_command?league_id={league_id}&key={api_key}"
        league_command_subscription = self.publisher.create_push_subscription(league_command_sub_id, LEAGUE_COMMAND_TOPIC, league_command_endpoint)
        league_command_subscription = league_command_subscription.name

        transaction = self.league_repo.firestore.create_transaction()

        @firestore.transactional
        def update_in_transaction(transaction):
            league = self.league_repo.get(league_id, transaction)
            league.league_command_subscription = True

            self.league_repo.update(league, transaction)

        update_in_transaction(transaction)

        return CreateLeagueSubscriptionsResult(
            command=command,
            subscriptions=[
                league_command_subscription,
            ],
        )
