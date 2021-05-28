from flask import Flask
from utils.keys import KeyPair
from utils.blockchain import Blockchain

app = Flask(__name__)

keys = KeyPair()
blockchain = Blockchain()


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/chain', methods=['GET'])
def get_chain():
    return blockchain.get_chain(), 200, {'Content-Type': 'application/json'}


if __name__ == '__main__':
    app.run()
