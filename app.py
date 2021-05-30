import json

from flask import Flask, request, jsonify
from utils.keys import KeyPair
from utils.blockchain import Blockchain

app = Flask(__name__)
keys = KeyPair()
blockchain = Blockchain()


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.get('/chain')
def get_chain():
    return blockchain.get_chain(), 200, {'Content-Type': 'application/json'}


@app.post('/new_transaction')
def new_transaction():
    return blockchain.new_transaction(request.get_json())


@app.get('/balance/<address>')
def get_balance(address: str):
    return {"balance": blockchain.get_balance(address)}, 200, {'Content-Type': 'application/json'}


@app.get('/open_transactions')
def get_open_transactions():
    return {"open_transactions": blockchain.get_open_transactions()}, 200, {'Content-Type': 'application/json'}


# TODO: remove this for production
@app.post('/test')
def test():
    data = request.get_json()
    return Blockchain.very_authenticity(
        data["transaction"]["sender"],
        data["public_key"],
        data["signature"],
        json.dumps(data["transaction"])
    )


if __name__ == '__main__':
    app.run()
