from typing import Dict

from fastapi.param_functions import Depends
from firebase_admin.firestore import firestore

from app.core.logging import Logger
from app.domain.entities.matchup_preview import MatchupPreview
from app.domain.entities.schedule import ScheduleWeek
from app.domain.entities.user_league_preview import UserLeaguePreview
from app.domain.enums.draft_state import DraftState
from app.domain.repositories.league_config_repository import LeagueConfigRepository, create_league_config_repository
from app.domain.repositories.league_repository import LeagueRepository, create_league_repository
from app.domain.repositories.league_roster_repository import LeagueRosterRepository, create_league_roster_repository
from app.domain.repositories.state_repository import StateRepository, create_state_repository
from app.domain.repositories.user_league_repository import UserLeagueRepository, create_user_league_repository


def create_issue_58_migration(
    league_repo=Depends(create_league_repository),
    user_league_repo=Depends(create_user_league_repository),
    league_config_repo=Depends(create_league_config_repository),
    league_roster_repo=Depends(create_league_roster_repository),
    state_repo=Depends(create_state_repository),
):
    return Issue58Migration(league_repo, user_league_repo, league_config_repo, league_roster_repo, state_repo)


class Issue58Migration:
    """Fixes the league preview for anyone affected by https://github.com/mdryden/110yards/issues/15"""

    def __init__(
        self,
        league_repo: LeagueRepository,
        user_league_repo: UserLeagueRepository,
        league_config_repo: LeagueConfigRepository,
        league_roster_repo: LeagueRosterRepository,
        state_repo: StateRepository,
    ):
        self.league_repo = league_repo
        self.user_league_repo = user_league_repo
        self.league_config_repo = league_config_repo
        self.league_roster_repo = league_roster_repo
        self.state_repo = state_repo

    def run(self, league_id) -> str:
        if league_id:
            leagues = [self.league_repo.get(league_id)]
        else:
            leagues = self.league_repo.get_all()

        current_week = self.state_repo.get().current_week

        league_count = 0
        failed_leagues = []

        for league in leagues:
            if league.draft_state == DraftState.NOT_STARTED:
                continue

            @firestore.transactional
            def apply_fix(transaction):
                Logger.info(f"Processing league {league.id}")
                rosters = self.league_roster_repo.get_all(league.id, transaction)
                schedule = self.league_config_repo.get_schedule_config(league.id, transaction)

                previews: Dict[str, UserLeaguePreview] = {}
                for roster in rosters:
                    preview = self.user_league_repo.get(roster.id, league.id, transaction)
                    previews[roster.id] = preview

                for roster in rosters:
                    week: ScheduleWeek = next(week for week in schedule.weeks if week.week_number == current_week)
                    matchup = next((m for m in week.matchups if (m.away and m.away.id == roster.id) or (m.home and m.home.id == roster.id)), None)
                    preview = previews[roster.id]

                    if not preview:
                        return False

                    preview.matchup = MatchupPreview.from_matchup(matchup) if matchup else None
                    self.user_league_repo.set(roster.id, preview, transaction)

                return True

            transaction = self.league_repo.firestore.create_transaction()
            fixed = apply_fix(transaction)

            if fixed:
                league_count += 1
            else:
                failed_leagues.append(league.id)

        result = f"Fixed Issue #58 for {league_count} leagues. Failed to apply fix to: "

        result += ", ".join(failed_leagues)

        return result
