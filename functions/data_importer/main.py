
from datetime import datetime, timedelta
import json
from os import environ

import functions_framework
import pytz
from cflpy import CflPy
from firebase_admin import db

from .firebase import initialize_firebase
from .hash_dict import hash_dict
from .proxy_callback import proxy_callback

GAMES_PATH = f"games/{datetime.now().year}/game"
API_KEY = environ.get("CFL_API_KEY", None)
GCLOUD_PROJECT = environ.get("GCLOUD_PROJECT", None)
RTDB_EMULATOR_HOST = environ.get("RTDB_EMULATOR_HOST", None)

assert API_KEY, "CFL_API_KEY not set"
assert GCLOUD_PROJECT, "GCLOUD_PROJECT not set"

CflPy.setup(api_key=API_KEY, logging_callback=proxy_callback)
initialize_firebase(
    rtdb_emulator_host=RTDB_EMULATOR_HOST,
    project_id=GCLOUD_PROJECT,
)


@functions_framework.cloud_event
def data_importer(event: dict):
    """
    Fetches the most recent game data from the CFL and publishes any games which have changed since last import
    """
    season = datetime.utcnow().year
    # only go 2 days back, since that's all the time we allow for stat corrections anyway
    # CFL's date filter does't work, at least not for greater than, so we have to filter manually.
    date_start = datetime.utcnow().replace(tzinfo=pytz.utc)
    date_start = date_start.astimezone(pytz.timezone("America/Toronto"))
    date_end = datetime.utcnow().replace(tzinfo=pytz.utc)

    date_start = date_start - timedelta(days=2)
    date_end = date_end + timedelta(days=1)

    # filter = GamesFilter(field="date_start", operator="gt", value=date_start.isoformat())

    games = CflPy.v1().games(season).get(page_size=100)

    for game in [g for g in games if date_start < g.date_start < date_end]:
        game = CflPy.v1().games(season).game(game.game_id).with_boxscore().with_rosters().get()

        new_hash = hash_dict(game.json())

        game_ref = db.reference(f"{GAMES_PATH}/{game.game_id}")
        existing_game = game_ref.get()

        existing_hash = getattr(existing_game, "hash", None)

        if new_hash != existing_hash:
            game.__dict__["hash"] = new_hash

            if existing_game:
                print(f"Updating game '{game.game_id}'")
                # did we get rosters?
                existing_team_1_roster = existing_game["rosters"]["teams"]["team_1"]["roster"]

                if len(existing_team_1_roster) == 0 and len(game.rosters.teams.team_1.roster) > 0:
                    print("Rosters have been added")
            else:
                print(f"Inserting game '{game.game_id}'")
                # no need to check the inner values, if it's brand new it's long before any roster is inside.

            # use Pydantic to serialize, then convert back to a clean dictionary for firebase
            doc = json.loads(game.json())
            game_ref.set(doc)
