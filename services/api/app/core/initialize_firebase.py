from typing import Optional

import firebase_admin
from firebase_admin import App, credentials


def initialize_firebase(rtdb_emulator_host: Optional[int], project_id: str) -> App:
    return firebase_admin.initialize_app(
        credential=credentials.ApplicationDefault(),
        options={
            "projectId": project_id,
            "databaseURL": realtime_db_url(rtdb_emulator_host, project_id),
        },
    )


def realtime_db_url(rtdb_emulator_host: Optional[int], project_id: str) -> str:
    if rtdb_emulator_host:
        return f"http://{rtdb_emulator_host}/?ns={project_id}"
    else:
        return f"https://{project_id}.firebaseio.com"
