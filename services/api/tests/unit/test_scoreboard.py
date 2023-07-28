from datetime import datetime, timedelta

import pytest
import pytz

from app.domain.entities.event_status import (
    EVENT_STATUS_CANCELLED,
    EVENT_STATUS_FINAL,
    EVENT_STATUS_IN_PROGRESS,
    EVENT_STATUS_POSTPONED,
    EVENT_STATUS_PRE_GAME,
    EventStatus,
)
from app.domain.entities.scoreboard import Scoreboard, ScoreboardGame
from tests.asserts import are_equal


def test_last_game_start():
    scoreboard = Scoreboard(
        games={
            "1": ScoreboardGame.construct(date_start=datetime(2021, 7, 1, 12, 00)),
            "2": ScoreboardGame.construct(date_start=datetime(2021, 7, 1, 16, 00)),
            "3": ScoreboardGame.construct(date_start=datetime(2021, 7, 2, 19, 00)),
            "4": ScoreboardGame.construct(date_start=datetime(2021, 7, 3, 18, 00)),
        }
    )

    expected = scoreboard.games["4"].date_start
    actual = scoreboard.last_game_start_time()

    are_equal(expected, actual)


def get_event_status(status_id: int):
    return EventStatus.construct(event_status_id=status_id)


is_game_complete_inputs = [
    (True, ScoreboardGame.construct(event_status=get_event_status(EVENT_STATUS_FINAL))),
    (True, ScoreboardGame.construct(event_status=get_event_status(EVENT_STATUS_CANCELLED))),
    (False, ScoreboardGame.construct(event_status=get_event_status(EVENT_STATUS_IN_PROGRESS))),
    (False, ScoreboardGame.construct(event_status=get_event_status(EVENT_STATUS_PRE_GAME))),
    (False, ScoreboardGame.construct(event_status=get_event_status(EVENT_STATUS_POSTPONED), date_start=datetime.now(tz=pytz.utc))),
    (False, ScoreboardGame.construct(event_status=get_event_status(EVENT_STATUS_POSTPONED), date_start=datetime.now(tz=pytz.utc) - timedelta(hours=3))),
    (True, ScoreboardGame.construct(event_status=get_event_status(EVENT_STATUS_POSTPONED), date_start=datetime.now(tz=pytz.utc) - timedelta(hours=24))),
]


@pytest.mark.parametrize("expected,game", is_game_complete_inputs)
def test_is_game_complete(expected: bool, game: ScoreboardGame):
    actual = game.is_complete()

    are_equal(expected, actual)
