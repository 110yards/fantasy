import requests

from app.config.settings import Settings

LIVE_TOKEN_URL = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword"



def login(email, password, settings: Settings):

    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True,
    }

    # payload = json.dumps(payload)
    if settings.is_dev():
        url = f"http://{settings.firebase_auth_emulator_host}/identitytoolkit.googleapis.com/v1/accounts:signInWithPassword"
    else:
        url = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword"
        
    headers = {
        "Content-Type": "application/json"
    }
    response = requests.post(url, headers=headers, params={"key": settings.firebase_api_key}, json=payload)

    return response.json()

