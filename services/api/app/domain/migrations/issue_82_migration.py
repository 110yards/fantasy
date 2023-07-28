from fastapi.param_functions import Depends
from firebase_admin.firestore import firestore

from app.core.logging import Logger
from app.domain.enums.draft_state import DraftState
from app.domain.repositories.league_repository import LeagueRepository, create_league_repository
from app.domain.repositories.league_roster_repository import LeagueRosterRepository, create_league_roster_repository


def create_issue_82_migration(
    league_repo=Depends(create_league_repository),
    league_roster_repo=Depends(create_league_roster_repository),
):
    return Issue82Migration(league_repo, league_roster_repo)


class Issue82Migration:
    """Fixes the stuck roster scores https://github.com/mdryden/110yards-api/issues/82"""

    def __init__(
        self,
        league_repo: LeagueRepository,
        league_roster_repo: LeagueRosterRepository,
    ):
        self.league_repo = league_repo
        self.league_roster_repo = league_roster_repo

    def run(self, league_id) -> str:
        if league_id:
            leagues = [self.league_repo.get(league_id)]
        else:
            leagues = self.league_repo.get_all()

        league_count = 0

        for league in leagues:
            if league.draft_state == DraftState.NOT_STARTED:
                continue

            @firestore.transactional
            def apply_fix(transaction):
                Logger.info(f"Processing league {league.id}")
                rosters = self.league_roster_repo.get_all(league.id, transaction)

                for roster in rosters:
                    roster.this_week_points_for = 0
                    roster.this_week_bench_points_for = 0

                    for position in roster.positions.values():
                        position.game_score = 0

                    self.league_roster_repo.set(league.id, roster, transaction)

            transaction = self.league_repo.firestore.create_transaction()
            apply_fix(transaction)
            league_count += 1

        result = f"Fixed Issue #82 for {league_count} leagues."

        return result
