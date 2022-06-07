
from api.app.domain.repositories.league_config_repository import LeagueConfigRepository, create_league_config_repository
from yards_py.core.logging import Logger
from fastapi.param_functions import Depends
from api.app.domain.repositories.league_repository import LeagueRepository, create_league_repository
from firebase_admin.firestore import firestore


def create_issue_84_migration(
    league_repo=Depends(create_league_repository),
    league_config_repo=Depends(create_league_config_repository),
):
    return Issue84Migration(league_repo, league_config_repo)


class Issue84Migration:
    '''Fixes bad scoring configs https://github.com/mdryden/110yards-api/issues/84'''

    def __init__(
        self,
        league_repo: LeagueRepository,
        league_config_repo: LeagueConfigRepository,
    ):
        self.league_repo = league_repo
        self.league_config_repo = league_config_repo

    def run(self, league_id) -> str:

        if league_id:
            leagues = [self.league_repo.get(league_id)]
        else:
            leagues = self.league_repo.get_all()

        league_count = 0

        for league in leagues:

            @firestore.transactional
            def apply_fix(transaction):
                Logger.info(f"Processing league {league.id}")
                config = self.league_config_repo.get_scoring_config(league.id, transaction)

                if config.field_goal_returns_yards != config.kick_returns_yards:
                    config.field_goal_returns_yards = config.kick_returns_yards
                    self.league_config_repo.set_scoring_config(league.id, config, transaction)
                    return 1
                else:
                    return 0

            transaction = self.league_repo.firestore.create_transaction()
            league_count += apply_fix(transaction)

        result = f"Fixed Issue #84 for {league_count} leagues."

        return result
