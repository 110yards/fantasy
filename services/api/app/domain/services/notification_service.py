from fastapi.param_functions import Depends
from app.yards_py.domain.entities.league import League
from app.domain.repositories.league_config_repository import LeagueConfigRepository, create_league_config_repository
from app.domain.services.discord_service import DiscordService, create_discord_service


def create_notification_service(
    config_repo: LeagueConfigRepository = Depends(create_league_config_repository),
    discord_service: DiscordService = Depends(create_discord_service),
):
    return NotificationService(
        config_repo=config_repo,
        discord_service=discord_service,
    )


class NotificationService:
    def __init__(
        self,
        config_repo: LeagueConfigRepository,
        discord_service: DiscordService,
    ):
        self.config_repo = config_repo
        self.discord_service = discord_service

    def __send_discord_message(self, league: League, message: str):
        private_config = self.config_repo.get_private_config(league.id)
        self.discord_service.send_message(private_config.discord_webhook_url, message)

    def send_draft_event(self, league: League, message: str):
        if league.enable_discord_notifications and league.notifications_draft:
            self.__send_discord_message(league, message)

    def send_transaction_event(self, league: League, message: str):
        if league.enable_discord_notifications and league.notifications_transactions:
            self.__send_discord_message(league, message)

    def send_waiver_results(self, league: League, message: str):

        if league.enable_discord_notifications and league.notifications_waivers:
            self.__send_discord_message(league, message)

    def send_weekly_summary(self, league: League, message: str):
        if league.enable_discord_notifications and league.notifications_end_of_week:
            self.__send_discord_message(league, message)
