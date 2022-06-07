import pytest
from api.tests.asserts import are_equal
from yards_py.domain.entities.roster import Roster

from yards_py.domain.entities.schedule import Matchup, PlayoffType, ScheduleWeek
from services.api.app.domain.enums.matchup_type import MatchupType
from services.api.app.domain.enums.week_type import WeekType
from services.api.app.domain.services.schedule_service import generate_playoffs

# MANAGERS
team_1 = Roster(id=1, name="team 1", rank=1)
team_2 = Roster(id=2, name="team 2", rank=2)
team_3 = Roster(id=3, name="team 3", rank=3)
team_4 = Roster(id=4, name="team 4", rank=4)
team_5 = Roster(id=5, name="team 5", rank=5)
team_6 = Roster(id=6, name="team 6", rank=6)
team_7 = Roster(id=7, name="team 7", rank=7)
team_8 = Roster(id=8, name="team 8", rank=8)

teams = [
    team_1,
    team_2,
    team_3,
    team_4,
    team_5,
    team_6,
    team_7,
    team_8,
]


@pytest.mark.parametrize("team_count", [(2), (4), (6), (8)])
def test_week1_assign_playoff_matchups_top2_no_loser_game(team_count: int):
    rosters = teams[0:team_count]

    previous_week = ScheduleWeek(week_number=0, week_type=WeekType.REGULAR)
    playoffs = generate_playoffs(team_count, PlayoffType.TOP_2, first_playoff_week=2, enable_loser_playoff=False)
    week = playoffs[0]
    week.assign_playoff_matchups(PlayoffType.TOP_2, rosters, previous_week)

    championship = week.matchups[0]
    are_equal(team_2, championship.away)
    are_equal(team_1, championship.home)


@pytest.mark.parametrize("team_count", [(4), (6), (8)])
def test_week1_assign_playoff_matchups_top2_loser_game(team_count: int):
    rosters = teams[0:team_count]

    previous_week = ScheduleWeek(week_number=0, week_type=WeekType.REGULAR)
    playoffs = generate_playoffs(team_count, PlayoffType.TOP_2, first_playoff_week=2, enable_loser_playoff=True)
    week = playoffs[0]
    week.assign_playoff_matchups(PlayoffType.TOP_2, rosters, previous_week)

    loser_game = week.matchups[1]
    last_place = rosters[-1]
    second_last = rosters[-2]
    are_equal(last_place, loser_game.away)
    are_equal(second_last, loser_game.home)


@pytest.mark.parametrize("team_count", [(4), (6), (8)])
def test_week1_assign_playoff_matchups_top3_no_loser_game(team_count: int):
    rosters = teams[0:team_count]

    previous_week = ScheduleWeek(week_number=0, week_type=WeekType.REGULAR)
    weeks = generate_playoffs(team_count, PlayoffType.TOP_3, first_playoff_week=2, enable_loser_playoff=False)
    week1 = weeks[0]
    week1.assign_playoff_matchups(PlayoffType.TOP_3, rosters, previous_week)

    matchup = week1.matchups[0]
    are_equal(team_3, matchup.away)
    are_equal(team_2, matchup.home)

    bye = week1.matchups[1]
    are_equal(None, bye.away)
    are_equal(team_1, bye.home)


@pytest.mark.parametrize("team_count", [(6), (8)])
def test_week1_assign_playoff_matchups_top3_loser_game(team_count: int):
    rosters = teams[0:team_count]

    previous_week = ScheduleWeek(week_number=0, week_type=WeekType.REGULAR)
    playoffs = generate_playoffs(team_count, PlayoffType.TOP_3, first_playoff_week=2, enable_loser_playoff=True)
    week = playoffs[0]
    week.assign_playoff_matchups(PlayoffType.TOP_3, rosters, previous_week)

    loser_game = week.matchups[2]
    last_place = rosters[-1]
    second_last = rosters[-2]
    are_equal(last_place, loser_game.away)
    are_equal(second_last, loser_game.home)


@pytest.mark.parametrize("home_wins", [(True), (False)])
def test_week2_assign_playoff_matchups_top3(home_wins: bool):
    previous_week = ScheduleWeek(week_number=0, week_type=WeekType.REGULAR)
    playoffs = generate_playoffs(teams, PlayoffType.TOP_3, first_playoff_week=2, enable_loser_playoff=False)
    week1 = playoffs[0]
    # setup week 1
    week1.assign_playoff_matchups(PlayoffType.TOP_3, teams, previous_week)

    for matchup in week1.matchups:
        if matchup.type != MatchupType.PLAYOFF_BYE:
            matchup.home_score = 100 if home_wins else 0
            matchup.away_score = 100 if not home_wins else 0

    week2 = playoffs[1]
    week2.assign_playoff_matchups(PlayoffType.TOP_3, teams, week1)

    matchup = week2.matchups[0]
    are_equal(team_1.id, matchup.home.id)
    if home_wins:
        are_equal(team_2.id, matchup.away.id)
    else:
        are_equal(team_3.id, matchup.away.id)


@pytest.mark.parametrize("team_count", [(4), (6), (8)])
def test_week1_assign_playoff_matchups_top4_no_loser_game(team_count: int):
    rosters = teams[0:team_count]

    previous_week = ScheduleWeek(week_number=0, week_type=WeekType.REGULAR)
    weeks = generate_playoffs(team_count, PlayoffType.TOP_4, first_playoff_week=2, enable_loser_playoff=False)
    week1 = weeks[0]
    week1.assign_playoff_matchups(PlayoffType.TOP_4, rosters, previous_week)

    matchup1 = week1.matchups[0]
    are_equal(team_4, matchup1.away)
    are_equal(team_1, matchup1.home)

    matchup2 = week1.matchups[1]
    are_equal(team_3, matchup2.away)
    are_equal(team_2, matchup2.home)


@pytest.mark.parametrize("team_count", [(6), (8)])
def test_week1_assign_playoff_matchups_top4_loser_game(team_count: int):
    rosters = teams[0:team_count]

    previous_week = ScheduleWeek(week_number=0, week_type=WeekType.REGULAR)
    playoffs = generate_playoffs(team_count, PlayoffType.TOP_4, first_playoff_week=2, enable_loser_playoff=True)
    week = playoffs[0]
    week.assign_playoff_matchups(PlayoffType.TOP_4, rosters, previous_week)

    loser_game = week.matchups[2]
    last_place = rosters[-1]
    second_last = rosters[-2]
    are_equal(last_place, loser_game.away)
    are_equal(second_last, loser_game.home)


@pytest.mark.parametrize("home_wins", [(True), (False)])
def test_week2_assign_playoff_matchups_top4(home_wins: bool):
    previous_week = ScheduleWeek(week_number=0, week_type=WeekType.REGULAR)
    playoffs = generate_playoffs(teams, PlayoffType.TOP_4, first_playoff_week=2, enable_loser_playoff=False)
    week1 = playoffs[0]
    # setup week 1
    week1.assign_playoff_matchups(PlayoffType.TOP_4, teams, previous_week)

    for matchup in week1.matchups:
        if matchup.type == MatchupType.PLAYOFF:
            matchup.home_score = 100 if home_wins else 0
            matchup.away_score = 100 if not home_wins else 0

    week2 = playoffs[1]
    week2.assign_playoff_matchups(PlayoffType.TOP_4, teams, week1)

    matchup = week2.matchups[0]
    if home_wins:
        are_equal(team_1.id, matchup.home.id)
        are_equal(team_2.id, matchup.away.id)
    else:
        are_equal(team_3.id, matchup.home.id)
        are_equal(team_4.id, matchup.away.id)


@pytest.mark.parametrize("team_count", [(6), (8)])
def test_week1_assign_playoff_matchups_top6_no_loser_game(team_count: int):
    rosters = teams[0:team_count]

    previous_week = ScheduleWeek(week_number=0, week_type=WeekType.REGULAR)
    weeks = generate_playoffs(team_count, PlayoffType.TOP_6, first_playoff_week=2, enable_loser_playoff=False)
    week1 = weeks[0]
    week1.assign_playoff_matchups(PlayoffType.TOP_6, rosters, previous_week)

    matchup1 = week1.matchups[0]
    are_equal(team_6, matchup1.away)
    are_equal(team_3, matchup1.home)

    matchup2 = week1.matchups[1]
    are_equal(team_5, matchup2.away)
    are_equal(team_4, matchup2.home)

    matchup3 = week1.matchups[2]
    are_equal(None, matchup3.away)
    are_equal(team_1, matchup3.home)

    matchup4 = week1.matchups[3]
    are_equal(None, matchup4.away)
    are_equal(team_2, matchup4.home)


@pytest.mark.parametrize("team_count", [(8)])
def test_week1_assign_playoff_matchups_top6_loser_game(team_count: int):
    rosters = teams[0:team_count]

    previous_week = ScheduleWeek(week_number=0, week_type=WeekType.REGULAR)
    playoffs = generate_playoffs(team_count, PlayoffType.TOP_6, first_playoff_week=2, enable_loser_playoff=True)
    week = playoffs[0]
    week.assign_playoff_matchups(PlayoffType.TOP_6, rosters, previous_week)

    loser_game = week.matchups[4]
    last_place = rosters[-1]
    second_last = rosters[-2]
    are_equal(last_place, loser_game.away)
    are_equal(second_last, loser_game.home)


@pytest.mark.parametrize("home_wins", [(True), (False)])
def test_week2_assign_playoff_matchups_top6(home_wins: bool):
    previous_week = ScheduleWeek(week_number=0, week_type=WeekType.REGULAR)
    playoffs = generate_playoffs(teams, PlayoffType.TOP_6, first_playoff_week=2, enable_loser_playoff=False)
    week1 = playoffs[0]
    # setup week 1
    week1.assign_playoff_matchups(PlayoffType.TOP_6, teams, previous_week)

    for matchup in week1.matchups:
        if matchup.type != MatchupType.PLAYOFF_BYE:
            matchup.home_score = 100 if home_wins else 0
            matchup.away_score = 100 if not home_wins else 0

    week2 = playoffs[1]
    week2.assign_playoff_matchups(PlayoffType.TOP_6, teams, week1)

    matchup1 = week2.matchups[0]
    matchup2 = week2.matchups[1]
    are_equal(team_1.id, matchup1.home.id)
    are_equal(team_2.id, matchup2.home.id)
    if home_wins:
        are_equal(team_4.id, matchup1.away.id)
        are_equal(team_3.id, matchup2.away.id)
    else:
        are_equal(team_6.id, matchup1.away.id)
        are_equal(team_5.id, matchup2.away.id)


@pytest.mark.parametrize("home_wins", [(True), (False)])
def test_week3_assign_playoff_matchups_top6(home_wins: bool):
    previous_week = ScheduleWeek(week_number=0, week_type=WeekType.REGULAR)
    playoffs = generate_playoffs(teams, PlayoffType.TOP_6, first_playoff_week=2, enable_loser_playoff=False)
    week1 = playoffs[0]
    # setup week 1
    week1.assign_playoff_matchups(PlayoffType.TOP_6, teams, previous_week)

    for matchup in week1.matchups:
        if matchup.type != MatchupType.PLAYOFF_BYE:
            matchup.home_score = 100 if home_wins else 0
            matchup.away_score = 100 if not home_wins else 0

    week2 = playoffs[1]
    week2.assign_playoff_matchups(PlayoffType.TOP_6, teams, week1)

    for matchup in week2.matchups:
        matchup.home_score = 100 if home_wins else 0
        matchup.away_score = 100 if not home_wins else 0

    week3 = playoffs[2]
    week3.assign_playoff_matchups(PlayoffType.TOP_6, teams, week2)

    matchup = week3.matchups[0]
    if home_wins:
        are_equal(team_1.id, matchup.home.id)
        are_equal(team_2.id, matchup.away.id)
    else:
        are_equal(team_5.id, matchup.home.id)
        are_equal(team_6.id, matchup.away.id)


def test_assign_winners_week2_away_win_home_win():
    previous_week = ScheduleWeek(week_number=1, week_type=WeekType.PLAYOFFS)
    previous_week.matchups = [
        Matchup(id="01", away=team_3, home=team_2, type=MatchupType.PLAYOFF, away_score=100, home_score=50),
        Matchup(id="02", away=team_4, home=team_1, type=MatchupType.PLAYOFF, away_score=50, home_score=100)
    ]

    current_week = ScheduleWeek(week_number=2, week_type=WeekType.CHAMPIONSHIP)
    current_week.matchups = [
        Matchup(id="01", type=MatchupType.CHAMPIONSHIP)
    ]

    current_week.assign_playoff_matchups(PlayoffType.TOP_4, teams, previous_week)
    matchup = current_week.matchups[0]
    are_equal(matchup.away, team_3)
    are_equal(matchup.home, team_1)
