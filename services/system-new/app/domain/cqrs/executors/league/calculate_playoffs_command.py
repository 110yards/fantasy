from fastapi import Depends
from firebase_admin import firestore

from app.yards_py.core.annotate_args import annotate_args
from app.yards_py.core.base_command_executor import BaseCommand, BaseCommandExecutor, BaseCommandResult
from app.yards_py.domain.entities.matchup_preview import MatchupPreview
from app.yards_py.domain.enums.week_type import WeekType
from app.yards_py.domain.repositories.league_config_repository import LeagueConfigRepository, create_league_config_repository
from app.yards_py.domain.repositories.league_repository import LeagueRepository, create_league_repository
from app.yards_py.domain.repositories.league_roster_repository import LeagueRosterRepository, create_league_roster_repository
from app.yards_py.domain.repositories.league_week_matchup_repository import LeagueWeekMatchupRepository, create_league_week_matchup_repository
from app.yards_py.domain.repositories.public_repository import PublicRepository, create_public_repository
from app.yards_py.domain.repositories.user_league_repository import UserLeagueRepository, create_user_league_repository


@annotate_args
class CalculatePlayoffsCommand(BaseCommand):
    league_id: str
    week_number: int


@annotate_args
class CalculatePlayoffsResult(BaseCommandResult[CalculatePlayoffsCommand]):
    pass


class CalculatePlayoffsCommandExecutor(BaseCommandExecutor[CalculatePlayoffsCommand, CalculatePlayoffsResult]):
    def __init__(
        self,
        league_repo: LeagueRepository,
        league_config_repo: LeagueConfigRepository,
        roster_repo: LeagueRosterRepository,
        matchup_repo: LeagueWeekMatchupRepository,
        user_league_repo: UserLeagueRepository,
        public_repo: PublicRepository,
    ):
        self.league_repo = league_repo
        self.league_config_repo = league_config_repo
        self.roster_repo = roster_repo
        self.matchup_repo = matchup_repo
        self.user_league_repo = user_league_repo
        self.public_repo = public_repo

    def on_execute(self, command: CalculatePlayoffsCommand) -> CalculatePlayoffsResult:
        week_index = command.week_number - 1
        state = self.public_repo.get_state()

        @firestore.transactional
        def calculate(transaction):
            league = self.league_repo.get(command.league_id, transaction=transaction)

            if not league or not league.is_active_for_season(state.current_season):
                return CalculatePlayoffsResult(command=command)

            schedule = self.league_config_repo.get_schedule_config(command.league_id, transaction=transaction)
            week = schedule.weeks[week_index] if len(schedule.weeks) >= week_index + 1 else None
            previous_week = schedule.weeks[week_index - 1] if week else None

            if not week:
                return CalculatePlayoffsResult(command=command, error=f"Unable to find week {command.week_number} in schedule config")

            if week.week_type == WeekType.REGULAR:
                return CalculatePlayoffsResult(command=command, error=f"Week {command.week_number} is not a playoff week")

            rosters = self.roster_repo.get_all(command.league_id, transaction=transaction)

            week.assign_playoff_matchups(schedule.playoff_type, rosters, previous_week)
            self.league_config_repo.set_schedule_config(command.league_id, schedule, transaction=transaction)

            # the transactions here kind of suck - if this runs too soon after calculate_results
            # the schedule can be squashed.  But I also don't want to refactor this piece, since calculate_results shouldn't care about the previews
            # so this stuff is non-transactional - TODO: fix in v3.
            for matchup in week.matchups:
                self.matchup_repo.set(command.league_id, command.week_number, matchup)
                preview = MatchupPreview.from_matchup(matchup)
                if matchup.away:  # away is null for byes
                    league_preview = self.user_league_repo.get(matchup.away.id, command.league_id)
                    league_preview.matchup = preview
                    self.user_league_repo.set(matchup.away.id, league_preview)

                league_preview = self.user_league_repo.get(matchup.home.id, command.league_id)
                league_preview.matchup = preview
                self.user_league_repo.set(matchup.home.id, league_preview)

            return CalculatePlayoffsResult(command=command)

        transaction = self.league_repo.firestore.create_transaction()
        return calculate(transaction)


def create_calculate_playoffs_command_executor(
    league_repo: LeagueRepository = Depends(create_league_repository),
    league_config_repo: LeagueConfigRepository = Depends(create_league_config_repository),
    league_roster_repo: LeagueRosterRepository = Depends(create_league_roster_repository),
    matchup_repo: LeagueWeekMatchupRepository = Depends(create_league_week_matchup_repository),
    user_league_repo: UserLeagueRepository = Depends(create_user_league_repository),
    public_repo: PublicRepository = Depends(create_public_repository),
):
    return CalculatePlayoffsCommandExecutor(league_repo, league_config_repo, league_roster_repo, matchup_repo, user_league_repo, public_repo)
