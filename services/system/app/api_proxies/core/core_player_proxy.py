from fastapi.param_functions import Depends

from .core_proxy import CoreProxy, create_core_proxy


class CorePlayerProxy():
    def __init__(self, proxy: CoreProxy):
        self.proxy = proxy

    def get_players_for_season(self, season: int | None = None, include_season_stats: bool | None = None) -> dict:
        return self.proxy.get(f"players?year={season}&include_season_stats={include_season_stats}")


def create_core_player_proxy(proxy: CoreProxy = Depends(create_core_proxy)):
    return CorePlayerProxy(proxy)
