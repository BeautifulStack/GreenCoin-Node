from flask import Flask, request
from utils.keys import KeyPair
from utils.blockchain import Blockchain

app = Flask(__name__)
keys = KeyPair()
blockchain = Blockchain()

print(blockchain.very_authenticity(
    "2c48a5ff54f40c3ddd4eb0b6784642796fdb179e",
    "MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDFRQJmUlfDmmOCbzdrnc6iW04CsvtxymYbglB7C727ZTdZoc698h/Jf3ZMuk4jXxFLMjX06j46rPWjraMr8K9wmpFQwqhtrrr7UTVshbPS4uEnfVW+q3K6gqf5SsbhbgrlbOO9olyGSQQe3GsWRLpPrDFbIZg8fcu26krhIpezUQIDAQAB",
    "Wm6NZHWIJJZrbLajHWvsC5YP60yL6oO+NDhz06D3DZOu/wd8+p27ZQNW1A0o3KzO5IxJpgHWMwffjeIjjMBFoqIUOxwMe2Jr5gLEH8RmX7MkDadlE9gipsw1l0xfcfsPYK/Fdr+GI4JMnhKC4cwfMhmioKnfNLXZ6PDAfm0sr9E=",
    "Test"
))


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
