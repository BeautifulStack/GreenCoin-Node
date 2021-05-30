import base64
from os import path
from utils.hash import *

from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256


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
        self.__last_block_hash = sha256_dict(self.__chain[0])

    def get_chain(self):
        return json.dumps({'length': self.__length, 'chain': self.__chain})

    def new_transaction(self, body):
        transaction = self.__check_body_transaction(body)
        if not transaction:
            return {"error": "Missing argument(s)"}, 400, {'Content-Type': 'application/json'}

        if not self.__very_authenticity(
                transaction["sender"],
                body["public_key"],
                body["signature"],
                json.dumps(transaction)
        ):
            return {"error": "Invalid public key or signature"}, 400, {'Content-Type': 'application/json'}

        funds = self.get_balance(transaction["sender"]) - transaction["amount"]
        if funds < 0:
            return {"error": "Not enough funds"}, 400, {'Content-Type': 'application/json'}

        self.__open_transaction.append(transaction)

        return {"new_balance": funds}, 200, {'Content-Type': 'application/json'}

    @staticmethod
    def __check_body_transaction(body):
        condition = "transaction" in body and "signature" in body and "public_key" in body
        if condition:
            transaction = json.loads(body["transaction"])
            print(transaction)
            condition = ("sender" in transaction and
                         "receiver" in transaction and
                         "amount" in transaction and
                         "time" in transaction)
            if condition:
                return transaction
            else:
                return None
        else:
            return None

    @staticmethod
    def __very_authenticity(sender: str, public_key: str, signature: str, msg: str):
        try:
            key = RSA.import_key(base64.b64decode(public_key))
        except ValueError:
            return False

        address = ripemd160(sha256_str(public_key))
        if address != sender:
            return False

        decoded_sig = base64.b64decode(signature)
        h = SHA256.new(msg.encode())
        try:
            pkcs1_15.new(key).verify(h, decoded_sig)
        except ValueError:
            return False

        return True

    def get_balance(self, address):
        balance = 0
        rec_tx = [[tx["amount"] for tx in bloc["transactions"] if tx["receiver"] == address] for bloc in self.__chain]
        sen_tx = [[tx["amount"] for tx in bloc["transactions"] if tx["sender"] == address] for bloc in self.__chain]

        for tx in rec_tx:
            if len(tx) > 0:
                balance += tx[0]

        for tx in sen_tx:
            if len(tx) > 0:
                balance -= tx[0]

        return balance
