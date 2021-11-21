from fastapi.param_functions import Depends

from .cfl_proxy import CflProxy, create_cfl_proxy


def create_cfl_game_proxy(proxy: CflProxy = Depends(create_cfl_proxy)):
    return CflGameProxy(proxy)


class CflGameProxy():
    def __init__(self, proxy: CflProxy):
        self.proxy = proxy

    def get_game_summaries_for_season(self, season: int) -> dict:
        return self.proxy.get(f"games/{season}")

    def get_game_summaries_for_week(self, season: int, week: int) -> dict:
        return self.proxy.get(f"games/{season}?filter[week][eq]={week}")

    def get_game(self, season: int, game_id: int) -> dict:
        return self.proxy.get(f"games/{season}/game/{game_id}?include=rosters,boxscore")
