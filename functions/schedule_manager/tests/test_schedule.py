from datetime import datetime

from schedule_manager.scheduler import schedule
import pytest


@pytest.mark.parametrize("segment_start,segment_end,now,expected", [
    pytest.param(datetime(2022, 11, 15), datetime(2022, 11, 20), datetime(2022, 11, 17), True, id="date_within_segment"),
    pytest.param(datetime(2022, 11, 15), datetime(2022, 11, 20), datetime(2022, 11, 21), False, id="date_outside_segment"),
    pytest.param(datetime(2022, 11, 15), datetime(2022, 11, 20), datetime(2022, 11, 15), True, id="start_should_be_inclusive"),
    pytest.param(datetime(2022, 11, 15), datetime(2022, 11, 20), datetime(2022, 11, 20), False, id="end_should_be_exclusive"),
])
def test_is_active_segment(segment_start, segment_end, now, expected):
    segment = schedule.Segment(type="regular_season", date_start=schedule.cfl_time(segment_start), date_end=schedule.cfl_time(segment_end))
    actual = schedule.is_active_segment(schedule.cfl_time(now), segment)

    assert expected == actual, f"Expected: {expected}, Actual: {actual}"


@pytest.mark.parametrize("is_preseason,is_regular_season,is_playoffs,expected", [
    pytest.param(True, False, False, False, id="preseason"),
    pytest.param(False, True, False, False, id="regular_season"),
    pytest.param(False, False, True, False, id="playoffs"),
    pytest.param(False, False, False, True, id="offseason")
])
def test_is_offseason(is_preseason, is_regular_season, is_playoffs, expected):
    sched = schedule.Schedule.construct(**{
        "is_preseason": is_preseason,
        "is_regular_season": is_regular_season,
        "is_playoffs": is_playoffs,
    })
    actual = schedule.is_offseason(sched)

    assert expected == actual, f"Expected: {expected}, Actual: {actual}"
