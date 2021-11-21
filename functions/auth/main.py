from typing import Dict, List
from firebase_admin import firestore
import firebase_admin
from google.cloud.firestore import Client
from google.cloud.firestore_v1.transforms import Increment

firebase_admin.initialize_app()
client = firestore.client()  # type: Client


def auth_on_user_create(event: Dict, context):
    id = event.get("uid")
    login_type = "email"

    provider_data = event.get("providerData", None)  # type: List
    if provider_data and len(provider_data) > 0:
        provider_data = provider_data[0]  # type: Dict
        login_type = provider_data.get("providerId", None)

    profile = {
        "id": id,
        "display_name": event.get("displayName", "Anonymous"),
        "email": event.get("email", None),
        "login_type": login_type,
        "event_data": event
    }

    ref = client.document(f"user/{id}")
    ref.set(profile)

    is_verified = event.get("emailVerified", False)

    if is_verified:
        count_ref = client.document("admin/stats")
        count_ref.update({"verified_user_count": Increment(1)})
