import hashlib
import json


def sha256_hex(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def sha256_json(value: object) -> str:
    content = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return sha256_hex(content)
