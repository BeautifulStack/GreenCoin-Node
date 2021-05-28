from flask import Flask
from utils.Keys import KeyPair

app = Flask(__name__)

keys = KeyPair()
keys.display()


@app.route('/')
def hello_world():
    return 'Hello World!'


if __name__ == '__main__':
    app.run()
