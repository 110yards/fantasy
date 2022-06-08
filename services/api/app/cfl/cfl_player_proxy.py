from fastapi.param_functions import Depends

from .cfl_proxy import CflProxy, create_cfl_proxy


def create_cfl_player_proxy(proxy: CflProxy = Depends(create_cfl_proxy)):
    return CflPlayerProxy(proxy)


class CflPlayerProxy():
    def __init__(self, proxy: CflProxy):
        self.proxy = proxy

    def get_players_for_season(self, season: int, page_number: int, page_size: int) -> dict:
        return self.proxy.get(f"players?filter[season][eq]={season}&include=current_team&page[number]={page_number}&page[size]={page_size}")

    def get_players_by_last_name(self, last_name: str, page_number: int, page_size: int) -> dict:
        args = "players?" + \
            f"&page[number]={page_number}" + \
            f"&page[size]={page_size}" + \
            f"&filter[last_name][eq]={last_name}"

        return self.proxy.get(args)
