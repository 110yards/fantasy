import pytest

from app.domain.models.name_slug import name_slug


@pytest.mark.parametrize(
    "team_abbr, full_name, expected",
    [
        ("BC", "T.J. Lee III", "bc-tjlee"),
        ("BC", "T.J. Lee", "bc-tjlee"),
        ("ham", "Kenneth Jr George", "ham-kennethgeorge"),
        ("ham", "Carthell Flowers-Lloyd", "ham-carthellflowerslloyd"),
    ],
)
def test_name_slug(team_abbr: str, full_name: str, expected: str) -> None:
    assert name_slug(team_abbr, full_name) == expected
