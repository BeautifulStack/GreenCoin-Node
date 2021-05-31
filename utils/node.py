import base64
import json
import sys
from os import path

import Crypto.Random
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15


class Node:
    __private_key = None
    __public_key = None
    signer = None
    chain_path = None
    peers = []
    master = None
    web_key = None

    def __init__(self):
        self.__import_config()
        self.__import_key()

    def __import_config(self):
        if path.exists("data/config.json"):
            with open("data/config.json", "r") as f:
                config = json.load(f)

            self.master = config["master"]
            self.chain_path = config["chain"]
            self.peers = config["peers"]
            self.web_key = config["web_key"]

        else:
            print("ERR: Couldn't find config data, copy config-sample.json to config.json", file=sys.stderr)
            exit(1)

    def __import_key(self):
        if path.exists("data/private.key"):
            with open("data/private.key", "r") as f:
                try:
                    self.__private_key = RSA.import_key(f.read())
                except ValueError:
                    print("ERR: Corrupted key, delete data folder to generate a new key (CAUTION)", file=sys.stderr)
                    exit(1)

                self.__public_key = self.__private_key.public_key()
                self.signer = pkcs1_15.new(self.__private_key)
        else:
            self.__generate_key()

    def __generate_key(self):
        self.__private_key = RSA.generate(1024, Crypto.Random.new().read)
        self.__public_key = self.__private_key.public_key()
        self.signer = pkcs1_15.new(self.__private_key)

        with open("data/private.key", "wb") as f:
            f.write(self.__private_key.export_key("PEM"))

    def sign(self, string) -> str:
        # TODO: signature process
        pass

    def display(self):
        return base64.b64encode(self.__public_key.export_key("DER"))

    def add_peer(self, body):
        pass
