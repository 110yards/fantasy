# from yards_py.domain.entities.league_week import LeagueWeek
# from yards_py.domain.repositories.league_repository import LeagueRepository
# from google.cloud.firestore_v1.transaction import Transaction
# from yards_py.core.firestore_proxy import FirestoreProxy


# def create_league_week_repository():
#     firestore = FirestoreProxy[LeagueWeek](LeagueWeek.parse_obj)
#     return LeagueWeekRepository(firestore)


# class LeagueWeekRepository:
#     def __init__(self, firestore: FirestoreProxy[LeagueWeek]):
#         self.firestore = firestore

#     @staticmethod
#     def path(league_id):
#         return f"{LeagueRepository.path}/{league_id}/week"

#     def get(self, league_id, week_id: str, transaction: Transaction = None) -> LeagueWeek:
#         return self.firestore.get(LeagueWeekRepository.path(league_id), week_id, transaction)

#     def set(self, league_id, week: LeagueWeek, transaction: Transaction = None) -> LeagueWeek:
#         return self.firestore.set(LeagueWeekRepository.path(league_id), week, transaction)
