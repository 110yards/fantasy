from fastapi.param_functions import Depends

from .core_proxy import CoreProxy, create_core_proxy

class CoreScoreboardProxy():
    def __init__(self, proxy: CoreProxy):
        self.proxy = proxy

    def get_scoreboard(self, season: int, week: int) -> dict:
        return self.proxy.get(f"scoreboard?year={season}&week={week}")



def create_core_scoreboard_proxy(proxy: CoreProxy = Depends(create_core_proxy)):
    return CoreScoreboardProxy(proxy)
