from pydantic import BaseModel


class InjuryStatus(BaseModel):
    injury: str
    last_updated: str
    status_id: int
    text: str
