from yards_py.core.publisher import VirtualPubSubPublisher
from services.api.app.domain.enums.draft_state import DraftState
from services.api.app.domain.repositories.league_transaction_repository import LeagueTransactionRepository
from yards_py.domain.entities.league import League
from yards_py.domain.entities.scoring_settings import ScoringSettings
from api.tests.asserts import are_equal
from yards_py.domain.entities.state import Locks, State
from services.api.app.domain.repositories.state_repository import StateRepository
from services.api.app.domain.repositories.league_config_repository import LeagueConfigRepository
from api.tests.mocks.mock_firestore_proxy import MockFirestoreProxy
from services.api.app.domain.repositories.league_repository import LeagueRepository
from services.api.app.domain.commands.league.update_league_scoring import UpdateLeagueScoringCommand, UpdateLeagueScoringCommandExecutor


# def test_cannot_update_when_week_started():
#     # keeping this in case I decide to go back to this rule
#     league = League.construct(id="league1")
#     league_repo = LeagueRepository(MockFirestoreProxy())
#     league_repo.create(league)

#     scoring = ScoringSettings.create_default()
#     league_config_repo = LeagueConfigRepository(MockFirestoreProxy())
#     league_config_repo.set_scoring_config(league.id, scoring)

#     state_repo = StateRepository(MockFirestoreProxy())
#     transaction_repo = LeagueTransactionRepository(MockFirestoreProxy())

#     locks = Locks(BC=True)
#     state = State.construct(locks=locks)
#     state_repo.set(state)

#     command_executor = UpdateLeagueScoringCommandExecutor(league_repo, league_config_repo, state_repo, transaction_repo)
#     command = UpdateLeagueScoringCommand(league_id=league.id, **scoring.dict())

#     result = command_executor.execute(command)

#     expected = False
#     actual = result.success

#     are_equal(expected, actual)

def get_publisher() -> VirtualPubSubPublisher:
    return VirtualPubSubPublisher("test_project", repo=None)


def test_can_update_when_not_started():
    league = League.construct(id="league1", draft_state=DraftState.NOT_STARTED)
    league_repo = LeagueRepository(MockFirestoreProxy())
    league_repo.create(league)

    scoring = ScoringSettings.create_default()
    league_config_repo = LeagueConfigRepository(MockFirestoreProxy())
    league_config_repo.set_scoring_config(league.id, scoring)

    state_repo = StateRepository(MockFirestoreProxy())
    transaction_repo = LeagueTransactionRepository(MockFirestoreProxy())

    locks = Locks()
    state = State.construct(locks=locks, current_season=2021)
    state_repo.set(state)

    command_executor = UpdateLeagueScoringCommandExecutor(league_repo, league_config_repo, state_repo, transaction_repo, get_publisher())
    command = UpdateLeagueScoringCommand(league_id=league.id, **scoring.dict())

    result = command_executor.execute(command)

    expected = True
    actual = result.success

    are_equal(expected, actual)


def test_returns_error_when_no_league():
    league_repo = LeagueRepository(MockFirestoreProxy())
    league_config_repo = LeagueConfigRepository(MockFirestoreProxy())
    state_repo = StateRepository(MockFirestoreProxy())
    transaction_repo = LeagueTransactionRepository(MockFirestoreProxy())

    locks = Locks()
    state = State.construct(locks=locks)
    state_repo.set(state)

    command_executor = UpdateLeagueScoringCommandExecutor(league_repo, league_config_repo, state_repo, transaction_repo, get_publisher())
    command = UpdateLeagueScoringCommand.construct(league_id="league1")

    result = command_executor.execute(command)

    expected = False
    actual = result.success

    are_equal(expected, actual)
