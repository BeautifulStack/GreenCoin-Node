from Crypto.Hash import RIPEMD160, SHA256


def sha256(key: str) -> str:
    return SHA256.new(key.encode()).hexdigest()


def ripemd160(key: str) -> str:
    h = RIPEMD160.new()
    h.update(key.encode())
    return h.hexdigest()
