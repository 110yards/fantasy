from fastapi.param_functions import Depends

from .core_proxy import CoreProxy, create_core_proxy

class CoreGameProxy():
    def __init__(self, proxy: CoreProxy):
        self.proxy = proxy

    def get_schedule(self, season: int) -> dict:
        return self.proxy.get(f"schedule?season={season}")



def create_cfl_game_proxy(proxy: CoreProxy = Depends(create_core_proxy)):
    return CoreGameProxy(proxy)

