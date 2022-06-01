from typing import List
from api.app.domain.entities.roster import Roster
from api.app.domain.entities.schedule import MatchupType, PlayoffType
import pytest
from api.app.domain.services.schedule_service import ScheduledMatchup, combine_schedule, generate_schedule, get_sequence_for_count
from api.tests.asserts import are_equal

SEASON_WEEKS = 21

# MANAGERS
teams = [
    Roster(id=1, name="team 1"),
    Roster(id=2, name="team 2"),
    Roster(id=3, name="team 3"),
    Roster(id=4, name="team 4"),
    Roster(id=5, name="team 5"),
    Roster(id=6, name="team 6"),
    Roster(id=7, name="team 7"),
    Roster(id=8, name="team 8"),
]

teamCounts = [2, 4, 6, 8]
playoffTypes = [
    {"type": PlayoffType.TOP_2, "weeks": 1},
    {"type": PlayoffType.TOP_3, "weeks": 2},
    {"type": PlayoffType.TOP_4, "weeks": 2},
    {"type": PlayoffType.TOP_6, "weeks": 3},
]

combinations = [
    (teamCounts[0], playoffTypes[0]),
    (teamCounts[0], playoffTypes[1]),
    (teamCounts[0], playoffTypes[2]),
    (teamCounts[0], playoffTypes[3]),

    (teamCounts[1], playoffTypes[0]),
    (teamCounts[1], playoffTypes[1]),
    (teamCounts[1], playoffTypes[2]),
    (teamCounts[1], playoffTypes[3]),

    (teamCounts[2], playoffTypes[0]),
    (teamCounts[2], playoffTypes[1]),
    (teamCounts[2], playoffTypes[2]),
    (teamCounts[2], playoffTypes[3]),

    (teamCounts[3], playoffTypes[0]),
    (teamCounts[3], playoffTypes[1]),
    (teamCounts[3], playoffTypes[2]),
    (teamCounts[3], playoffTypes[3]),
]


def test_combine_schedule():
    season_weeks = 5
    regular_season = [1, 2, 3, 4, 5]
    playoffs = [1, 2]

    expected = 5  # max for entire season
    actual = len(combine_schedule(season_weeks, regular_season, playoffs))

    are_equal(expected, actual)


@pytest.mark.parametrize("team_count, playoff_type", combinations)
def test_correct_week_count_for_playoff_type(team_count, playoff_type):
    active_teams = teams[0:team_count]
    first_playoff_week = 7
    enable_loser_playoff = False

    expected = first_playoff_week - 1 + playoff_type["weeks"]
    schedule = generate_schedule(SEASON_WEEKS, active_teams, first_playoff_week, playoff_type["type"], enable_loser_playoff)
    actual = len(schedule)

    are_equal(expected, actual)


@pytest.mark.parametrize("team_count", teamCounts)
def test_correct_matchup_counts_per_week(team_count):
    active_teams = teams[0:team_count]

    # irrelevant for the test, but required for the function
    playoff_type = PlayoffType.TOP_2
    first_playoff_week = 5
    enable_loser_playoff = False

    expected = team_count / 2
    schedule = generate_schedule(SEASON_WEEKS, active_teams, first_playoff_week, playoff_type, enable_loser_playoff)
    actual = len(schedule[0].matchups)

    are_equal(expected, actual)


@pytest.mark.parametrize("team_count", teamCounts)
def test_no_duplicate_matchups(team_count):
    weeks = get_sequence_for_count(team_count)

    checked_matchups = []  # type:List[ScheduledMatchup]
    duplicates_found = []

    for week in weeks:
        for game in week:
            matches = [m for m in checked_matchups if m.home == game.home and m.away == game.away]
            if matches:
                duplicates_found.extend(matches)
            else:
                checked_matchups.append(game)

    are_equal(0, len(duplicates_found))


@pytest.mark.parametrize("team_count", teamCounts)
def test_1_match_per_team_per_week(team_count):
    weeks = get_sequence_for_count(team_count)

    bad_weeks = []

    for week in weeks:
        for x in range(0, team_count):
            matchups_for_team = [m for m in week if m.home == x or m.away == x]

            if len(matchups_for_team) != 1:
                bad_weeks.append(week)

    are_equal(0, len(bad_weeks))


@pytest.mark.parametrize("team_count", teamCounts)
def test_equal_number_of_matchups_per_team(team_count):
    weeks = get_sequence_for_count(team_count)

    game_count = {}

    for week in weeks:
        for x in range(0, team_count):
            matchups_for_team = [m for m in week if m.home == x or m.away == x]

            if x not in game_count:
                game_count[x] = 0
            game_count[x] += len(matchups_for_team)

    expected_count = game_count[0]
    all_equal = True

    for team_id in range(0, team_count):
        count = game_count[team_id]
        if count != expected_count:
            all_equal = False

    are_equal(True, all_equal)


def test_cannot_exceed_season_length():
    active_teams = teams[0:6]

    schedule = generate_schedule(season_weeks=21, rosters=active_teams, first_playoff_week=21, playoff_type=PlayoffType.TOP_4, enable_loser_playoff=False)

    expected = 21
    actual = len(schedule)

    are_equal(expected, actual)


def test_can_generate_loser_league_game():
    active_teams = teams[0:4]

    schedule = generate_schedule(season_weeks=21, rosters=active_teams, first_playoff_week=5, playoff_type=PlayoffType.TOP_2, enable_loser_playoff=True)

    playoff_week = schedule[-1]
    loser_game = [m for m in playoff_week.matchups if m.type == MatchupType.LOSER]

    expected = 1
    actual = len(loser_game)

    are_equal(expected, actual)


def test_no_loser_game_if_not_enough_teams():
    active_teams = teams[0:4]

    # all four make the playoffs, can't have a loser game
    schedule = generate_schedule(season_weeks=21, rosters=active_teams, first_playoff_week=5, playoff_type=PlayoffType.TOP_4, enable_loser_playoff=True)

    playoff_week = schedule[-1]
    loser_game = [m for m in playoff_week.matchups if m.type == MatchupType.LOSER]

    expected = 0
    actual = len(loser_game)

    are_equal(expected, actual)


@pytest.mark.parametrize("team_count, playoff_type", combinations)
def test_week_ids_match(team_count, playoff_type):
    active_teams = teams[0:team_count]
    first_playoff_week = 20
    enable_loser_playoff = False

    schedule = generate_schedule(SEASON_WEEKS, active_teams, first_playoff_week, playoff_type["type"], enable_loser_playoff)

    week_number = 1
    for week in schedule:
        are_equal(week_number, week.week_number)
        week_number += 1
