import os
from flask import Flask
from flask_cors import CORS
from .socket import create_socket
from .api import create_api
from .utils import read_cors


def create_app():
    app = Flask(__name__)
    app.secret_key = os.environ["FLASK_SECRET"]
    CORS(app, origins=read_cors())
    api = create_api(app)
    socket = create_socket(app)
    return app, socket, api


def run(host, port, debug):
    app, socket, _ = create_app()
    app.config["APP_PORT"] = port
    socket.run(app, host=host, port=port, debug=debug)


if __name__ == "__main__":
    run("127.0.0.1", 5000, True)
