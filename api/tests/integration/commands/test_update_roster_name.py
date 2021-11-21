

from api.app.domain.repositories.league_transaction_repository import LeagueTransactionRepository
from api.app.domain.entities.user_league_preview import UserLeaguePreview
from api.app.domain.entities.schedule import Matchup, MatchupType, PlayoffType, Schedule, ScheduleWeek, WeekType
from api.app.domain.entities.roster import Roster
from api.app.domain.enums.draft_state import DraftState
from api.app.domain.entities.league import League
from api.app.domain.commands.roster.update_roster_name import UpdateRosterNameCommand, UpdateRosterNameCommandExecutor
from api.app.domain.repositories.league_roster_repository import LeagueRosterRepository
from api.app.domain.repositories.league_config_repository import LeagueConfigRepository
from api.app.domain.repositories.league_week_matchup_repository import LeagueWeekMatchupRepository
from api.app.domain.repositories.user_league_repository import UserLeagueRepository
from api.app.domain.repositories.league_repository import LeagueRepository
from api.tests.asserts import are_equal
from api.tests.mocks.mock_firestore_proxy import MockFirestoreProxy
from api.app.core.publisher import VirtualPubSubPublisher


def get_league_repo(league) -> LeagueRepository:
    leagues = [league]
    proxy = MockFirestoreProxy(leagues)
    return LeagueRepository(proxy)


def get_league_roster_repo(roster) -> LeagueRosterRepository:
    rosters = [roster]
    proxy = MockFirestoreProxy(rosters)
    return LeagueRosterRepository(proxy)


def get_league_config_repo() -> LeagueConfigRepository:
    proxy = MockFirestoreProxy()
    return LeagueConfigRepository(proxy)


def get_league_week_matchup_repo() -> LeagueWeekMatchupRepository:
    proxy = MockFirestoreProxy()
    return LeagueWeekMatchupRepository(proxy)


def get_user_league_repo(user_league) -> UserLeagueRepository:
    leagues = [user_league]
    proxy = MockFirestoreProxy(leagues)
    return UserLeagueRepository(proxy)


def get_league_transaction_repo() -> LeagueTransactionRepository:
    proxy = MockFirestoreProxy()
    return LeagueTransactionRepository(proxy)


def get_publisher() -> VirtualPubSubPublisher:
    return VirtualPubSubPublisher("test_project")


def create_mock_schedule(week_number) -> Schedule:
    return Schedule(
        weeks=[
            ScheduleWeek(week_number=week_number, week_type=WeekType.REGULAR)
        ],
        playoff_type=PlayoffType.TOP_2,
        enable_loser_playoff=False,
        first_playoff_week=2
    )


def test_update_roster_name():
    league = League.construct(id="league1", draft_state=DraftState.NOT_STARTED, name="Test League", commissioner_id="commish")
    roster = Roster(id="roster1", name="Mock Roster")
    user_league = UserLeaguePreview.create(roster, league)

    roster_repo = get_league_roster_repo(roster)
    league_repo = get_league_repo(league)
    user_league_repo = get_user_league_repo(user_league)

    command_executor = UpdateRosterNameCommandExecutor(
        league_config_repo=get_league_config_repo,
        league_repo=league_repo,
        league_roster_repo=roster_repo,
        league_week_matchup_repo=get_league_week_matchup_repo(),
        user_league_repo=user_league_repo,
        publisher=get_publisher(),
        league_transaction_repo=get_league_transaction_repo())

    new_name = "Update Roster Name"

    command = UpdateRosterNameCommand(league_id=league.id, roster_id=roster.id, roster_name=new_name, current_user_id=roster.id)

    result = command_executor.execute(command)

    assert result.success

    expected = new_name
    actual = roster_repo.get(league.id, roster.id).name

    are_equal(expected, actual)


def test_update_roster_name_updates_away_matchups():
    week_number = 1

    league = League.construct(id="league1", draft_state=DraftState.NOT_STARTED, name="Test League", schedule_generated=True, commissioner_id="commish")
    roster = Roster(id="roster1", name="Mock Roster")
    user_league = UserLeaguePreview.create(roster, league)
    schedule = create_mock_schedule(week_number)

    roster_repo = get_league_roster_repo(roster)
    league_repo = get_league_repo(league)
    user_league_repo = get_user_league_repo(user_league)
    matchup_repo = get_league_week_matchup_repo()
    config_repo = get_league_config_repo()

    matchup = Matchup(id="1", away=roster, type=MatchupType.REGULAR)
    matchup_repo.set(league.id, week_number, matchup)
    schedule.weeks[0].matchups.append(matchup)

    config_repo.set_schedule_config(league.id, schedule)

    command_executor = UpdateRosterNameCommandExecutor(
        league_config_repo=config_repo,
        league_repo=league_repo,
        league_roster_repo=roster_repo,
        league_week_matchup_repo=matchup_repo,
        user_league_repo=user_league_repo,
        publisher=get_publisher(),
        league_transaction_repo=get_league_transaction_repo())

    new_name = "Update Roster Name"

    command = UpdateRosterNameCommand(league_id=league.id, roster_id=roster.id, roster_name=new_name, current_user_id=roster.id)

    result = command_executor.execute(command)

    assert result.success

    expected = new_name
    actual = matchup_repo.get(league.id, week_number, matchup.id).away.name

    are_equal(expected, actual)


def test_update_roster_name_updates_schedule_config_away():
    week_number = 1

    league = League.construct(id="league1", draft_state=DraftState.NOT_STARTED, name="Test League", schedule_generated=True, commissioner_id="commish")
    roster = Roster(id="roster1", name="Mock Roster")
    user_league = UserLeaguePreview.create(roster, league)
    schedule = create_mock_schedule(week_number)

    roster_repo = get_league_roster_repo(roster)
    league_repo = get_league_repo(league)
    user_league_repo = get_user_league_repo(user_league)
    matchup_repo = get_league_week_matchup_repo()
    config_repo = get_league_config_repo()

    matchup = Matchup(id="1", away=roster, type=MatchupType.REGULAR)
    matchup_repo.set(league.id, week_number, matchup)
    schedule.weeks[0].matchups.append(matchup)

    config_repo.set_schedule_config(league.id, schedule)

    command_executor = UpdateRosterNameCommandExecutor(
        league_config_repo=config_repo,
        league_repo=league_repo,
        league_roster_repo=roster_repo,
        league_week_matchup_repo=matchup_repo,
        user_league_repo=user_league_repo,
        publisher=get_publisher(),
        league_transaction_repo=get_league_transaction_repo())

    new_name = "Update Roster Name"

    command = UpdateRosterNameCommand(league_id=league.id, roster_id=roster.id, roster_name=new_name, current_user_id=roster.id)

    result = command_executor.execute(command)

    assert result.success

    expected = new_name
    updated_schedule = config_repo.get_schedule_config(league.id)
    actual = updated_schedule.weeks[0].matchups[0].away.name

    are_equal(expected, actual)


def test_update_roster_name_updates_home_matchups():
    week_number = 1

    league = League.construct(id="league1", draft_state=DraftState.NOT_STARTED, name="Test League", schedule_generated=True, commissioner_id="commish")
    roster = Roster(id="roster1", name="Mock Roster")
    user_league = UserLeaguePreview.create(roster, league)
    schedule = create_mock_schedule(week_number)

    roster_repo = get_league_roster_repo(roster)
    league_repo = get_league_repo(league)
    user_league_repo = get_user_league_repo(user_league)
    matchup_repo = get_league_week_matchup_repo()
    config_repo = get_league_config_repo()

    matchup = Matchup(id="1", home=roster, type=MatchupType.REGULAR)
    matchup_repo.set(league.id, week_number, matchup)
    schedule.weeks[0].matchups.append(matchup)

    config_repo.set_schedule_config(league.id, schedule)

    command_executor = UpdateRosterNameCommandExecutor(
        league_config_repo=config_repo,
        league_repo=league_repo,
        league_roster_repo=roster_repo,
        league_week_matchup_repo=matchup_repo,
        user_league_repo=user_league_repo,
        publisher=get_publisher(),
        league_transaction_repo=get_league_transaction_repo())

    new_name = "Update Roster Name"

    command = UpdateRosterNameCommand(league_id=league.id, roster_id=roster.id, roster_name=new_name, current_user_id=roster.id)

    result = command_executor.execute(command)

    assert result.success

    expected = new_name
    actual = matchup_repo.get(league.id, week_number, matchup.id).home.name

    are_equal(expected, actual)


def test_update_roster_name_updates_schedule_config_home():
    week_number = 1

    league = League.construct(id="league1", draft_state=DraftState.NOT_STARTED, name="Test League", schedule_generated=True, commissioner_id="commish")
    roster = Roster(id="roster1", name="Mock Roster")
    user_league = UserLeaguePreview.create(roster, league)
    schedule = create_mock_schedule(week_number)

    roster_repo = get_league_roster_repo(roster)
    league_repo = get_league_repo(league)
    user_league_repo = get_user_league_repo(user_league)
    matchup_repo = get_league_week_matchup_repo()
    config_repo = get_league_config_repo()

    matchup = Matchup(id="1", home=roster, type=MatchupType.REGULAR)
    matchup_repo.set(league.id, week_number, matchup)
    schedule.weeks[0].matchups.append(matchup)

    config_repo.set_schedule_config(league.id, schedule)

    command_executor = UpdateRosterNameCommandExecutor(
        league_config_repo=config_repo,
        league_repo=league_repo,
        league_roster_repo=roster_repo,
        league_week_matchup_repo=matchup_repo,
        user_league_repo=user_league_repo,
        publisher=get_publisher(),
        league_transaction_repo=get_league_transaction_repo())

    new_name = "Update Roster Name"

    command = UpdateRosterNameCommand(league_id=league.id, roster_id=roster.id, roster_name=new_name, current_user_id=roster.id)

    result = command_executor.execute(command)

    assert result.success

    expected = new_name
    updated_schedule = config_repo.get_schedule_config(league.id)
    actual = updated_schedule.weeks[0].matchups[0].home.name

    are_equal(expected, actual)


def test_update_roster_name_updates_user_leagues_home():
    league = League.construct(id="league1", draft_state=DraftState.NOT_STARTED, name="Test League", commissioner_id="commish")
    roster = Roster(id="roster1", name="Mock Roster")
    user_league = UserLeaguePreview.create(roster, league)

    roster_repo = get_league_roster_repo(roster)
    league_repo = get_league_repo(league)
    user_league_repo = get_user_league_repo(user_league)

    command_executor = UpdateRosterNameCommandExecutor(
        league_config_repo=get_league_config_repo,
        league_repo=league_repo,
        league_roster_repo=roster_repo,
        league_week_matchup_repo=get_league_week_matchup_repo(),
        user_league_repo=user_league_repo,
        publisher=get_publisher(),
        league_transaction_repo=get_league_transaction_repo())

    new_name = "Update Roster Name"

    command = UpdateRosterNameCommand(league_id=league.id, roster_id=roster.id, roster_name=new_name, current_user_id=roster.id)

    result = command_executor.execute(command)

    assert result.success

    expected = new_name
    actual = user_league_repo.get(roster.id, league.id).matchup.home.name

    are_equal(expected, actual)


def test_update_another_user_should_fail():
    league = League.construct(id="league1", draft_state=DraftState.NOT_STARTED, name="Test League", commissioner_id="commish")
    roster = Roster(id="roster1", name="Mock Roster")
    user_league = UserLeaguePreview.create(roster, league)

    roster_repo = get_league_roster_repo(roster)
    league_repo = get_league_repo(league)
    user_league_repo = get_user_league_repo(user_league)

    command_executor = UpdateRosterNameCommandExecutor(
        league_config_repo=get_league_config_repo,
        league_repo=league_repo,
        league_roster_repo=roster_repo,
        league_week_matchup_repo=get_league_week_matchup_repo(),
        user_league_repo=user_league_repo,
        publisher=get_publisher(),
        league_transaction_repo=get_league_transaction_repo())

    new_name = "Update Roster Name"

    command = UpdateRosterNameCommand(league_id=league.id, roster_id=roster.id, roster_name=new_name, current_user_id="anotheruser")

    result = command_executor.execute(command)

    assert not result.success


def test_cannot_change_while_drafting():
    league = League.construct(id="league1", draft_state=DraftState.IN_PROGRESS, name="Test League", commissioner_id="commish")
    roster = Roster(id="roster1", name="Mock Roster")
    user_league = UserLeaguePreview.create(roster, league)

    roster_repo = get_league_roster_repo(roster)
    league_repo = get_league_repo(league)
    user_league_repo = get_user_league_repo(user_league)

    command_executor = UpdateRosterNameCommandExecutor(
        league_config_repo=get_league_config_repo,
        league_repo=league_repo,
        league_roster_repo=roster_repo,
        league_week_matchup_repo=get_league_week_matchup_repo(),
        user_league_repo=user_league_repo,
        publisher=get_publisher(),
        league_transaction_repo=get_league_transaction_repo())

    new_name = "Update Roster Name"

    command = UpdateRosterNameCommand(league_id=league.id, roster_id=roster.id, roster_name=new_name, current_user_id=roster.id)

    result = command_executor.execute(command)

    assert not result.success


def test_update_by_commisssioner():
    league = League.construct(id="league1", draft_state=DraftState.NOT_STARTED, name="Test League", commissioner_id="commish")
    roster = Roster(id="roster1", name="Mock Roster")
    user_league = UserLeaguePreview.create(roster, league)

    roster_repo = get_league_roster_repo(roster)
    league_repo = get_league_repo(league)
    user_league_repo = get_user_league_repo(user_league)

    command_executor = UpdateRosterNameCommandExecutor(
        league_config_repo=get_league_config_repo,
        league_repo=league_repo,
        league_roster_repo=roster_repo,
        league_week_matchup_repo=get_league_week_matchup_repo(),
        user_league_repo=user_league_repo,
        publisher=get_publisher(),
        league_transaction_repo=get_league_transaction_repo())

    new_name = "Update Roster Name"
    command = UpdateRosterNameCommand(league_id=league.id, roster_id=roster.id, roster_name=new_name, current_user_id=league.commissioner_id)

    result = command_executor.execute(command)

    assert result.success

    expected = new_name
    actual = roster_repo.get(league.id, roster.id).name

    are_equal(expected, actual)


def test_update_by_other_user():
    league = League.construct(id="league1", draft_state=DraftState.NOT_STARTED, name="Test League", commissioner_id="commish")
    roster = Roster(id="roster1", name="Mock Roster")
    user_league = UserLeaguePreview.create(roster, league)

    roster_repo = get_league_roster_repo(roster)
    league_repo = get_league_repo(league)
    user_league_repo = get_user_league_repo(user_league)

    command_executor = UpdateRosterNameCommandExecutor(
        league_config_repo=get_league_config_repo,
        league_repo=league_repo,
        league_roster_repo=roster_repo,
        league_week_matchup_repo=get_league_week_matchup_repo(),
        user_league_repo=user_league_repo,
        publisher=get_publisher(),
        league_transaction_repo=get_league_transaction_repo())

    new_name = "Update Roster Name"

    command = UpdateRosterNameCommand(league_id=league.id, roster_id=roster.id, roster_name=new_name, current_user_id="otheruser")

    result = command_executor.execute(command)

    assert not result.success

    expected = roster.name
    actual = roster_repo.get(league.id, roster.id).name

    are_equal(expected, actual)