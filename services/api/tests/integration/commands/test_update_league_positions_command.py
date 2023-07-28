from datetime import datetime

import pytest

from app.domain.commands.league.update_league_positions import UpdateLeaguePositionsCommand, UpdateLeaguePositionsCommandExecutor
from app.domain.entities.draft import DraftOrder
from app.domain.entities.league import League
from app.domain.entities.league_positions_config import LeaguePositionsConfig
from app.domain.enums.draft_state import DraftState
from app.domain.enums.draft_type import DraftType
from app.domain.enums.position_type import PositionType
from app.domain.repositories.league_config_repository import LeagueConfigRepository
from app.domain.repositories.league_repository import LeagueRepository
from tests.asserts import are_equal
from tests.mocks.mock_firestore_proxy import MockFirestoreProxy


@pytest.mark.parametrize("position", PositionType.all())
def test_position_count_is_updated(position):
    mock_league = League(
        id="league1",
        name="test league",
        commissioner_id="user1",
        created=datetime.now(),
        draft_state=DraftState.NOT_STARTED,
        draft_type=DraftType.SNAKE,
        private=False,
        positions=LeaguePositionsConfig().create_positions(),
        draft_order=[DraftOrder(roster_id="user1")],
    )

    league_repo = LeagueRepository(MockFirestoreProxy())
    league_repo.create(mock_league)

    league_config_repo = LeagueConfigRepository(MockFirestoreProxy())
    league_config_repo.set_positions_config(mock_league.id, LeaguePositionsConfig())

    d = {e: 1 for e in PositionType.all()}
    d[position] = 0
    d["league_id"] = mock_league.id
    d["allow_bench_qb"] = False
    d["allow_bench_rb"] = False
    d["allow_bench_k"] = False

    command = UpdateLeaguePositionsCommand.parse_obj(d)
    command_executor = UpdateLeaguePositionsCommandExecutor(league_repo, league_config_repo)

    command_executor.execute(command)

    updated_config = league_config_repo.get_positions_config(mock_league.id)

    expected = 0
    actual = updated_config.dict()[position]

    are_equal(expected, actual)
