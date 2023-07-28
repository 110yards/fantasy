from copy import deepcopy

from api.tests.mocks.mock_firestore_proxy import MockFirestoreProxy
from app.domain.entities.league_positions_config import LeaguePositionsConfig
from app.domain.entities.player import Player
from app.domain.entities.roster import Roster
from app.domain.entities.team import Team
from app.domain.entities.waiver_bid import WaiverBid, WaiverBidResult
from app.domain.enums.position_type import PositionType
from app.domain.repositories.league_config_repository import LeagueConfigRepository
from app.domain.repositories.league_owned_player_repository import LeagueOwnedPlayerRepository
from app.domain.repositories.league_roster_repository import LeagueRosterRepository
from app.domain.repositories.league_transaction_repository import LeagueTransactionRepository
from app.domain.services.roster_player_service import RosterPlayerService
from app.domain.services.waiver_service import WaiverService

MOCK_LEAGUE_ID = "0"

player1 = Player(id="1", cfl_central_id=1, first_name="Player", last_name="One", position=PositionType.rb, team=Team.bc(), status_current=1)
player2 = Player(id="2", cfl_central_id=2, first_name="Player", last_name="Two", position=PositionType.rb, team=Team.cgy(), status_current=1)
player3 = Player(id="3", cfl_central_id=3, first_name="Player", last_name="Three", position=PositionType.rb, team=Team.ssk(), status_current=1)
player4wr = Player(id="4", cfl_central_id=4, first_name="Player", last_name="Four", position=PositionType.wr, team=Team.mtl(), status_current=1)

league_positions = LeaguePositionsConfig().create_positions()


def get_roster_player_service() -> RosterPlayerService:
    league_owned_player_repo = LeagueOwnedPlayerRepository(MockFirestoreProxy())
    roster_repo = LeagueRosterRepository(MockFirestoreProxy())
    league_transaction_repo = LeagueTransactionRepository(MockFirestoreProxy())
    league_config_repo = LeagueConfigRepository(MockFirestoreProxy())

    league_config_repo.set_positions_config(MOCK_LEAGUE_ID, LeaguePositionsConfig())

    return RosterPlayerService(league_owned_player_repo, roster_repo, league_transaction_repo, league_config_repo)


def test_waiver_priority_is_reverse_rank():
    roster1 = Roster(id="1", name="team 1", rank=1)
    roster2 = Roster(id="2", name="team 2", rank=3)
    roster3 = Roster(id="3", name="team 3", rank=4)
    roster4 = Roster(id="4", name="team 4", rank=2)

    rosters = [roster1, roster2, roster3, roster4]

    target = WaiverService(get_roster_player_service())

    waiver_priority = target.get_initial_waiver_priority(rosters)

    assert waiver_priority[0] == "3"
    assert waiver_priority[1] == "2"
    assert waiver_priority[2] == "4"
    assert waiver_priority[3] == "1"


def test_highest_bid_wins_first_team():
    roster1 = Roster(id="1", name="team 1", rank=1, positions=deepcopy(league_positions))
    roster2 = Roster(id="2", name="team 2", rank=2, positions=deepcopy(league_positions))

    roster1.waiver_bids.append(WaiverBid(roster_id=roster1.id, player=player1, amount=5))
    roster2.waiver_bids.append(WaiverBid(roster_id=roster2.id, player=player1, amount=4))

    target = WaiverService(get_roster_player_service())

    target.process_bids([roster1, roster2])

    assert roster1.waiver_bids[0].result == WaiverBidResult.SuccessPending
    assert roster2.waiver_bids[0].result == WaiverBidResult.FailedOutBid


def test_highest_bid_wins_second_team():
    roster1 = Roster(id="1", name="team 1", rank=1, positions=deepcopy(league_positions))
    roster2 = Roster(id="2", name="team 2", rank=2, positions=deepcopy(league_positions))

    roster1.waiver_bids.append(WaiverBid(roster_id=roster1.id, player=player1, amount=4))
    roster2.waiver_bids.append(WaiverBid(roster_id=roster2.id, player=player1, amount=5))

    target = WaiverService(get_roster_player_service())

    target.process_bids([roster1, roster2])

    assert roster1.waiver_bids[0].result == WaiverBidResult.FailedOutBid
    assert roster2.waiver_bids[0].result == WaiverBidResult.SuccessPending


def test_tie_bids_different_players_both_succeed():
    roster1 = Roster(id="1", name="team 1", rank=1, positions=deepcopy(league_positions))
    roster2 = Roster(id="2", name="team 2", rank=2, positions=deepcopy(league_positions))

    roster1.waiver_bids.append(WaiverBid(roster_id=roster1.id, player=player1, amount=5))
    roster2.waiver_bids.append(WaiverBid(roster_id=roster2.id, player=player2, amount=5))

    target = WaiverService(get_roster_player_service())

    target.process_bids([roster1, roster2])

    assert roster1.waiver_bids[0].result == WaiverBidResult.SuccessPending
    assert roster2.waiver_bids[0].result == WaiverBidResult.SuccessPending


def test_tie_goes_to_highest_priority():
    roster1 = Roster(id="1", name="team 1", rank=1, positions=deepcopy(league_positions))
    roster2 = Roster(id="2", name="team 2", rank=2, positions=deepcopy(league_positions))
    roster3 = Roster(id="3", name="team 3", rank=3, positions=deepcopy(league_positions))

    roster1.waiver_bids.append(WaiverBid(roster_id=roster1.id, player=player1, amount=5))
    roster2.waiver_bids.append(WaiverBid(roster_id=roster2.id, player=player1, amount=5))
    roster3.waiver_bids.append(WaiverBid(roster_id=roster3.id, player=player1, amount=5))

    target = WaiverService(get_roster_player_service())
    target.process_bids([roster1, roster2, roster3])

    assert roster1.waiver_bids[0].result == WaiverBidResult.FailedLowerPriority
    assert roster2.waiver_bids[0].result == WaiverBidResult.FailedLowerPriority
    assert roster3.waiver_bids[0].result == WaiverBidResult.SuccessPending


def test_tie_goes_to_highest_priority_two_ties():
    roster1 = Roster(id="1", name="team 1", rank=1, positions=deepcopy(league_positions))
    roster2 = Roster(id="2", name="team 2", rank=2, positions=deepcopy(league_positions))

    roster1.waiver_bids.append(WaiverBid(roster_id=roster1.id, player=player1, amount=5))
    roster2.waiver_bids.append(WaiverBid(roster_id=roster2.id, player=player1, amount=5))

    roster1.waiver_bids.append(WaiverBid(roster_id=roster1.id, player=player2, amount=5))
    roster2.waiver_bids.append(WaiverBid(roster_id=roster2.id, player=player2, amount=5))

    target = WaiverService(get_roster_player_service())
    target.process_bids([roster1, roster2])

    assert roster1.waiver_bids[0].result == WaiverBidResult.FailedLowerPriority, "Assert 1 failed"
    assert roster2.waiver_bids[0].result == WaiverBidResult.SuccessPending, "Assert 2 failed"

    assert roster1.waiver_bids[1].result == WaiverBidResult.SuccessPending, "Assert 3 failed"
    assert roster2.waiver_bids[1].result == WaiverBidResult.FailedLowerPriority, "Assert 4 failed"


def test_teams_with_no_bids_work_ok():
    roster1 = Roster(id="1", name="team 1", rank=1, positions=deepcopy(league_positions))
    roster2 = Roster(id="2", name="team 2", rank=2, positions=deepcopy(league_positions))

    roster1.waiver_bids.append(WaiverBid(roster_id=roster1.id, player=player1, amount=5))

    target = WaiverService(get_roster_player_service())

    target.process_bids([roster1, roster2])

    assert roster1.waiver_bids[0].result == WaiverBidResult.SuccessPending


def test_cannot_exceed_waiver_budget_one_bid():
    roster1 = Roster(id="1", name="team 1", rank=1, waiver_budget=20, positions=deepcopy(league_positions))

    roster1.waiver_bids.append(WaiverBid(roster_id=roster1.id, player=player1, amount=25))

    target = WaiverService(get_roster_player_service())

    target.process_bids([roster1])

    assert roster1.waiver_bids[0].result == WaiverBidResult.FailedNotEnoughMoney


def test_cannot_exceed_waiver_budget_combined_bids():
    roster1 = Roster(id="1", name="team 1", rank=1, waiver_budget=20, positions=deepcopy(league_positions))

    roster1.waiver_bids.append(WaiverBid(roster_id=roster1.id, player=player1, amount=15))
    roster1.waiver_bids.append(WaiverBid(roster_id=roster1.id, player=player2, amount=10))

    target = WaiverService(get_roster_player_service())

    target.process_bids([roster1])

    assert roster1.waiver_bids[0].result == WaiverBidResult.SuccessPending
    assert roster1.waiver_bids[1].result == WaiverBidResult.FailedNotEnoughMoney


def test_drop_player_must_still_be_on_roster():
    roster1 = Roster(id="1", name="team 1", rank=1, positions=deepcopy(league_positions))

    # note that player 2 is not actually in a position on roster1
    roster1.waiver_bids.append(WaiverBid(roster_id=roster1.id, player=player1, drop_player=player2, amount=25))

    target = WaiverService(get_roster_player_service())

    target.process_bids([roster1])

    assert roster1.waiver_bids[0].result == WaiverBidResult.FailedDropPlayerNotOnRoster


def test_drop_player_must_still_be_on_roster_already_dropped():
    roster1 = Roster(id="1", name="team 1", rank=1, positions=deepcopy(league_positions))

    roster1.positions["1"].player = player2

    roster1.waiver_bids.append(WaiverBid(roster_id=roster1.id, player=player1, drop_player=player2, amount=25))
    roster1.waiver_bids.append(WaiverBid(roster_id=roster1.id, player=player3, drop_player=player2, amount=15))

    target = WaiverService(get_roster_player_service())

    target.process_bids([roster1])

    assert roster1.waiver_bids[1].result == WaiverBidResult.FailedDropPlayerNotOnRoster


def test_roster_budget_is_updated():
    roster1 = Roster(id="1", name="team 1", rank=1, positions=deepcopy(league_positions))

    roster1.waiver_bids.append(WaiverBid(roster_id=roster1.id, player=player1, amount=5))

    target = WaiverService(get_roster_player_service())

    target.process_bids([roster1])

    assert roster1.waiver_budget == 95


def test_roster_budget_not_updated_failed_bids():
    roster1 = Roster(id="1", name="team 1", rank=1, positions=deepcopy(league_positions))
    roster2 = Roster(id="2", name="team 2", rank=2, positions=deepcopy(league_positions))

    roster1.waiver_bids.append(WaiverBid(roster_id=roster1.id, player=player1, amount=5))
    roster2.waiver_bids.append(WaiverBid(roster_id=roster2.id, player=player1, amount=4))

    target = WaiverService(get_roster_player_service())

    target.process_bids([roster1, roster2])

    assert roster2.waiver_budget == 100


def test_roster_budget_not_updated_failed_bid_due_to_player_not_on_roster():
    roster1 = Roster(id="1", name="team 1", rank=1, positions=deepcopy(league_positions))

    # bug 187 - waiver budget is reduced when attempting to add a player and there is no space on roster (wrong add/drop combo)
    # roster already has a RB
    roster1.positions["2"].player = player3
    # drop player is a WR
    roster1.positions["3"].player = player4wr
    # add player is a RB
    roster1.waiver_bids.append(WaiverBid(roster_id=roster1.id, player=player1, drop_player=player4wr, amount=5))

    target = WaiverService(get_roster_player_service())

    bids = target.process_bids([roster1])
    target.apply_winning_bid(MOCK_LEAGUE_ID, bids[0], roster1, None)

    assert roster1.waiver_budget == 100
