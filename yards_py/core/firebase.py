import requests

LIVE_TOKEN_URL = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword"
LOCAL_TOKEN_URL = "http://localhost:9099/identitytoolkit.googleapis.com/v1/accounts:signInWithPassword"


def login(email, password, firebase_api_key: str, is_dev: bool):

    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True,
    }

    # payload = json.dumps(payload)

    url = LOCAL_TOKEN_URL if is_dev else LIVE_TOKEN_URL

    headers = {
        "Content-Type": "application/json"
    }
    response = requests.post(url, headers=headers, params={"key": firebase_api_key}, json=payload)

    return response.json()
