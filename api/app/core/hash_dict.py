import base64
import json


def hash_dict(d: dict):
    return base64.b64encode(json.dumps(d).encode("utf-8")).decode("ascii")
