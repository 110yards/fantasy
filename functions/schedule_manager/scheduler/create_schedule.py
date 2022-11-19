from datetime import timedelta
from typing import Dict, Iterable, List, Optional
from .schedule import Schedule, Game, Segment, Week

PRESEASON = 0
REGULAR_SEASON = 1
PLAYOFFS = 2
GREY_CUP = 3


def create_schedule(year: int, games: List[Game], post_week_buffer_hours: int) -> Schedule:
    schedule = Schedule(season=year)

    games = sorted(games, key=lambda x: x.date_start)

    preseason_games = [g for g in games if g.event_type.event_type_id == PRESEASON]
    regular_season_games = [g for g in games if g.event_type.event_type_id == REGULAR_SEASON]
    playoff_games = [g for g in games if g.event_type.event_type_id in (PLAYOFFS, GREY_CUP)]

    schedule.preseason = create_segment("preseason", preseason_games, post_week_buffer_hours)
    schedule.regular_season = create_segment("regular_season", regular_season_games, post_week_buffer_hours)
    schedule.playoffs = create_segment("playoffs", playoff_games, post_week_buffer_hours)

    schedule.set_state()
    schedule.calculate_hash()

    return schedule


def create_segment(type: str, games: Iterable[Game], post_week_buffer_hours: int) -> Segment:
    weeks: Dict[int, Week] = {}

    first_week = 99
    last_week = 0

    for game in games:
        if game.week not in weeks:
            weeks[game.week] = Week(week_number=game.week, date_start=game.date_start, date_end=game.date_start)

        if game.week < first_week:
            first_week = game.week

        if game.week > last_week:
            last_week = game.week

        weeks[game.week].games.append(game)

    for week in weeks.values():
        previous_week = weeks.get(week.week_number - 1)
        set_week_dates(week, previous_week, post_week_buffer_hours)

    segment = Segment(type=type, weeks=weeks)

    segment.date_start = weeks[first_week].date_start
    segment.date_end = weeks[last_week].date_end

    return segment


def set_week_dates(week: Week, previous_week: Optional[Week], post_week_buffer_hours: int):
    first_game = week.games[0]
    last_game = week.games[-1]

    # this will only take effect at the start of a new part of the season and doesn't matter much. (famous last words?)
    week.date_start = first_game.date_start + timedelta(days=-1)

    post_game_buffer = last_game.date_start + timedelta(hours=post_week_buffer_hours)  # X hours (probably 24) after the last game of the week.
    week.date_end = post_game_buffer + timedelta(days=1)  # next day
    week.date_end = week.date_end.replace(hour=0, minute=0, second=0)  # midnight next day

    if previous_week is not None:
        # week start = previous week end
        week.date_start = previous_week.date_end
