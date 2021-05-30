from flask import Flask, request
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
    """
    Takes form-data encoding for now, may switch to JSON later
    """

    return blockchain.new_transaction(request.form)


if __name__ == '__main__':
    app.run()
