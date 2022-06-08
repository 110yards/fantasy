
from fastapi.param_functions import Depends
from services.api.app.domain.enums.draft_state import DraftState
from services.api.app.domain.repositories.league_repository import LeagueRepository, create_league_repository
from services.api.app.domain.repositories.league_config_repository import LeagueConfigRepository, create_league_config_repository


def create_issue_121_migration(
    league_repo=Depends(create_league_repository),
    league_config_repo=Depends(create_league_config_repository),
):
    return Issue121Migration(league_repo, league_config_repo)


class Issue121Migration:
    def __init__(self, league_repo: LeagueRepository, league_config_repo: LeagueConfigRepository):
        self.league_repo = league_repo
        self.league_config_repo = league_config_repo

    def run(self, commit: bool) -> str:
        leagues = self.league_repo.get_all()

        fixes = []
        # For each league:
        for league in leagues:
            if league.draft_state == DraftState.NOT_STARTED:  # Config might not be done, don't bother
                continue

            config = self.league_config_repo.get_schedule_config(league.id)

            requires_fix = False
            index = 0

            for week in config.weeks:
                expected_week_number = index + 1
                week_number_correct = week.week_number == expected_week_number
                if not week_number_correct:
                    requires_fix = True
                    fixes.append(f"League {league.id}: {week.week_number} should be {expected_week_number}")
                    week.week_number = expected_week_number
                    week.week_id = f"{expected_week_number:02}"
                index += 1

            if requires_fix and commit:
                self.league_config_repo.set_schedule_config(league.id, config)

        if not fixes:
            return "No issues found"
        else:
            return fixes
