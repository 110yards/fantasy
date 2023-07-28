from pydantic import BaseModel, validator
from typing import Optional
from random import randint


class SimState(BaseModel):
    game_id: Optional[int]
    quarter: Optional[int]

    @validator("quarter", pre=True, always=True)
    def validate_quarter(cls, v):
        if v and (v > 3 or v < 1):
            v = None

        return v

    def __is_pre_game(self, game: dict) -> bool:
        return self.game_id and game["game_id"] > self.game_id

    def __is_mid_game(self, game: dict) -> bool:
        return self.game_id and game["game_id"] == self.game_id and self.quarter

    def __adjust_score(self, team: dict):
        line_scores = [x["score"] for x in team["linescores"] if x["quarter"] <= self.quarter]
        team["score"] = sum(line_scores)

    def apply_to_score(self, game: dict):
        if self.__is_pre_game(game):
            game["team_1"]["score"] = 0
            game["team_2"]["score"] = 0
            game["event_status"]["is_active"] = False
            game["event_status"]["event_status_id"] = 1
            game["event_status"]["quarter"] = 0

        if self.__is_mid_game(game):
            self.__adjust_score(game["team_1"])
            self.__adjust_score(game["team_2"])
            game["event_status"]["is_active"] = True
            game["event_status"]["event_status_id"] = 2
            game["event_status"]["quarter"] = self.quarter
            game["event_status"]["minutes"] = randint(1, 14)
            game["event_status"]["seconds"] = randint(0, 59)

    def apply_to_stats(self, game: dict):
        if self.__is_pre_game(game):
            factor = 0
        elif self.__is_mid_game(game):
            factor = self.quarter / 4.0
        else:
            return

        for player in game["player_stats"].values():
            for key, value in player["stats"].items():
                if type(value) == int:
                    player["stats"][key] = int(value * factor)
