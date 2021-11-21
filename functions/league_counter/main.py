from typing import Dict
from firebase_admin import firestore
import firebase_admin
from google.cloud.firestore import Client
from google.cloud.firestore_v1 import Increment

firebase_admin.initialize_app()
client: Client = firestore.client()


def update_league_count(event: Dict, context):
    count_ref = client.collection("admin").document("stats")

    count_ref.update({"league_count": Increment(1)})


if __name__ == "__main__":
    update_league_count(None, None)
