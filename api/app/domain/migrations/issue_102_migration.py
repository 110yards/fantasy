
from api.app.domain.repositories.league_config_repository import LeagueConfigRepository, create_league_config_repository
from api.app.core.logging import Logger
from fastapi.param_functions import Depends
from api.app.domain.repositories.league_repository import LeagueRepository, create_league_repository
from firebase_admin.firestore import firestore


def create_issue_102_migration(
    league_repo=Depends(create_league_repository),
    league_config_repo=Depends(create_league_config_repository),
):
    return Issue102Migration(league_repo, league_config_repo)


class Issue102Migration:
    '''Fixes large schedule configs https://github.com/mdryden/110yards-api/issues/102'''

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
                schedule = self.league_config_repo.get_schedule_config(league.id, transaction)

                save_required = False
                for week in schedule.weeks:
                    for matchup in week.matchups:
                        if matchup.away and matchup.away.waiver_bids:
                            matchup.away.waiver_bids = []
                            save_required = True
                        if matchup.away and matchup.away.processed_waiver_bids:
                            matchup.away.processed_waiver_bids = []
                            save_required = True

                        if matchup.home and matchup.home.waiver_bids:
                            matchup.home.waiver_bids = []
                            save_required = True
                        if matchup.home and matchup.home.processed_waiver_bids:
                            matchup.home.processed_waiver_bids = []
                            save_required = True

                if save_required:
                    self.league_config_repo.set_schedule_config(league.id, schedule, transaction)

                return save_required

            transaction = self.league_repo.firestore.create_transaction()
            was_saved = apply_fix(transaction)
            if was_saved:
                league_count += 1

        result = f"Fixed Issue #84 for {league_count} leagues."

        return result
