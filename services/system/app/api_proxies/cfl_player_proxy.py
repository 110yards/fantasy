from typing import Optional
from fastapi.param_functions import Depends

from .cfl_proxy import CflProxy, create_cfl_proxy


def create_cfl_player_proxy(proxy: CflProxy = Depends(create_cfl_proxy)):
    return CflPlayerProxy(proxy)


class CflPlayerProxy():
    def __init__(self, proxy: CflProxy):
        self.proxy = proxy

    def get_players_for_season(self, season: int | None = None, include_season_stats: bool | None = None) -> dict:
        return self.proxy.get(f"players?year={season}&include_season_stats={include_season_stats}")

    def get_player(self, player_id: int) -> dict:
        return self.proxy.get(f"players/{player_id}")

    def get_players_by_last_name(self, last_name: str, page_number: int, page_size: int) -> dict:
        args = "players?" + \
            f"&page[number]={page_number}" + \
            f"&page[size]={page_size}" + \
            f"&filter[last_name][eq]={last_name}"

        return self.proxy.get(args)
