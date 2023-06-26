

from fastapi.param_functions import Depends
from app.yards_py.domain.entities.scoring_settings import ScoringSettings
from app.domain.repositories.league_repository import LeagueRepository, create_league_repository
from app.domain.repositories.league_config_repository import LeagueConfigRepository, create_league_config_repository
from firebase_admin.firestore import firestore


def create_issue_46_migration(
    league_repo=Depends(create_league_repository),
    league_config_repo=Depends(create_league_config_repository),
):
    return Issue46Migration(league_repo, league_config_repo)


class Issue46Migration:
    '''Fixes a problem with the original default scoring config

    This resets the default scoring config for all affected leagues.
    '''

    def __init__(self, league_repo: LeagueRepository, league_config_repo: LeagueConfigRepository):
        self.league_repo = league_repo
        self.league_config_repo = league_config_repo

    def run(self) -> str:
        leagues = self.league_repo.get_all()

        fixed_count = 0

        for league in leagues:
            if league.issue_46_fixed:
                continue

            @firestore.transactional
            def apply_fix(transaction):
                league.issue_46_fixed = True
                self.league_config_repo.set_scoring_config(league.id, ScoringSettings.create_default(), transaction)
                self.league_repo.update(league, transaction)

            transaction = self.league_repo.firestore.create_transaction()
            apply_fix(transaction)
            fixed_count += 1

        return f"Fixed Issue #46 for {fixed_count} leagues"
