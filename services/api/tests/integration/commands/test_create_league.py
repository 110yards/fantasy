from datetime import datetime

from app.core.publisher import VirtualPubSubPublisher
from app.domain.commands.league.create_league import CreateLeagueCommand, CreateLeagueCommandExecutor
from app.domain.entities.state import State
from app.domain.entities.user import User
from app.domain.repositories.league_config_repository import LeagueConfigRepository
from app.domain.repositories.league_repository import LeagueRepository
from app.domain.repositories.league_roster_repository import LeagueRosterRepository
from app.domain.repositories.public_repository import PublicRepository
from app.domain.repositories.user_league_repository import UserLeagueRepository
from app.domain.repositories.user_repository import UserRepository
from tests.asserts import are_equal
from tests.mocks.mock_firestore_proxy import MockFirestoreProxy


def get_commissioner():
    return User(id="1", display_name="Test Guy", email="test@test.com", login_type="email")


def get_user_repo() -> UserRepository:
    users = [get_commissioner()]
    proxy = MockFirestoreProxy(users)
    return UserRepository(proxy)


def get_league_repo() -> LeagueRepository:
    proxy = MockFirestoreProxy()
    return LeagueRepository(proxy)


def get_user_league_repo() -> UserLeagueRepository:
    proxy = MockFirestoreProxy()
    return UserLeagueRepository(proxy)


def get_league_roster_repo() -> LeagueRosterRepository:
    proxy = MockFirestoreProxy()
    return LeagueRosterRepository(proxy)


def get_league_config_repo() -> LeagueConfigRepository:
    proxy = MockFirestoreProxy()
    return LeagueConfigRepository(proxy)


def get_public_repo() -> PublicRepository:
    public_repo = PublicRepository(MockFirestoreProxy())
    public_repo.set_state(State(current_week=1, current_season=datetime.now().year, season_weeks=21))
    return public_repo


def get_publisher() -> VirtualPubSubPublisher:
    return VirtualPubSubPublisher("test_project", repo=None)


def test_user_joins_league():
    commissioner = get_commissioner()

    user_repo = get_user_repo()
    league_repo = get_league_repo()
    user_league_repo = get_user_league_repo()
    league_roster_repo = get_league_roster_repo()
    league_config_repo = get_league_config_repo()
    publisher = get_publisher()

    command_executor = CreateLeagueCommandExecutor(
        user_repo,
        league_repo,
        user_league_repo,
        league_roster_repo,
        league_config_repo,
        publisher,
        get_public_repo(),
    )

    command = CreateLeagueCommand(commissioner_id=commissioner.id, name="Test League", private=False)
    result = command_executor.execute(command)

    roster = league_roster_repo.get(result.league.id, commissioner.id)

    expected = commissioner.id
    actual = roster.id

    are_equal(expected, actual)


def test_league_added_to_user():
    commissioner = get_commissioner()

    user_repo = get_user_repo()
    league_repo = get_league_repo()
    user_league_repo = get_user_league_repo()
    league_roster_repo = get_league_roster_repo()
    league_config_repo = get_league_config_repo()
    publisher = get_publisher()

    command_executor = CreateLeagueCommandExecutor(
        user_repo,
        league_repo,
        user_league_repo,
        league_roster_repo,
        league_config_repo,
        publisher,
        get_public_repo(),
    )

    command = CreateLeagueCommand(commissioner_id=commissioner.id, name="Test League", private=False)
    result = command_executor.execute(command)

    user_league = user_league_repo.get(commissioner.id, result.league.id)

    expected = result.league.id
    actual = user_league.id

    are_equal(expected, actual)


def test_league_preview_has_matchup():
    commissioner = get_commissioner()

    user_repo = get_user_repo()
    league_repo = get_league_repo()
    user_league_repo = get_user_league_repo()
    league_roster_repo = get_league_roster_repo()
    league_config_repo = get_league_config_repo()
    publisher = get_publisher()

    command_executor = CreateLeagueCommandExecutor(
        user_repo,
        league_repo,
        user_league_repo,
        league_roster_repo,
        league_config_repo,
        publisher,
        get_public_repo(),
    )

    command = CreateLeagueCommand(commissioner_id=commissioner.id, name="Test League", private=False)
    result = command_executor.execute(command)

    user_league = user_league_repo.get(commissioner.id, result.league.id)
    user_roster = league_roster_repo.get(result.league.id, commissioner.id)

    expected = user_roster.name
    actual = user_league.matchup.home.name

    assert expected is not None
    are_equal(expected, actual)


def test_creator_is_commissioner():
    commissioner = get_commissioner()

    user_repo = get_user_repo()
    league_repo = get_league_repo()
    user_league_repo = get_user_league_repo()
    league_roster_repo = get_league_roster_repo()
    league_config_repo = get_league_config_repo()
    publisher = get_publisher()

    command_executor = CreateLeagueCommandExecutor(
        user_repo,
        league_repo,
        user_league_repo,
        league_roster_repo,
        league_config_repo,
        publisher,
        get_public_repo(),
    )

    command = CreateLeagueCommand(commissioner_id=commissioner.id, name="Test League", private=False)
    result = command_executor.execute(command)

    new_league = league_repo.get(result.league.id)

    expected = commissioner.id
    actual = new_league.commissioner_id

    are_equal(expected, actual)


def test_private_config_initialized():
    commissioner = get_commissioner()

    user_repo = get_user_repo()
    league_repo = get_league_repo()
    user_league_repo = get_user_league_repo()
    league_roster_repo = get_league_roster_repo()
    league_config_repo = get_league_config_repo()
    publisher = get_publisher()

    command_executor = CreateLeagueCommandExecutor(
        user_repo,
        league_repo,
        user_league_repo,
        league_roster_repo,
        league_config_repo,
        publisher,
        get_public_repo(),
    )

    command = CreateLeagueCommand(commissioner_id=commissioner.id, name="Test League", private=False)
    result = command_executor.execute(command)

    config = league_config_repo.get_private_config(result.league.id)

    assert config is not None


def test_scoring_config_initialized():
    commissioner = get_commissioner()

    user_repo = get_user_repo()
    league_repo = get_league_repo()
    user_league_repo = get_user_league_repo()
    league_roster_repo = get_league_roster_repo()
    league_config_repo = get_league_config_repo()
    publisher = get_publisher()

    command_executor = CreateLeagueCommandExecutor(
        user_repo,
        league_repo,
        user_league_repo,
        league_roster_repo,
        league_config_repo,
        publisher,
        get_public_repo(),
    )

    command = CreateLeagueCommand(commissioner_id=commissioner.id, name="Test League", private=False)
    result = command_executor.execute(command)

    config = league_config_repo.get_scoring_config(result.league.id)

    assert config is not None


def test_positions_config_initialized():
    commissioner = get_commissioner()

    user_repo = get_user_repo()
    league_repo = get_league_repo()
    user_league_repo = get_user_league_repo()
    league_roster_repo = get_league_roster_repo()
    league_config_repo = get_league_config_repo()
    publisher = get_publisher()

    command_executor = CreateLeagueCommandExecutor(
        user_repo,
        league_repo,
        user_league_repo,
        league_roster_repo,
        league_config_repo,
        publisher,
        get_public_repo(),
    )

    command = CreateLeagueCommand(commissioner_id=commissioner.id, name="Test League", private=False)
    result = command_executor.execute(command)

    config = league_config_repo.get_positions_config(result.league.id)

    assert config is not None
