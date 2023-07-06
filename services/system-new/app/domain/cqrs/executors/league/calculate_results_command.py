
from app.yards_py.core.logging import Logger
from app.yards_py.core.publisher import Publisher
from app.di import create_publisher
from app.domain.commands.league.calculate_playoffs import CalculatePlayoffsCommand
from app.yards_py.domain.entities.league import League
from app.yards_py.domain.enums.league_command_type import LeagueCommandType
from app.yards_py.domain.enums.matchup_type import MatchupType
from app.yards_py.domain.repositories.game_repository import GameRepository, create_game_repository
from app.yards_py.domain.repositories.player_league_season_score_repository import PlayerLeagueSeasonScoreRepository, create_player_league_season_score_repository
from app.yards_py.domain.entities.matchup_preview import MatchupPreview
from app.yards_py.domain.repositories.state_repository import StateRepository, create_state_repository
from app.yards_py.domain.repositories.user_league_repository import UserLeagueRepository, create_user_league_repository
from app.yards_py.domain.enums.week_type import WeekType
from app.yards_py.domain.entities.schedule import Schedule
from app.yards_py.domain.repositories.league_repository import LeagueRepository, create_league_repository
from app.yards_py.domain.entities.roster import Roster
from app.yards_py.domain.repositories.league_week_matchup_repository import LeagueWeekMatchupRepository, create_league_week_matchup_repository
from app.yards_py.domain.repositories.league_roster_repository import LeagueRosterRepository, create_league_roster_repository
from app.yards_py.domain.repositories.league_config_repository import LeagueConfigRepository, create_league_config_repository
from typing import Optional
from fastapi import Depends
from app.yards_py.core.annotate_args import annotate_args
from app.yards_py.core.base_command_executor import BaseCommand, BaseCommandResult, BaseCommandExecutor
from firebase_admin import firestore

from app.domain.services.league_command_push_data import LeagueCommandPushData
from app.yards_py.domain.services.notification_service import NotificationService, create_notification_service
from app.yards_py.domain.topics import LEAGUE_COMMAND_TOPIC


def create_calculate_results_command_executor(
    state_repo: StateRepository = Depends(create_state_repository),
    league_config_repo: LeagueConfigRepository = Depends(create_league_config_repository),
    league_roster_repo: LeagueRosterRepository = Depends(create_league_roster_repository),
    matchup_repo: LeagueWeekMatchupRepository = Depends(create_league_week_matchup_repository),
    league_repo: LeagueRepository = Depends(create_league_repository),
    user_league_repo: UserLeagueRepository = Depends(create_user_league_repository),
    player_score_repo: PlayerLeagueSeasonScoreRepository = Depends(create_player_league_season_score_repository),
    game_repo: GameRepository = Depends(create_game_repository),
    publisher: Publisher = Depends(create_publisher),
    notification_service: NotificationService = Depends(create_notification_service),
):
    return CalculateResultsCommandExecutor(
        state_repo=state_repo,
        league_config_repo=league_config_repo,
        league_roster_repo=league_roster_repo,
        matchup_repo=matchup_repo,
        league_repo=league_repo,
        user_league_repo=user_league_repo,
        player_score_repo=player_score_repo,
        game_repo=game_repo,
        publisher=publisher,
        notification_service=notification_service,
    )


@annotate_args
class CalculateResultsCommand(BaseCommand):
    league_id: Optional[str]
    week_number: int
    past_week: bool = False


@annotate_args
class CalculateResultsResult(BaseCommandResult[CalculateResultsCommand]):
    next_week_is_playoffs: bool = False
    league_season_complete: bool = False
    results_message: Optional[str]
    league: Optional[League]


class CalculateResultsCommandExecutor(BaseCommandExecutor[CalculateResultsCommand, CalculateResultsResult]):
    def __init__(
        self,
        state_repo: StateRepository,
        league_config_repo: LeagueConfigRepository,
        league_roster_repo: LeagueRosterRepository,
        matchup_repo: LeagueWeekMatchupRepository,
        league_repo: LeagueRepository,
        user_league_repo: UserLeagueRepository,
        player_score_repo: PlayerLeagueSeasonScoreRepository,
        game_repo: GameRepository,
        publisher: Publisher,
        notification_service: NotificationService,

    ):
        self.state_repo = state_repo
        self.league_config_repo = league_config_repo
        self.league_roster_repo = league_roster_repo
        self.matchup_repo = matchup_repo
        self.league_repo = league_repo
        self.user_league_repo = user_league_repo
        self.player_score_repo = player_score_repo
        self.game_repo = game_repo
        self.publisher = publisher
        self.notification_service = notification_service

    def on_execute(self, command: CalculateResultsCommand) -> CalculateResultsResult:
        league = self.league_repo.get(command.league_id)

        state = self.state_repo.get()
        if not league.is_active_for_season(state.current_season):
            Logger.warn(f"League {command.league_id} is not active for season {state.current_season} but is receiving league events")
            return CalculateResultsResult(command=command)

        schedule_config = self.league_config_repo.get_schedule_config(command.league_id)

        if not schedule_config or not schedule_config.first_playoff_week:
            return CalculateResultsResult(command=command)

        last_playoff_week = schedule_config.first_playoff_week + schedule_config.playoff_type.weeks

        if state.current_week > last_playoff_week:
            return CalculateResultsResult(command=command)

        #  This happens first, to block users from adding players in the event that the next part fails.
        @firestore.transactional
        def mark_league_waivers_active(transaction):
            league_state = self.league_config_repo.get_state(command.league_id, transaction)

            league_state.waivers_active = True
            self.league_config_repo.set_state(command.league_id, league_state, transaction)

        transaction = self.league_repo.firestore.create_transaction()
        mark_league_waivers_active(transaction)
        
        self.games_for_week = self.game_repo.for_week(state.current_season, command.week_number)
        self.league_scoring = self.league_config_repo.get_scoring_config(command.league_id)

        @firestore.transactional
        def calculate(transaction) -> CalculateResultsResult:
            results_message = f"Week {command.week_number} summary\n\n"
            league = self.league_repo.get(command.league_id, transaction)

            rosters = self.league_roster_repo.get_all(command.league_id, transaction)
            rosters = {roster.id: roster for roster in rosters}
            matchups = self.matchup_repo.get_all(command.league_id, command.week_number, transaction)
            schedule = self.league_config_repo.get_schedule_config(command.league_id, transaction)
            week_index = command.week_number - 1

            for matchup in matchups:
                schedule_matchup = next(m for m in schedule.weeks[week_index].matchups if m.id == matchup.id)
                if not matchup.home and not matchup.away:
                    continue  # not sure how this would happen, but there's nothing to calculate

                if matchup.home:
                    if not command.past_week:  # don't copy current roster if re-calculating a previous week
                        matchup.home = self.archive_roster(rosters[matchup.home.id])
                    matchup.home.this_week_points_for = matchup.home.calculate_score()
                    matchup.home.this_week_bench_points_for = matchup.home.calculate_bench_score()
                    matchup.home_score = matchup.home.this_week_points_for

                if matchup.away:
                    if not command.past_week:
                        matchup.away = self.archive_roster(rosters[matchup.away.id])
                    matchup.away.this_week_points_for = matchup.away.calculate_score()
                    matchup.away.this_week_bench_points_for = matchup.away.calculate_bench_score()
                    matchup.away_score = matchup.away.this_week_points_for

                if matchup.home and matchup.away:
                    home_won = matchup.home_score > matchup.away_score
                    tied = matchup.away_score == matchup.home_score

                    if tied and matchup.type == MatchupType.REGULAR:
                        results_message += f"{matchup.away.name} tied {matchup.home.name} at {matchup.away_score}\n"
                    elif home_won or tied and matchup.type != MatchupType.REGULAR:
                        results_message += f"{matchup.home.name} defeated {matchup.away.name}, {matchup.home_score:.2f} - {matchup.away_score:.2f}\n"
                        if matchup.type == MatchupType.CHAMPIONSHIP:
                            results_message += f"\n{matchup.home.name} is the {state.current_season} league champion! 🏆"
                    else:
                        results_message += f"{matchup.away.name} defeated {matchup.home.name}, {matchup.away_score:.2f} - {matchup.home_score:.2f}\n"
                        if matchup.type == MatchupType.CHAMPIONSHIP:
                            results_message += f"\n{matchup.away.name} is the {state.current_season} league champion! 🏆"

                schedule_matchup.away_score = matchup.away_score
                schedule_matchup.home_score = matchup.home_score

                self.matchup_repo.set(command.league_id, command.week_number, matchup, transaction)

            league_season_complete = len(schedule.weeks) <= week_index + 1
            next_week_matchups = schedule.weeks[week_index + 1].matchups if len(schedule.weeks) > week_index + 1 else None
            next_week_playoffs = schedule.weeks[week_index + 1].week_type.is_playoffs() if len(schedule.weeks) > week_index + 1 else False

            for roster in rosters.values():
                update_record(roster, command.week_number, schedule, league.league_start_week)
                if next_week_matchups:
                    roster_matchup = next((m for m in next_week_matchups if (m.away and m.away.id == roster.id) or (m.home and m.home.id == roster.id)), None)
                    if roster_matchup:
                        roster_matchup = MatchupPreview.from_matchup(roster_matchup)
                    else:
                        roster_matchup = None

                    updates = {
                        "matchup": roster_matchup.dict() if roster_matchup else None
                    }

                    self.user_league_repo.partial_update(roster.id, command.league_id, updates, transaction)

            for week in schedule.weeks:
                if week.week_number <= command.week_number:
                    continue

                for matchup in week.matchups:
                    if matchup.away:
                        if not command.past_week:
                            matchup.away = rosters[matchup.away.id].copy(deep=True)
                        matchup.away.positions = []
                        matchup.away.waiver_bids = []
                        matchup.away.processed_waiver_bids = []

                    if matchup.home:
                        if not command.past_week:
                            matchup.home = rosters[matchup.home.id].copy(deep=True)
                        matchup.home.positions = []
                        matchup.home.waiver_bids = []
                        matchup.home.processed_waiver_bids = []

            rosters = list(rosters.values())
            rosters = Roster.sort(rosters)

            rank = 1
            for roster in rosters:
                roster.rank = rank
                rank += 1
                roster.this_week_points_for = 0
                roster.this_week_bench_points_for = 0

                for position in roster.positions.values():
                    position.game_score = 0

                self.league_roster_repo.set(command.league_id, roster, transaction)

            self.league_config_repo.set_schedule_config(command.league_id, schedule, transaction)

            return CalculateResultsResult(
                command=command,
                next_week_is_playoffs=next_week_playoffs,
                league_season_complete=league_season_complete,
                results_message=results_message,
                league=league,
            )

        transaction = self.league_roster_repo.firestore.create_transaction()
        result = calculate(transaction)

        if result.success and not command.past_week:
            self.notification_service.send_weekly_summary(result.league, result.results_message)

        if result.success and result.next_week_is_playoffs:
            command = CalculatePlayoffsCommand(league_id=command.league_id, week_number=command.week_number + 1)
            payload = LeagueCommandPushData(command_type=LeagueCommandType.CALCULATE_PLAYOFFS, command_data=command.dict())
            self.publisher.publish(payload, LEAGUE_COMMAND_TOPIC)

        return result

    def archive_roster(self, roster: Roster):
        copy = roster.copy(deep=True)

        for position in copy.positions.values():
            if position.player:
                for game in self.games_for_week:
                    if position.player.id in game.player_stats:
                        game_stats = game.player_stats[position.player.id]
                        score = self.league_scoring.calculate_score(game_stats.stats)

                        position.game_id = game.id
                        position.game_score = score.total_score

        return copy


def update_record(roster: Roster, up_to_week: int, schedule: Schedule, league_start_week: int):
    wins = 0
    losses = 0
    ties = 0
    total_score_for = 0.0
    total_score_against = 0.0
    last_result = "-"

    for week in schedule.weeks:
        if week.week_number < league_start_week:
            continue

        if week.week_number > up_to_week or week.week_type != WeekType.REGULAR:
            break

        matchup = next(m for m in week.matchups if m.away and m.away.id == roster.id or m.home and m.home.id == roster.id)

        if matchup:
            score_for = matchup.away_score if matchup.away and matchup.away.id == roster.id else matchup.home_score
            score_against = matchup.home_score if matchup.away and matchup.away.id == roster.id else matchup.away_score

            total_score_for += score_for
            total_score_against += score_for

            won = score_for > score_against
            lost = score_for < score_against
            tied = score_for == score_against

            if won:
                wins += 1
                last_result = "W"

            if lost:
                losses += 1
                last_result = "L"

            if tied:
                ties += 1
                last_result = "T"

    roster.wins = wins
    roster.losses = losses
    roster.ties = ties
    roster.record = Roster.format_record(roster)
    roster.wl_points = Roster.calculate_wl_points(roster)
    roster.last_week_result = last_result
    roster.points_for = total_score_for
    roster.points_against = total_score_against
