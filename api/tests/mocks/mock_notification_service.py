from api.app.domain.entities.league import League


class MockNotificationService:

    def send_draft_event(self, league: League, message: str):
        pass

    def send_transaction_event(self, league: League, message: str):
        pass

    def send_waiver_results(self, league: League, message: str):
        pass

    def send_weekly_summary(self, league: League, message: str):
        pass
