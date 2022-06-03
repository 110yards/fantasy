
from services.system.app.config.settings import Settings, get_settings
from fastapi.params import Depends
from yards_py.domain import topics
from yards_py.core.publisher import Publisher, SubscriptionConfig
from services.system.app.di import create_publisher


def create_configure_events(settings: Settings = Depends(get_settings), publisher: Publisher = Depends(create_publisher)):

    return ConfigureEvents(settings.endpoint, settings.api_key, publisher)


class ConfigureEvents:
    def __init__(self, endpoint: str, api_key: str, publisher: Publisher):
        self.endpoint = endpoint
        self.api_key = api_key
        self.publisher = publisher

    def configure_events(self) -> bool:
        # TOPICS
        for topic in topics.ALL_TOPICS:
            self.publisher.create_topic(topic)

        # SUBSCRIPTIONS
        config = SubscriptionConfig(expiration_days=None)
        create_league_subscriptions = f"{self.endpoint}/league/subscriptions?key={self.api_key}"
        self.publisher.create_push_subscription("push_create_league_subscriptions", topics.LEAGUE_CREATED_TOPIC, create_league_subscriptions, config)
        self.publisher.create_push_subscription("push_renew_league_subscriptions", topics.LEAGUE_RENEWED_TOPIC, create_league_subscriptions, config)

        long_ack_config = SubscriptionConfig(expiration_days=None, ack_deadline=600)
        update_games = f"{self.endpoint}/system/games?key={self.api_key}"
        self.publisher.create_push_subscription("push_system_update_games", topics.UPDATE_GAMES_TOPIC, update_games, long_ack_config)

        update_players = f"{self.endpoint}/system/players?key={self.api_key}"
        self.publisher.create_push_subscription("push_system_update_players", topics.UPDATE_PLAYERS_TOPIC, update_players, long_ack_config)

        end_of_day = f"{self.endpoint}/system/end_of_day?key={self.api_key}"
        self.publisher.create_push_subscription("push_system_end_of_day", topics.END_OF_DAY_TOPIC, end_of_day, config)

        end_of_week = f"{self.endpoint}/system/end_of_week?key={self.api_key}"
        self.publisher.create_push_subscription("push_system_end_of_week", topics.END_OF_WEEK_TOPIC, end_of_week, config)

        # maybe create jobs here too?

        return True
