from app.core.publisher import VirtualPubSubPublisher
from app.domain.commands.league.update_league_scoring import UpdateLeagueScoringCommand, UpdateLeagueScoringCommandExecutor
from app.domain.entities.league import League
from app.domain.entities.scoring_settings import ScoringSettings
from app.domain.enums.draft_state import DraftState
from app.domain.repositories.league_config_repository import LeagueConfigRepository
from app.domain.repositories.league_repository import LeagueRepository
from app.domain.repositories.league_transaction_repository import LeagueTransactionRepository
from app.domain.repositories.state_repository import StateRepository
from tests.asserts import are_equal
from tests.mocks.mock_firestore_proxy import MockFirestoreProxy

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

    command_executor = UpdateLeagueScoringCommandExecutor(league_repo, league_config_repo, state_repo, transaction_repo, get_publisher())
    command = UpdateLeagueScoringCommand.construct(league_id="league1")

    result = command_executor.execute(command)

    expected = False
    actual = result.success

    are_equal(expected, actual)
