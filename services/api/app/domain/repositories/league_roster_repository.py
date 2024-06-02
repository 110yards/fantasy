from services.api.app.domain.repositories.league_repository import LeagueRepository
from google.cloud.firestore_v1.transaction import Transaction
from typing import Dict, List
from yards_py.core.firestore_proxy import FirestoreProxy
from yards_py.domain.entities.roster import Roster
from typing import Dict


def create_league_roster_repository():
    def patch_abbreviation(obj: Dict) -> Roster:
        # Create a copy of the dictionary keys
        keys = list(obj.keys())
        
        # Iterate over the copied keys
        for key in keys:
            if key == "abbreviation":
                obj["abbr"] = obj.pop(key)
            elif isinstance(obj[key], dict):
                obj[key] = patch_abbreviation(obj[key])

        return obj

    
    def parse(obj: Dict):
        obj = patch_abbreviation(obj)
        return Roster(**obj)

        

    firestore = FirestoreProxy[Roster](parse)
    return LeagueRosterRepository(firestore)


class LeagueRosterRepository:

    def __init__(self, firestore: FirestoreProxy[Roster]):
        self.firestore = firestore

    @staticmethod
    def path(league_id):
        return f"{LeagueRepository.path}/{league_id}/roster"

    def get_all(self, league_id, transaction: Transaction = None) -> List[Roster]:
        return self.firestore.get_all(LeagueRosterRepository.path(league_id), transaction)

    def set(self, league_id, roster: Roster, transaction: Transaction = None) -> Roster:
        return self.firestore.set(LeagueRosterRepository.path(league_id), roster, transaction)

    def update(self, league_id, roster: Roster, transaction: Transaction = None) -> Roster:
        return self.firestore.update(LeagueRosterRepository.path(league_id), roster, transaction)

    def get(self, league_id, user_id, transaction: Transaction = None) -> Roster:
        return self.firestore.get(LeagueRosterRepository.path(league_id), user_id, transaction)

    def delete(self, league_id, user_id, transaction: Transaction = None):
        self.firestore.delete(LeagueRosterRepository.path(league_id), user_id, transaction)

    def partial_update(self, league_id: str, roster_id: str, updates: Dict, transaction: Transaction = None):
        self.firestore.partial_update(LeagueRosterRepository.path(league_id), roster_id, updates, transaction)
