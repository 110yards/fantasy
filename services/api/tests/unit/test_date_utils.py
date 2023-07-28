from datetime import datetime

import pytest
import pytz

from app.core.date_utils import hours_since
from tests.asserts import are_equal

hours_since_cases = [
    (datetime(2021, 8, 15, 2, 0, 0, tzinfo=pytz.utc), datetime(2021, 8, 16, 2, 0, 0, tzinfo=pytz.utc), 24),
    (datetime(2021, 8, 15, 2, 0, 0, tzinfo=pytz.utc), datetime(2021, 8, 16, 11, 0, 0, tzinfo=pytz.utc), 33),
]


@pytest.mark.parametrize("start, end, expected", hours_since_cases)
def test_hours_since(start, end, expected):
    actual = hours_since(start, end)

    are_equal(expected, actual)
