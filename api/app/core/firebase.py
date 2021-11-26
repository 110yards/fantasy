import requests
from api.app.config.settings import Settings

LIVE_TOKEN_URL = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword"
LOCAL_TOKEN_URL = "http://localhost:9099/identitytoolkit.googleapis.com/v1/accounts:signInWithPassword"


def login(email, password, settings: Settings):
    key = settings.firebase_api_key

    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True,
    }

    # payload = json.dumps(payload)

    url = LOCAL_TOKEN_URL if settings.is_dev else LIVE_TOKEN_URL

    headers = {
        "Content-Type": "application/json"
    }
    response = requests.post(url, headers=headers, params={"key": key}, json=payload)

    return response.json()
