# import json
# import requests

# verification_url = "https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode"


# def send_verification_email(id_token, firebase_api_key):

#     payload = json.dumps({
#         "email": email,
#         "password": password,
#         "returnSecureToken": True
#     })

#     res = requests.post(verification_url, params={"key": firebase_api_key}, data=payload)

#     return res.json()
