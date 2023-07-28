from typing import List

from pydantic.main import BaseModel

from app.core.exceptions import NotSupportedException
from app.domain.entities.roster import Roster
from app.domain.entities.schedule import Matchup, MatchupType, PlayoffType, ScheduleWeek, WeekType


class ScheduledMatchup(BaseModel):
    away: int
    home: int


def matchup(away: int, home: int) -> ScheduledMatchup:
    return ScheduledMatchup(away=away, home=home)


def two_teams() -> List[List[ScheduledMatchup]]:
    return [
        [matchup(0, 1)],
        # reverse
        [matchup(1, 0)],
    ]


def four_teams() -> List[List[ScheduledMatchup]]:
    return [
        [matchup(0, 1), matchup(2, 3)],
        [matchup(0, 2), matchup(1, 3)],
        [matchup(0, 3), matchup(1, 2)],
        #  reverse
        [matchup(1, 0), matchup(3, 2)],
        [matchup(2, 0), matchup(3, 1)],
        [matchup(3, 0), matchup(2, 1)],
    ]


def six_teams() -> List[List[ScheduledMatchup]]:
    return [
        [matchup(0, 1), matchup(2, 3), matchup(4, 5)],
        [matchup(0, 2), matchup(1, 4), matchup(3, 5)],
        [matchup(0, 3), matchup(1, 5), matchup(2, 4)],
        [matchup(0, 4), matchup(1, 3), matchup(2, 5)],
        [matchup(0, 5), matchup(1, 2), matchup(3, 4)],
        # reverse
        [matchup(1, 0), matchup(3, 2), matchup(5, 4)],
        [matchup(2, 0), matchup(4, 1), matchup(5, 3)],
        [matchup(3, 0), matchup(5, 1), matchup(4, 2)],
        [matchup(4, 0), matchup(3, 1), matchup(5, 2)],
        [matchup(5, 0), matchup(2, 1), matchup(4, 3)],
    ]


def eight_teams() -> List[List[ScheduledMatchup]]:
    return [
        [matchup(0, 4), matchup(1, 5), matchup(2, 6), matchup(3, 7)],
        [matchup(0, 1), matchup(2, 4), matchup(3, 5), matchup(7, 6)],
        [matchup(0, 2), matchup(3, 1), matchup(7, 4), matchup(6, 5)],
        [matchup(0, 3), matchup(7, 2), matchup(6, 1), matchup(5, 4)],
        [matchup(0, 7), matchup(6, 3), matchup(5, 2), matchup(4, 1)],
        [matchup(0, 6), matchup(5, 7), matchup(4, 3), matchup(1, 2)],
        [matchup(0, 5), matchup(4, 6), matchup(1, 7), matchup(2, 3)],
        # reverse
        [matchup(4, 0), matchup(5, 1), matchup(6, 2), matchup(7, 3)],
        [matchup(1, 0), matchup(4, 2), matchup(5, 3), matchup(6, 7)],
        [matchup(2, 0), matchup(1, 3), matchup(4, 7), matchup(5, 6)],
        [matchup(3, 0), matchup(2, 7), matchup(1, 6), matchup(4, 5)],
        [matchup(7, 0), matchup(3, 6), matchup(2, 5), matchup(1, 4)],
        [matchup(6, 0), matchup(7, 5), matchup(3, 4), matchup(2, 1)],
        [matchup(5, 0), matchup(6, 4), matchup(7, 1), matchup(3, 2)],
    ]


def ten_teams() -> List[List[ScheduledMatchup]]:
    return [
        [matchup(0, 9), matchup(1, 8), matchup(2, 7), matchup(3, 6), matchup(4, 5)],
        [matchup(8, 0), matchup(7, 9), matchup(6, 1), matchup(5, 2), matchup(4, 3)],
        [matchup(0, 7), matchup(8, 6), matchup(9, 5), matchup(1, 4), matchup(2, 3)],
        [matchup(6, 0), matchup(5, 7), matchup(4, 8), matchup(3, 9), matchup(2, 1)],
        [matchup(0, 5), matchup(6, 4), matchup(7, 3), matchup(8, 2), matchup(9, 1)],
        [matchup(4, 0), matchup(3, 5), matchup(2, 6), matchup(1, 7), matchup(9, 8)],
        [matchup(0, 3), matchup(2, 4), matchup(5, 1), matchup(6, 9), matchup(7, 8)],
        [matchup(2, 0), matchup(1, 3), matchup(9, 4), matchup(8, 5), matchup(7, 6)],
        [matchup(0, 1), matchup(9, 2), matchup(3, 8), matchup(4, 7), matchup(5, 6)],
        # reverse
        [matchup(9, 0), matchup(8, 1), matchup(7, 2), matchup(6, 3), matchup(5, 4)],
        [matchup(0, 8), matchup(9, 7), matchup(1, 6), matchup(2, 5), matchup(3, 4)],
        [matchup(7, 0), matchup(6, 8), matchup(5, 9), matchup(4, 1), matchup(3, 2)],
        [matchup(0, 6), matchup(7, 5), matchup(8, 4), matchup(9, 3), matchup(1, 2)],
        [matchup(5, 0), matchup(4, 6), matchup(3, 7), matchup(2, 8), matchup(1, 9)],
        [matchup(0, 4), matchup(5, 3), matchup(6, 2), matchup(7, 1), matchup(8, 9)],
        [matchup(3, 0), matchup(4, 2), matchup(1, 5), matchup(9, 6), matchup(8, 7)],
        [matchup(0, 2), matchup(3, 1), matchup(4, 9), matchup(5, 8), matchup(6, 7)],
        [matchup(1, 0), matchup(2, 9), matchup(8, 3), matchup(7, 4), matchup(6, 5)],
    ]


def get_sequence_for_count(teams: int):
    if teams == 2:
        return two_teams()
    elif teams == 4:
        return four_teams()
    elif teams == 6:
        return six_teams()
    elif teams == 8:
        return eight_teams()
    elif teams == 10:
        return ten_teams()
    else:
        raise NotSupportedException(f"Schedule for {teams} teams is not supported")


def generate_regular_season(
    number_of_weeks: int,
    sequence: List[List[ScheduledMatchup]],
    rosters: List[Roster],
) -> List[ScheduleWeek]:
    weeks = []

    for week_number in range(1, number_of_weeks + 1):
        games = sequence[0]
        week = ScheduleWeek(week_number=week_number, week_type=WeekType.REGULAR)

        for game in games:
            away = rosters[game.away]
            home = rosters[game.home]
            matchup = Matchup(away=away, home=home, type=MatchupType.REGULAR)
            week.matchups.append(matchup)

        weeks.append(week)

        sequence.append(sequence.pop(0))

    return weeks


def generate_top_2_playoffs(first_playoff_week: int) -> ScheduleWeek:
    championship_week = ScheduleWeek(week_number=first_playoff_week, week_type=WeekType.CHAMPIONSHIP)
    championship_week.matchups.append(Matchup(type=MatchupType.CHAMPIONSHIP))

    return championship_week


def generate_top_3_playoffs(first_playoff_week: int) -> List[ScheduleWeek]:
    week_1 = ScheduleWeek(week_number=first_playoff_week, week_type=WeekType.PLAYOFFS)
    week_1.matchups.append(Matchup(type=MatchupType.PLAYOFF))
    week_1.matchups.append(Matchup(type=MatchupType.PLAYOFF_BYE))

    championship_week = ScheduleWeek(week_number=first_playoff_week + 1, week_type=WeekType.CHAMPIONSHIP)
    championship_week.matchups.append(Matchup(type=MatchupType.CHAMPIONSHIP))

    return [week_1, championship_week]


def generate_top_4_playoffs(first_playoff_week: int) -> List[ScheduleWeek]:
    week_1 = ScheduleWeek(week_number=first_playoff_week, week_type=WeekType.PLAYOFFS)
    week_1.matchups.append(Matchup(type=MatchupType.PLAYOFF))
    week_1.matchups.append(Matchup(type=MatchupType.PLAYOFF))

    championship_week = ScheduleWeek(week_number=first_playoff_week + 1, week_type=WeekType.CHAMPIONSHIP)
    championship_week.matchups.append(Matchup(type=MatchupType.CHAMPIONSHIP))

    return [week_1, championship_week]


def generate_top_6_playoffs(first_playoff_week: int) -> List[ScheduleWeek]:
    week_1 = ScheduleWeek(week_number=first_playoff_week, week_type=WeekType.PLAYOFFS)
    week_1.matchups.append(Matchup(type=MatchupType.PLAYOFF))
    week_1.matchups.append(Matchup(type=MatchupType.PLAYOFF))
    week_1.matchups.append(Matchup(type=MatchupType.PLAYOFF_BYE))
    week_1.matchups.append(Matchup(type=MatchupType.PLAYOFF_BYE))

    week_2 = ScheduleWeek(week_number=first_playoff_week + 1, week_type=WeekType.PLAYOFFS)
    week_2.matchups.append(Matchup(type=MatchupType.PLAYOFF))
    week_2.matchups.append(Matchup(type=MatchupType.PLAYOFF))

    championship_week = ScheduleWeek(week_number=first_playoff_week + 2, week_type=WeekType.CHAMPIONSHIP)
    championship_week.matchups.append(Matchup(type=MatchupType.CHAMPIONSHIP))

    return [week_1, week_2, championship_week]


def generate_playoffs(
    total_teams: int,
    playoff_type: PlayoffType,
    first_playoff_week,
    enable_loser_playoff,
) -> List[ScheduleWeek]:
    playoffs = []  # type: List[ScheduleWeek]

    if playoff_type == PlayoffType.TOP_2:
        playoffs.append(generate_top_2_playoffs(first_playoff_week))
    elif playoff_type == PlayoffType.TOP_3:
        playoffs.extend(generate_top_3_playoffs(first_playoff_week))
    elif playoff_type == PlayoffType.TOP_4:
        playoffs.extend(generate_top_4_playoffs(first_playoff_week))
    elif playoff_type == PlayoffType.TOP_6:
        playoffs.extend(generate_top_6_playoffs(first_playoff_week))
    else:
        raise NotSupportedException(f"Playoff type '{playoff_type}' is not supported")

    if enable_loser_playoff:
        enough_teams = total_teams - playoff_type >= 2
        if enough_teams:
            loser_game = Matchup(type=MatchupType.LOSER)
            playoffs[0].matchups.append(loser_game)

    return playoffs


def combine_schedule(season_weeks: int, weeks: List[ScheduleWeek], playoffs: List[ScheduleWeek]) -> List[ScheduleWeek]:
    if len(weeks) + len(playoffs) > season_weeks:
        weeks_over = len(weeks) + len(playoffs) - season_weeks
        weeks = weeks[0 : len(weeks) - weeks_over]

    weeks.extend(playoffs)

    return weeks


def generate_schedule(season_weeks: int, rosters: List[Roster], first_playoff_week: int, playoff_type: PlayoffType, enable_loser_playoff: bool):
    sequence = get_sequence_for_count(len(rosters))
    number_of_weeks = first_playoff_week - 1

    weeks = generate_regular_season(number_of_weeks, sequence, rosters)
    playoffs = generate_playoffs(len(rosters), playoff_type, first_playoff_week, enable_loser_playoff)

    weeks = combine_schedule(season_weeks, weeks, playoffs)

    week_number = 1
    for week in weeks:
        week.week_id = f"{week_number:02}"
        week.week_number = week_number
        week_number += 1
        matchup_id = 1
        for matchup in week.matchups:
            matchup.id = str(matchup_id)
            matchup_id += 1

    assert len(weeks) <= season_weeks

    return weeks
