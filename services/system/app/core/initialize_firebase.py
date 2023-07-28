from typing import Optional

import firebase_admin
from firebase_admin import App, credentials
from strivelogger import StriveLogger


def initialize_firebase(rtdb_emulator_host: Optional[int], project_id: str) -> App:
    database_url = realtime_db_url(rtdb_emulator_host, project_id)
    StriveLogger.info(f"Initializing Firebase with database URL: {database_url}")

    return firebase_admin.initialize_app(
        credential=credentials.ApplicationDefault(),
        options={
            "projectId": project_id,
            "databaseURL": database_url,
        },
    )


def realtime_db_url(rtdb_emulator_host: Optional[int], project_id: str) -> str:
    if rtdb_emulator_host:
        return f"http://{rtdb_emulator_host}/?ns={project_id}"
    else:
        return f"https://{project_id}.firebaseio.com"
