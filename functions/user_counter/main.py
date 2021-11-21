from typing import Dict
from firebase_admin import firestore
import firebase_admin
from google.cloud.firestore import Client
from google.cloud.firestore_v1 import Increment

firebase_admin.initialize_app()
client = firestore.client()  # type: Client


def update_user_count(event: Dict, context):
    old_value: Dict = event.get("oldValue", None)
    new_value: Dict = event.get("value", None)

    if not old_value or not new_value:
        return

    old_event_data: Dict = old_value["fields"]["event_data"]["mapValue"]["fields"]
    new_event_data: Dict = new_value["fields"]["event_data"]["mapValue"]["fields"]

    old_email_verified: Dict = old_event_data.get("emailVerified", {})
    new_email_verified: Dict = new_event_data.get("emailVerified", None)

    if not new_email_verified:
        return

    was_verified_before = old_email_verified.get("booleanValue", False) if old_email_verified else False
    is_verified_now = new_email_verified.get("booleanValue", False) if new_email_verified else False

    just_verified = not was_verified_before and is_verified_now

    if just_verified:
        count_ref = client.document("admin/stats")
        count_ref.update({"verified_user_count": Increment(1)})
