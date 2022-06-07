from typing import List
from yards_py.domain.entities.roster import Roster
import pytest
from time import sleep

case1 = [
    # purely by points
    ([Roster(name="one", wins=1), Roster(name="two", wins=0, losses=1)], "one"),
    ([Roster(name="two", wins=0, losses=1), Roster(name="one", wins=1)], "one"),

    # by points for
    ([Roster(name="one", points_for=100), Roster(name="two", points_for=50)], "one"),
    ([Roster(name="one", points_for=50), Roster(name="two", points_for=150)], "two"),


    # by point differential
    ([Roster(name="one", points_for=100, points_against=50), Roster(name="two", points_for=100, points_against=75)], "one"),
    ([Roster(name="one", points_for=100, points_against=50), Roster(name="two", points_for=100, points_against=25)], "two"),

]


@pytest.mark.parametrize("rosters, first", case1)
def test_sort_roster(rosters: List[Roster], first):

    for roster in rosters:
        roster.wl_points = Roster.calculate_wl_points(roster)

    rosters = Roster.sort(rosters)

    assert rosters[0].name == first


def test_random_winner():
    rosters = [Roster(name="one"), Roster(name="two")]

    winners = []

    for x in range(1000):
        rosters = Roster.sort(rosters)
        sleep(0.001)
        winners.append(rosters[0].name)

    assert "one" in winners
    assert "two" in winners
