import hashlib
import json

from pydantic import BaseModel

from app.domain.models.game import Game


class Schedule(BaseModel):
    year: int
    games: dict[str, Game]

    def hash(self) -> str:
        return hashlib.md5(json.dumps(self.json()).encode("utf-8")).hexdigest()
