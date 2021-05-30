import hashlib
import json

from Crypto.Hash import RIPEMD160


def sha256_dict(bloc: dict) -> str:
    result = hashlib.sha256(json.dumps(bloc).encode()).hexdigest()
    return result


def sha256_str(key: str) -> str:
    return hashlib.sha256(key.encode()).hexdigest()


def ripemd160(key: str) -> str:
    h = RIPEMD160.new()
    h.update(key.encode())
    return h.hexdigest()
