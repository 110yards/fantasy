from fastapi import Depends
from google.cloud.firestore_v1.transaction import Transaction

from app.domain.enums.draft_state import DraftState
from app.domain.repositories.league_config_repository import LeagueConfigRepository, create_league_config_repository
from app.domain.repositories.league_repository import LeagueRepository, create_league_repository
from app.domain.repositories.public_repository import PublicRepository, create_public_repository
from app.yards_py.domain.entities.draft import Draft
from app.yards_py.domain.entities.league import League


def create_draft_service(
    league_repo: LeagueRepository = Depends(create_league_repository),
    league_config_repo: LeagueConfigRepository = Depends(create_league_config_repository),
    public_repo: PublicRepository = Depends(create_public_repository),
):
    return DraftService(league_repo, league_config_repo, public_repo)


class DraftService:
    def __init__(self, league_repo: LeagueRepository, league_config_repo: LeagueConfigRepository, public_repo: PublicRepository):
        self.league_repo = league_repo
        self.league_config_repo = league_config_repo
        self.public_repo = public_repo

    def was_last_pick(self, draft: Draft, pick_number: int):
        return len(draft.slots) == pick_number

    def complete(self, draft: Draft, league: League, transaction: Transaction):
        state = self.public_repo.get_state()
        scoreboard = self.public_repo.get_scoreboard()

        start_week = state.current_week

        if scoreboard.any_locks():
            start_week += 1

        league.draft_state = DraftState.COMPLETE
        league.league_start_week = start_week
        self.league_repo.update(league, transaction)
        draft.complete = True
        self.league_config_repo.set_draft(league.id, draft, transaction)
