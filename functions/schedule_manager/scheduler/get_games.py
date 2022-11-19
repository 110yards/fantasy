from typing import List

import requests

from .schedule import Game

CFL_API = "https://api.cfl.ca/v1"


def get_all_games(key: str, year: int) -> List[Game]:
    path_no_key = f"{CFL_API}/games/{year}?page[size]=100"
    url = f"{path_no_key}&key={key}"

    resp = requests.get(url)

    if resp.status_code != 200:
        raise Exception(f"request to {path_no_key} returned status code {resp.status_code}")

    data = resp.json()["data"]

    return [Game(**x) for x in data]
