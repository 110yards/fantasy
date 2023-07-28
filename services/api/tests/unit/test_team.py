import pytest

from app.domain.entities.team import Team
from tests.asserts import are_equal


@pytest.mark.parametrize("team_id,expected", [(1, "BC"), (2, "CGY"), (3, "EDM"), (4, "HAM"), (5, "MTL"), (6, "OTT"), (7, "SSK"), (8, "TOR"), (9, "WPG")])
def test_by_id(team_id, expected):
    actual = Team.by_id(team_id).abbreviation
    are_equal(expected, actual)


@pytest.mark.parametrize(
    "abbreviation,expected",
    [("BC", "BC"), ("CGY", "CGY"), ("EDM", "EDM"), ("HAM", "HAM"), ("MTL", "MTL"), ("OTT", "OTT"), ("SSK", "SSK"), ("TOR", "TOR"), ("WPG", "WPG")],
)
def test_by_abbreviation(abbreviation, expected):
    actual = Team.by_abbreviation(abbreviation).abbreviation
    are_equal(expected, actual)
