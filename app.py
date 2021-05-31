from flask import Flask, request
from utils.node import Node
from utils.blockchain import Blockchain

app = Flask(__name__)
node = Node()
blockchain = Blockchain(node)


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


@app.get('/public_key')
def get_public_key():
    return {"public_key": node.display().decode()}, 200, {'Content-Type': 'application/json'}


if __name__ == '__main__':
    app.run()
