import pytest

from app.domain.entities.scoreboard import Scoreboard, Team, Teams
from tests.asserts import are_equal

lock_cases = [
    ({}, False),  # No teams locked
    ("bc", True),
    ("cgy", True),
    ("edm", True),
    ("ssk", True),
    ("wpg", True),
    ("ham", True),
    ("tor", True),
    ("ott", True),
    ("mtl", True),
]


@pytest.mark.parametrize("locked_team, expected", lock_cases)
def test_any_locks_works_with_all_teams(locked_team: str, expected: bool):
    scoreboard = Scoreboard(games=[], teams=Teams())

    if locked_team:
        team: Team = getattr(scoreboard.teams, locked_team)
        team.locked = True

    actual = scoreboard.any_locks()
    are_equal(expected, actual)
