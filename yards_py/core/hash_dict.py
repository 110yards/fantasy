import json
import hashlib


def hash_dict(d: dict):
    return hashlib.md5(json.dumps(d).encode("utf-8")).hexdigest()
