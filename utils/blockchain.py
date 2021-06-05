import base64
import json
import re
import sys
import time
from os import path
from threading import Thread

from utils.hash import *
from utils.node import Node


class Blockchain:
    __length = 0
    __tx_length = 0
    __chain = []  # el famoso blockchain
    __open_transactions = []
    __last_block_hash = None
    __node = None

    def __init__(self, node):
        self.__node = node
        if self.__node.master_host:
            if not self.__load_chain():
                chain = self.__node.request_chain()

                if not chain:
                    print("ERR: Couldn't get chain data from master node", file=sys.stderr)
                    exit(1)

                self.__length = chain["length"]
                self.__chain = chain["chain"]
                self.__tx_length = self.__chain[-1]["transactions"][-1]["index"]
                self.__last_block_hash = sha256(json.dumps(self.__chain[-1]))
        else:
            if not self.__load_chain():
                print("ERR: Couldn't find chain data, copy chain-sample.json to chain.json", file=sys.stderr)
                exit(1)

            miner = Thread(target=self.__mine, daemon=True)
            miner.start()

    def __load_chain(self):
        if not path.exists(self.__node.chain_path):
            return False

        with open(self.__node.chain_path, "r") as f:
            chain = json.load(f)

        self.__length = chain["length"]
        self.__chain = chain["chain"]
        self.__tx_length = self.__chain[-1]["transactions"][-1]["index"]
        self.__last_block_hash = sha256(json.dumps(self.__chain[-1]))

        return True

    def get_chain(self):
        return {'length': self.__length, 'chain': self.__chain}

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

        if not re.fullmatch('[a-f0-9]{40}', transaction["receiver"]):
            return {"error": "Incorrect receiver"}, 400, {'Content-Type': 'application/json'}

        # TODO: check if amount is 0

        # We're good, add transaction to queue
        self.__open_transactions.append(transaction)

        return {"new_balance": funds}, 200, {'Content-Type': 'application/json'}

    @staticmethod
    def __check_body_transaction(body):
        condition = "transaction" in body and "signature" in body and "public_key" in body
        if condition:
            transaction = body["transaction"]
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
        key = Node.read_key(base64.b64decode(public_key))
        if not key:
            return False

        address = ripemd160(sha256(public_key))
        if address != sender:
            return False

        if not Node.verify_signature(key, signature, msg):
            return False

        return True

    def get_balance(self, address):
        balance = 0
        rec_tx = [[tx["amount"] for tx in bloc["transactions"] if tx["receiver"] == address] for bloc in self.__chain]
        sen_tx = [[tx["amount"] for tx in bloc["transactions"] if tx["sender"] == address] for bloc in self.__chain]
        rec_open_tx = [tx["amount"] for tx in self.__open_transactions if tx["receiver"] == address]
        sen_open_tx = [tx["amount"] for tx in self.__open_transactions if tx["sender"] == address]

        for bloc in rec_tx:
            for tx in bloc:
                balance += tx

        for tx in rec_open_tx:
            balance += tx

        for bloc in sen_tx:
            for tx in bloc:
                balance -= tx

        for tx in sen_open_tx:
            balance -= tx

        return balance

    def get_open_transactions(self):
        return self.__open_transactions

    def __mine(self):
        while True:
            time.sleep(60)

            if not self.__open_transactions:
                continue

            for i, tx in enumerate(self.__open_transactions):
                tx["index"] = self.__tx_length + (i + 1)

            block = {
                "index": self.__length,
                "previous_hash": self.__last_block_hash,
                "time": time.time(),
                "transactions": self.__open_transactions
            }

            self.__chain.append(block)
            self.__length += 1
            self.__tx_length += len(self.__open_transactions)
            self.__last_block_hash = sha256(json.dumps(block))
            self.__open_transactions = []

            with open(self.__node.chain_path, "w") as f:
                f.write(json.dumps({'length': self.__length, 'chain': self.__chain}))

            self.__node.send_block(block)

            print(f"New block : {block['index']}")

    def __verify_chain(self):
        # TODO: check the previous hash of each block
        pass

    def new_block(self, body):
        key = Node.read_key(base64.b64decode(body["public_key"]))
        if not key:
            return {"error": "Invalid public key"}, 400, {'Content-Type': 'application/json'}

        if not Node.verify_signature(key, body["signature"], json.dumps(body["block"])):
            return {"error": "Invalid signature"}, 400, {'Content-Type': 'application/json'}

        if self.__last_block_hash != body["block"]["previous_hash"]:
            return {"error": "Invalid previous hash"}, 400, {'Content-Type': 'application/json'}

        self.__chain.append(body["block"])
        self.__length += 1
        self.__tx_length += len(body["block"]["transactions"])
        self.__last_block_hash = sha256(json.dumps(body["block"]))

        with open(self.__node.chain_path, "w") as f:
            f.write(json.dumps({'length': self.__length, 'chain': self.__chain}))

        print(f"New block : {body['block']['index']}")
        return "Ok", 200, {'Content-Type': 'application/json'}

    def new_reward(self, body):
        transaction = json.dumps(body["transaction"])
        if not Node.verify_signature(self.__node.web_key, body["signature"], transaction):
            return {"error": "Invalid signature"}, 400, {'Content-Type': 'application/json'}

        self.__open_transactions.append(body["transaction"])
        return "Ok", 200, {'Content-Type': 'application/json'}
