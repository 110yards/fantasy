from yards_py.domain.entities.draft import DraftOrder
from yards_py.domain.entities.league_positions_config import LeaguePositionsConfig
from yards_py.domain.entities.user_league_preview import UserLeaguePreview
from services.api.app.domain.commands.league.join_league import create_roster
from services.api.app.domain.repositories.league_config_repository import LeagueConfigRepository, create_league_config_repository
from services.api.app.domain.repositories.league_roster_repository import LeagueRosterRepository, create_league_roster_repository
from services.api.app.domain.repositories.public_repository import PublicRepository, create_public_repository
from services.api.app.domain.repositories.user_league_repository import UserLeagueRepository, create_user_league_repository
from datetime import datetime
from typing import Optional

from yards_py.core.annotate_args import annotate_args
from yards_py.core.base_command_executor import (BaseCommand, BaseCommandExecutor,
                                                 BaseCommandResult)
from yards_py.core.publisher import Publisher
from services.api.app.di import create_publisher
from yards_py.domain.entities.league import (DraftState, DraftType, League,
                                             PrivateConfig)
from yards_py.domain.entities.scoring_settings import ScoringSettings
from services.api.app.domain.repositories.league_repository import (
    LeagueRepository, create_league_repository)
from services.api.app.domain.topics import LEAGUE_CREATED_TOPIC
from fastapi.param_functions import Depends
from firebase_admin import firestore
from services.api.app.domain.repositories.user_repository import UserRepository, create_user_repository


def create_league_command_executor(
    user_repo: UserRepository = Depends(create_user_repository),
    league_repo: LeagueRepository = Depends(create_league_repository),
    user_league_repo: UserLeagueRepository = Depends(create_user_league_repository),
    league_roster_repo: LeagueRosterRepository = Depends(create_league_roster_repository),
    league_config_repo: LeagueConfigRepository = Depends(create_league_config_repository),
    publisher: Publisher = Depends(create_publisher),
    public_repo: PublicRepository = Depends(create_public_repository),
):
    return CreateLeagueCommandExecutor(
        user_repo,
        league_repo,
        user_league_repo,
        league_roster_repo,
        league_config_repo,
        publisher,
        public_repo=public_repo,
    )


@annotate_args
class CreateLeagueCommand(BaseCommand):
    commissioner_id: Optional[str]
    name: str
    private: bool
    password: Optional[str]


@annotate_args
class CreateLeagueResult(BaseCommandResult):
    league: League


class CreateLeagueCommandExecutor(BaseCommandExecutor[CreateLeagueCommand, CreateLeagueResult]):

    def __init__(
        self,
        user_repo: UserRepository,
        league_repo: LeagueRepository,
        user_league_repo: UserLeagueRepository,
        league_roster_repo: LeagueRosterRepository,
        league_config_repo: LeagueConfigRepository,
        publisher: Publisher,
        public_repo: PublicRepository,
    ):
        self.user_repo = user_repo
        self.league_repo = league_repo
        self.user_league_repo = user_league_repo
        self.league_roster_repo = league_roster_repo
        self.league_config_repo = league_config_repo
        self.publisher = publisher
        self.public_repo = public_repo

    def on_execute(self, command: CreateLeagueCommand) -> CreateLeagueResult:
        commissioner = self.user_repo.get(command.commissioner_id)

        positions_config = LeaguePositionsConfig()
        state = self.public_repo.get_state()

        draft_order = [
            DraftOrder(roster_id=commissioner.id)
        ]

        league = League(
            name=command.name,
            commissioner_id=command.commissioner_id,
            created=datetime.now(),
            draft_state=DraftState.NOT_STARTED,
            draft_type=DraftType.SNAKE,
            private=command.private,
            positions=positions_config.create_positions(),
            draft_order=draft_order,
            season=state.current_season,
        )

        roster = create_roster(commissioner.id, commissioner.display_name)

        private_config = PrivateConfig(password=command.password)
        scoring_config = ScoringSettings.create_default()

        command.password = None  # don't publish the league

        transaction = self.league_repo.firestore.create_transaction()

        @firestore.transactional
        def create_in_transaction(transaction):
            new_league = self.league_repo.create(league, transaction)
            self.league_config_repo.set_private_config(new_league.id, private_config, transaction)
            self.league_config_repo.set_scoring_config(new_league.id, scoring_config, transaction)
            self.league_config_repo.set_positions_config(new_league.id, positions_config, transaction)
            self.league_roster_repo.set(new_league.id, roster, transaction)

            commissioner.commissioner_of.append(new_league.id)

            user_league_preview = UserLeaguePreview.create(roster, new_league)

            self.user_league_repo.set(command.commissioner_id, user_league_preview, transaction)

            return new_league

        league = create_in_transaction(transaction)

        self.publisher.publish(league, LEAGUE_CREATED_TOPIC)

        return CreateLeagueResult(command=command, league=league)
