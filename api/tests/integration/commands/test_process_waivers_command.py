
from yards_py.domain.entities.schedule import PlayoffType, Schedule
from yards_py.domain.entities.state import State
from api.app.domain.repositories.league_config_repository import LeagueConfigRepository
from api.app.domain.repositories.state_repository import StateRepository
from api.app.domain.repositories.league_week_repository import LeagueWeekRepository
from yards_py.domain.entities.league_transaction import TransactionType
from api.app.domain.repositories.league_transaction_repository import LeagueTransactionRepository
from api.app.domain.repositories.league_owned_player_repository import LeagueOwnedPlayerRepository
from api.app.domain.services.roster_player_service import RosterPlayerService
from api.app.domain.services.waiver_service import WaiverService
from api.app.domain.repositories.league_repository import LeagueRepository
from yards_py.domain.entities.league import League
from api.tests.mocks.mock_firestore_proxy import MockFirestoreProxy
from api.app.domain.repositories.league_roster_repository import LeagueRosterRepository
from typing import List
from api.app.domain.commands.league.process_waivers import ProcessWaiversCommand, ProcessWaiversCommandExecutor
from yards_py.domain.entities.waiver_bid import WaiverBid, WaiverBidResult
from yards_py.domain.entities.league_positions_config import LeaguePositionsConfig
from yards_py.domain.entities.team import Team
from api.app.domain.enums.position_type import PositionType
from yards_py.domain.entities.player import Player
from yards_py.domain.entities.roster import Roster
from copy import deepcopy

from api.tests.mocks.mock_notification_service import MockNotificationService

rb1 = Player(id="1", cfl_central_id=1, first_name="Player", last_name="One", position=PositionType.rb, team=Team.bc(), status_current=1)
rb2 = Player(id="2", cfl_central_id=2, first_name="Player", last_name="Two", position=PositionType.rb, team=Team.cgy(), status_current=1)
rb3 = Player(id="3", cfl_central_id=3, first_name="Player", last_name="Three", position=PositionType.rb, team=Team.ssk(), status_current=1)
wr1 = Player(id="4", cfl_central_id=4, first_name="Player", last_name="Four", position=PositionType.wr, team=Team.ssk(), status_current=1)

league_positions = LeaguePositionsConfig().create_positions()
league = League.construct(id="test_league", name="Test League", waivers_active=True)
state = State.default(with_current_week=2)


def get_target(rosters: List[Roster]) -> ProcessWaiversCommandExecutor:

    state_repo = StateRepository(MockFirestoreProxy([state]))
    league_repo = LeagueRepository(MockFirestoreProxy([deepcopy(league)]))
    league_roster_repo = LeagueRosterRepository(MockFirestoreProxy(rosters))
    league_owned_player_repo = LeagueOwnedPlayerRepository(MockFirestoreProxy())
    transaction_repo = LeagueTransactionRepository(MockFirestoreProxy())
    league_week_repo = LeagueWeekRepository(MockFirestoreProxy())
    league_config_repo = LeagueConfigRepository(MockFirestoreProxy())

    league_config_repo.set_positions_config(league.id, LeaguePositionsConfig())
    league_config_repo.set_schedule_config(league.id, Schedule(first_playoff_week=15, playoff_type=PlayoffType.TOP_2, weeks=[], enable_loser_playoff=False))

    notification_service = MockNotificationService()

    roster_player_service = RosterPlayerService(league_owned_player_repo, league_roster_repo, transaction_repo, league_config_repo)
    waiver_service = WaiverService(roster_player_service)

    return ProcessWaiversCommandExecutor(
        state_repo=state_repo,
        league_roster_repo=league_roster_repo,
        league_repo=league_repo,
        waiver_service=waiver_service,
        league_week_repo=league_week_repo,
        league_config_repo=league_config_repo,
        notification_service=notification_service,
    )


def test_process_two_successful_bids():
    # create two bids without drop players, no conflicts, ensure they both work
    roster1 = Roster(id="1", name="team 1", rank=1, positions=deepcopy(league_positions))

    roster1.waiver_bids.append(WaiverBid(roster_id=roster1.id, player=rb1, amount=25))
    roster1.waiver_bids.append(WaiverBid(roster_id=roster1.id, player=wr1, amount=15))

    command = ProcessWaiversCommand(league_id=league.id)
    executor = get_target([roster1])

    executor.execute(command)

    assert roster1.processed_waiver_bids[0].result == WaiverBidResult.Success, "assert 1 failed"
    assert roster1.processed_waiver_bids[1].result == WaiverBidResult.Success, "assert 2 failed"


def test_no_drop_player_no_space_on_roster():
    # create two bids without drop players, same position, only one position available
    # first should pass, second should fail as there is no space on roster after processing the first one
    roster1 = Roster(id="1", name="team 1", rank=1, positions=deepcopy(league_positions))

    roster1.waiver_bids.append(WaiverBid(roster_id=roster1.id, player=rb1, amount=25))
    roster1.waiver_bids.append(WaiverBid(roster_id=roster1.id, player=rb3, amount=15))

    command = ProcessWaiversCommand(league_id=league.id)
    executor = get_target([roster1])

    executor.execute(command)

    assert roster1.processed_waiver_bids[0].result == WaiverBidResult.Success, "assert 1 failed"
    assert roster1.processed_waiver_bids[1].result == WaiverBidResult.FailedNoRosterSpace, "assert 2 failed"


def test_add_transaction_is_created():
    # create two bids without drop players, no conflicts, ensure they both work
    roster1 = Roster(id="1", name="team 1", rank=1, positions=deepcopy(league_positions))

    roster1.waiver_bids.append(WaiverBid(roster_id=roster1.id, player=rb1, amount=25))

    command = ProcessWaiversCommand(league_id=league.id)
    executor = get_target([roster1])

    executor.execute(command)

    transaction_repo = executor.waiver_service.roster_player_service.league_transaction_repo
    transactions = transaction_repo.firestore.get_all(None)
    transaction = next((x for x in transactions if x.type == TransactionType.CLAIM_PLAYER and x.player_id == rb1.id), None)

    assert transaction, "No add transaction found"


def test_drop_transaction_is_created():
    roster1 = Roster(id="1", name="team 1", rank=1, positions=deepcopy(league_positions))

    roster1.positions["2"].player = rb2

    roster1.waiver_bids.append(WaiverBid(roster_id=roster1.id, player=rb1, drop_player=rb2, amount=25))

    command = ProcessWaiversCommand(league_id=league.id)
    executor = get_target([roster1])

    executor.execute(command)

    transaction_repo = executor.waiver_service.roster_player_service.league_transaction_repo
    transactions = transaction_repo.firestore.get_all(None)
    transaction = next((x for x in transactions if x.type == TransactionType.DROP_PLAYER and x.player_id == rb2.id), None)

    assert transaction, "No drop transaction found"


def test_waivers_are_unlocked():
    command = ProcessWaiversCommand(league_id=league.id)
    executor = get_target([])

    executor.execute(command)

    updated_league = executor.league_repo.get(league.id)

    assert not updated_league.waivers_active, "Waivers were not deactivated"


def test_bids_are_saved():
    roster1 = Roster(id="1", name="team 1", rank=1, positions=deepcopy(league_positions))

    roster1.waiver_bids.append(WaiverBid(roster_id=roster1.id, player=rb1, amount=25))

    command = ProcessWaiversCommand(league_id=league.id)
    executor = get_target([roster1])

    executor.execute(command)

    updated_week = executor.league_week_repo.get(league.id, str(state.current_week - 1))

    assert updated_week and updated_week is not None, "Bids were not saved on week"


def test_roster_budget_updated():
    # create two bids without drop players, no conflicts, ensure they both work
    roster1 = Roster(id="1", name="team 1", waiver_budget=100, rank=1, positions=deepcopy(league_positions))

    roster1.waiver_bids.append(WaiverBid(roster_id=roster1.id, player=rb1, amount=25))

    command = ProcessWaiversCommand(league_id=league.id)
    executor = get_target([roster1])

    executor.execute(command)

    roster = executor.league_roster_repo.get(league.id, roster1.id)

    assert roster.waiver_budget == 75, "Waiver budget was not updated"
