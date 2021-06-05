import base64
import json
import sys
from os import path

import Crypto.Random
import requests
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from requests.exceptions import HTTPError


class Node:
    __private_key = None
    __public_key = None
    signer = None
    chain_path = None
    peers = []
    master_host = None
    master_key = None
    web_key = None

    def __init__(self):
        self.__import_config()
        self.__import_key()

    def __import_config(self):
        if path.exists("data/config.json"):
            with open("data/config.json", "r") as f:
                config = json.load(f)

            self.master_host = config["master_host"]  # "<ip_address>:<port>"
            self.chain_path = config["chain"]
            self.peers = config["peers"]  # ["<ip_address>:<port>"]

            if self.master_host:
                self.master_key = self.read_key(base64.b64decode(config["master_key"]))
                if not self.master_key:
                    print("ERR: Corrupted master key", file=sys.stderr)
                    exit(1)
            else:
                self.web_key = self.read_key(base64.b64decode(config["web_key"]))
                if not self.web_key:
                    print("ERR: Corrupted web key", file=sys.stderr)
                    exit(1)

        else:
            print("ERR: Couldn't find config data, copy config-sample.json to config.json", file=sys.stderr)
            exit(1)

    @staticmethod
    def read_key(key):
        try:
            rsa_key = RSA.import_key(key)
        except Exception:
            return None

        return rsa_key

    def __import_key(self):
        if path.exists("data/private.key"):
            with open("data/private.key", "r") as f:
                self.__private_key = self.read_key(f.read())
                if not self.__private_key:
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

    def new_peer(self, body):
        if not self.verify_signature(self.web_key, body["signature"], body["peer"]):
            return {"error": "Invalid signature"}, 400, {'Content-Type': 'application/json'}

        self.peers.append(body["peer"])
        return "Ok", 200, {'Content-Type': 'application/json'}

    @staticmethod
    def verify_signature(key, signature, msg):
        decoded_sig = base64.b64decode(signature)
        h = SHA256.new(msg.encode())
        try:
            pkcs1_15.new(key).verify(h, decoded_sig)
        except ValueError:
            return False

        return True

    def request_chain(self):
        try:
            r = requests.get(f"http://{self.master_host}/chain")
        except HTTPError:
            return

        return r.json()

    def send_block(self, block):
        sig = base64.b64encode(self.signer.sign(SHA256.new(json.dumps(block).encode())))

        for peer in self.peers:
            try:
                requests.post(f"http://{peer}/new_block", json={
                    "block": block,
                    "signature": sig,
                    "public_key": self.__public_key
                })
            except HTTPError:
                continue
