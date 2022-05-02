
from api.app.core.publisher import Publisher, create_publisher
from api.app.domain.entities.league_transaction import LeagueTransaction
from api.app.domain.repositories.league_transaction_repository import LeagueTransactionRepository, create_league_transaction_repository
from api.app.domain.repositories.state_repository import StateRepository, create_state_repository
from typing import Optional

from api.app.core.annotate_args import annotate_args
from api.app.core.base_command_executor import (BaseCommand, BaseCommandExecutor,
                                                BaseCommandResult)
from api.app.domain.repositories.league_config_repository import (
    LeagueConfigRepository, create_league_config_repository)
from api.app.domain.repositories.league_repository import LeagueRepository, create_league_repository
from fastapi import Depends
from firebase_admin import firestore


def create_update_league_scoring_command_executor(
    league_repo: LeagueRepository = Depends(create_league_repository),
    league_config_repo: LeagueConfigRepository = Depends(create_league_config_repository),
    state_repo: StateRepository = Depends(create_state_repository),
    transaction_repo: LeagueTransactionRepository = Depends(create_league_transaction_repository),
    publisher: Publisher = Depends(create_publisher),
):
    return UpdateLeagueScoringCommandExecutor(league_repo, league_config_repo, state_repo, transaction_repo, publisher)


@annotate_args
class UpdateLeagueScoringCommand(BaseCommand):
    league_id: Optional[str]
    pass_attempts: float
    pass_completions: float
    pass_net_yards: float
    pass_touchdowns: float
    pass_interceptions: float
    # pass_fumbles: float
    rush_net_yards: float
    rush_attempts: float
    rush_touchdowns: float
    # rush_long_touchdowns: float
    receive_caught: float
    receive_yards: float
    receive_touchdowns: float
    receive_fumbles: float
    punt_singles: float
    kick_returns_yards: float
    kick_returns_touchdowns: float
    field_goal_made: float
    field_goal_misses: float
    field_goal_singles: float
    # field_goal_returns_yards: float
    # field_goal_returns_touchdowns: float
    # punt_returns_yards: float
    # punt_returns_touchdowns: float
    # kicks_singles: float
    one_point_converts_made: float
    two_point_converts_made: float
    tackles_defensive: float
    tackles_special_teams: float
    sacks_qb_made: float
    interceptions: float
    fumbles_forced: float
    fumbles_recovered: float
    passes_knocked_down: float


@annotate_args
class UpdateLeagueScoringResult(BaseCommandResult[UpdateLeagueScoringCommand]):
    pass


class UpdateLeagueScoringCommandExecutor(BaseCommandExecutor[UpdateLeagueScoringCommand, UpdateLeagueScoringResult]):

    def __init__(
        self,
        league_repo: LeagueRepository,
        league_config_repo: LeagueConfigRepository,
        state_repo: StateRepository,
        transaction_repo: LeagueTransactionRepository,
        publisher: Publisher,
    ):
        self.league_repo = league_repo
        self.league_config_repo = league_config_repo
        self.state_repo = state_repo
        self.transaction_repo = transaction_repo
        self.publisher = publisher

    def on_execute(self, command: UpdateLeagueScoringCommand) -> UpdateLeagueScoringResult:

        league = self.league_repo.get(command.league_id)

        if not league:
            return UpdateLeagueScoringResult(command=command, error="League not found")

        scoring = self.league_config_repo.get_scoring_config(command.league_id)

        scoring.pass_attempts = command.pass_attempts
        scoring.pass_completions = command.pass_completions
        scoring.pass_net_yards = command.pass_net_yards
        scoring.pass_touchdowns = command.pass_touchdowns
        scoring.pass_interceptions = command.pass_interceptions
        scoring.pass_fumbles = command.receive_fumbles  # synced with receive fumbles
        scoring.rush_net_yards = command.rush_net_yards
        scoring.rush_attempts = command.rush_attempts
        scoring.rush_touchdowns = command.rush_touchdowns
        # rush_long_touchdowns= # Rush long touchdowns are not scored
        scoring.receive_caught = command.receive_caught
        scoring.receive_yards = command.receive_yards
        scoring.receive_touchdowns = command.receive_touchdowns
        scoring.receive_fumbles = command.receive_fumbles
        scoring.punt_singles = command.punt_singles
        scoring.kick_returns_yards = command.kick_returns_yards
        scoring.kick_returns_touchdowns = command.kick_returns_touchdowns
        scoring.field_goal_made = command.field_goal_made
        scoring.field_goal_misses = command.field_goal_misses
        scoring.field_goal_singles = command.field_goal_singles
        scoring.field_goal_returns_yards = command.kick_returns_yards  # synced with kick returns
        scoring.field_goal_returns_touchdowns = command.kick_returns_touchdowns  # synced with kick returns
        scoring.punt_returns_yards = command.kick_returns_yards  # synced with kick returns
        scoring.punt_returns_touchdowns = command.kick_returns_touchdowns  # synced with kick returns
        scoring.kicks_singles = command.punt_singles  # synced with punt singles
        scoring.one_point_converts_made = command.one_point_converts_made
        scoring.two_point_converts_made = command.two_point_converts_made
        scoring.tackles_defensive = command.tackles_defensive
        scoring.tackles_special_teams = command.tackles_special_teams
        scoring.sacks_qb_made = command.sacks_qb_made
        scoring.interceptions = command.interceptions
        scoring.fumbles_forced = command.fumbles_forced
        scoring.fumbles_recovered = command.fumbles_recovered
        scoring.passes_knocked_down = command.passes_knocked_down

        @firestore.transactional
        def update(transaction):
            self.league_repo.update(league, transaction)
            self.league_config_repo.set_scoring_config(league.id, scoring, transaction)

            league_transaction = LeagueTransaction.change_scoring(command.league_id)
            self.transaction_repo.create(command.league_id, league_transaction, transaction)

        transaction = self.league_repo.firestore.create_transaction()
        update(transaction)

        return UpdateLeagueScoringResult(command=command)
