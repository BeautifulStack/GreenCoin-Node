import base64
import json
import hashlib
from os import path


class Blockchain:
    __length = 0
    __chain = []  # el famoso blockchain
    __open_transaction = []
    __last_block_hash = None

    def __init__(self):
        if not path.exists("data/chain.json"):
            print("ERR: Couldn't find chain data, copy chain-sample.json to chain.json")
            exit(1)

        with open("data/chain.json", "r") as f:
            chain = json.load(f)

        self.__length = chain["length"]
        self.__chain = chain["chain"]
        self.__last_block_hash = base64.b64encode(
            hashlib.sha256(json.dumps(self.__chain[0]).encode()).digest()).decode()

    def get_chain(self):
        return json.dumps({'length': self.__length, 'chain': self.__chain})

    def new_transaction(self, body):
        if not self.__check_body_transaction(body):
            return {"error": "Missing argument(s)"}, 400, {'Content-Type': 'application/json'}

    def __very_authenticity(self, sender, public_key):
        pass

    @staticmethod
    def __check_body_transaction(body):
        condition = "transaction" in body or "signature" in body or "public_key" in body
        if condition:
            condition = "sender" in body or "receiver" in body or "public_key" in body or "time" in body
            if condition:
                return True
            else:
                return False
        else:
            return False
