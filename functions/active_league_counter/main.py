from typing import Dict
from firebase_admin import firestore
import firebase_admin
from google.cloud.firestore import Client
from google.cloud.firestore_v1 import Increment

firebase_admin.initialize_app()
client = firestore.client()  # type: Client


def update_active_league_count(event: Dict, context):
    old_value: Dict = event.get("oldValue", None)
    new_value: Dict = event.get("value", None)

    if not old_value or not new_value:
        return

    old_value: Dict = old_value["fields"]["draft_state"]["stringValue"]
    new_value: Dict = new_value["fields"]["draft_state"]["stringValue"]

    was_inactive = old_value != "completed"
    is_active = new_value == "completed"

    just_activated = was_inactive and is_active
    # print(f"was_inactive: {was_inactive} is_active: {is_active} just_activated: {just_activated}")

    if just_activated:
        count_ref = client.document("admin/stats")
        count_ref.update({"active_league_count": Increment(1)})
