from fastapi.param_functions import Depends

from .core_proxy import CoreProxy, create_core_proxy


class CoreScheduleProxy():
    def __init__(self, proxy: CoreProxy):
        self.proxy = proxy

    def get_schedule(self, season: int | None = None) -> dict:
        url = "schedule"

        if season:
            url += f"?year={season}"
            
        return self.proxy.get(url)


def create_core_schedule_proxy(proxy: CoreProxy = Depends(create_core_proxy)):
    return CoreScheduleProxy(proxy)
