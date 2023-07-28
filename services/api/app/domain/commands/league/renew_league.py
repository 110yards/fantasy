from datetime import datetime
from typing import Optional

from fastapi.param_functions import Depends

from app.core.annotate_args import annotate_args
from app.core.base_command_executor import BaseCommand, BaseCommandExecutor, BaseCommandResult
from app.core.publisher import Publisher
from app.di import create_publisher
from app.domain.entities.league import DraftState, League
from app.domain.entities.league_transaction import LeagueTransaction
from app.domain.entities.user_league_preview import UserLeaguePreview
from app.domain.repositories.league_config_repository import LeagueConfigRepository, create_league_config_repository
from app.domain.repositories.league_owned_player_repository import LeagueOwnedPlayerRepository, create_league_owned_player_repository
from app.domain.repositories.league_repository import LeagueRepository, create_league_repository
from app.domain.repositories.league_roster_repository import LeagueRosterRepository, create_league_roster_repository
from app.domain.repositories.league_transaction_repository import LeagueTransactionRepository, create_league_transaction_repository
from app.domain.repositories.league_week_matchup_repository import LeagueWeekMatchupRepository, create_league_week_matchup_repository
from app.domain.repositories.league_week_repository import LeagueWeekRepository, create_league_week_repository
from app.domain.repositories.player_league_season_score_repository import PlayerLeagueSeasonScoreRepository, create_player_league_season_score_repository
from app.domain.repositories.public_repository import PublicRepository, create_public_repository
from app.domain.repositories.user_archive_league_repository import UserArchiveLeagueRepository, create_user_archive_league_repository
from app.domain.repositories.user_league_repository import UserLeagueRepository, create_user_league_repository
from app.domain.repositories.user_repository import UserRepository, create_user_repository
from app.domain.topics import LEAGUE_RENEWED_TOPIC


def create_renew_league_command_executor(
    league_repo: LeagueRepository = Depends(create_league_repository),
    user_league_repo: UserLeagueRepository = Depends(create_user_league_repository),
    league_roster_repo: LeagueRosterRepository = Depends(create_league_roster_repository),
    league_config_repo: LeagueConfigRepository = Depends(create_league_config_repository),
    public_repo: PublicRepository = Depends(create_public_repository),
    league_week_repo: LeagueWeekRepository = Depends(create_league_week_repository),
    archive_league_repo: UserArchiveLeagueRepository = Depends(create_user_archive_league_repository),
    owned_player_repo: LeagueOwnedPlayerRepository = Depends(create_league_owned_player_repository),
    player_score_repo: PlayerLeagueSeasonScoreRepository = Depends(create_player_league_season_score_repository),
    transaction_repo: LeagueTransactionRepository = Depends(create_league_transaction_repository),
    publisher: Publisher = Depends(create_publisher),
    matchup_repo: LeagueWeekMatchupRepository = Depends(create_league_week_matchup_repository),
    user_repo: UserRepository = Depends(create_user_repository),
):
    return RenewLeagueCommandExecutor(
        archive_league_repo=archive_league_repo,
        league_config_repo=league_config_repo,
        league_repo=league_repo,
        league_roster_repo=league_roster_repo,
        league_week_repo=league_week_repo,
        owned_player_repo=owned_player_repo,
        player_score_repo=player_score_repo,
        transaction_repo=transaction_repo,
        user_league_repo=user_league_repo,
        public_repo=public_repo,
        publisher=publisher,
        matchup_repo=matchup_repo,
        user_repo=user_repo,
    )


@annotate_args
class RenewLeagueCommand(BaseCommand):
    league_id: str


@annotate_args
class RenewLeagueResult(BaseCommandResult):
    league: Optional[League]


class RenewLeagueCommandExecutor(BaseCommandExecutor[RenewLeagueCommand, RenewLeagueResult]):
    def __init__(
        self,
        league_repo: LeagueRepository,
        user_league_repo: UserLeagueRepository,
        league_roster_repo: LeagueRosterRepository,
        league_config_repo: LeagueConfigRepository,
        public_repo: PublicRepository,
        owned_player_repo: LeagueOwnedPlayerRepository,
        player_score_repo: PlayerLeagueSeasonScoreRepository,
        transaction_repo: LeagueTransactionRepository,
        league_week_repo: LeagueWeekRepository,
        archive_league_repo: UserArchiveLeagueRepository,
        publisher: Publisher,
        matchup_repo: LeagueWeekMatchupRepository,
        user_repo: UserRepository,
    ):
        self.league_repo = league_repo
        self.user_league_repo = user_league_repo
        self.league_roster_repo = league_roster_repo
        self.league_config_repo = league_config_repo
        self.public_repo = public_repo
        self.owned_player_repo = owned_player_repo
        self.player_score_repo = player_score_repo
        self.transaction_repo = transaction_repo
        self.league_week_repo = league_week_repo
        self.archive_league_repo = archive_league_repo
        self.publisher = publisher
        self.matchup_repo = matchup_repo
        self.user_repo = user_repo

    def on_execute(self, command: RenewLeagueCommand) -> RenewLeagueResult:
        league = self.league_repo.get(command.league_id)

        if not league:
            return RenewLeagueResult(command=command, error="League not found")

        if not league.commissioner_id == command.request_user_id:
            user = self.user_repo.get(command.request_user_id)
            if not user.is_admin:
                return RenewLeagueResult(command=command, error="You are not the commissioner or admin")

        state = self.public_repo.get_state()

        league.season = state.current_season
        league.has_completed_season = True
        league.draft_state = DraftState.NOT_STARTED
        league.first_playoff_week = None
        league.renewed = datetime.now()
        league.schedule_generated = False
        league.is_complete = False

        schedule = self.league_config_repo.get_schedule_config(league.id)
        schedule.reset()
        self.league_config_repo.set_schedule_config(league.id, schedule)

        self.owned_player_repo.delete_all(league.id)
        self.transaction_repo.delete_all(league.id)
        self.league_week_repo.delete_all(league.id)
        self.matchup_repo.delete_all(league.id)
        self.player_score_repo.delete_all(league.id)

        for roster in self.league_roster_repo.get_all(league.id):
            roster.reset()
            self.league_roster_repo.set(league.id, roster)
            preview = UserLeaguePreview.create(roster, league)
            self.user_league_repo.set(roster.id, preview)

        trx = LeagueTransaction.league_event(league.id, f"🏈 The commissioner renewed the league for {state.current_season} 🏈")
        self.transaction_repo.create(league.id, trx)

        # save the league and remove the archive link last, in a transaction, in case something goes wrong.  Then the user can try again.
        self.league_repo.update(league)
        self.archive_league_repo.delete(league.commissioner_id, league.id)

        self.publisher.publish(league, LEAGUE_RENEWED_TOPIC)

        return RenewLeagueResult(command=command, league=league)
