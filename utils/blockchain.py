import base64
import json
import hashlib
from os import path


class Blockchain:
    length = 0
    chain = []
    open_transaction = []
    last_block_hash = None

    def __init__(self):
        if not path.exists("data/chain.json"):
            print("ERR: Couldn't find chain data, copy chain-sample.json to chain.json")
            exit(1)

        with open("data/chain.json", "r") as f:
            chain = json.load(f)

        self.length = chain["length"]
        self.chain = chain["chain"]
        self.last_block_hash = base64.b64encode(hashlib.sha256(json.dumps(self.chain[0]).encode()).digest()).decode()

