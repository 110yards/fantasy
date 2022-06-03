import os
import requests
import sys

from requests.models import Response

endpoint = os.environ.get("ENDPOINT", "http://0.0.0.0:8001")
api_key = os.environ.get("API_KEY", "000000")


def check_response(response: Response, test_name: str):
    print(f"{response.request.method}\t({response.status_code})\t{response.request.url} ")

    if not response.ok:
        print(f"ERROR:\t\tSmoke test failed on {test_name}")
        sys.exit(1)


def configure_api():
    url = f"{endpoint}/system/configure?key={api_key}"
    response = requests.post(url)
    check_response(response, "configure_api")


def api_smoke_test():
    url = f"{endpoint}/system/smoke_test?key={api_key}"
    response = requests.post(url)
    check_response(response, "api_smoke_test")


#############
# Smoke tests
#############
print("Smoke test started")

configure_api()
api_smoke_test()

print("Smoke test completed successfully")
sys.exit(0)
