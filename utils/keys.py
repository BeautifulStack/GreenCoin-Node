import base64
from os import path, mkdir

import Crypto.Random
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15


class KeyPair:
    __private_key = None
    __public_key = None
    signer = None

    def __init__(self):
        if path.exists("data/private.key"):
            with open("data/private.key", "r") as f:
                try:
                    self.__private_key = RSA.import_key(f.read())
                except ValueError:
                    print("ERR: Corrupted key, delete data folder to generate a new key (CAUTION)")
                    exit(1)

                self.__public_key = self.__private_key.public_key()
                self.signer = pkcs1_15.new(self.__private_key)
        else:
            self.__generate_key()

    def __generate_key(self):
        self.__private_key = RSA.generate(1024, Crypto.Random.new().read)
        self.__public_key = self.__private_key.public_key()
        self.signer = pkcs1_15.new(self.__private_key)

        if not path.exists("data"):
            mkdir("data", 0o777)

        with open("data/private.key", "wb") as f:
            f.write(self.__private_key.export_key("PEM"))

    def sign(self, string):
        # todo: signature process, must return str
        pass

    def display(self):
        print(base64.b64encode(self.__private_key.export_key("DER")))
