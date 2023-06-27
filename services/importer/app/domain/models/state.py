from pydantic import BaseModel


class State(BaseModel):
    current_season: int
    current_week: int
    is_offseason: bool
