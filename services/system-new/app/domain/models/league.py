from pydantic import BaseModel


class League(BaseModel):
    name: str
    draft_state: str
    season: int

    @property
    def is_active(self) -> bool:
        return self.draft_state == "completed"

    def is_active_for_season(self, season: int) -> bool:
        return self.is_active and self.season == season
