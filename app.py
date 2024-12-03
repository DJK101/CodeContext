from flask import Flask, jsonify
from flask_caching import Cache
import logging
import json
import datetime
from lib.block_timer import BlockTimer
from lib.data_snapshot import DataSnapshot

logger = logging.getLogger(__name__)

app = Flask(__name__)


@app.route("/")
def index():
    with BlockTimer():
        logging.info("Test message, 10,000 for loop")
        for i in range(10000):
            x = i + 1
    return {"status": "success", "message": "Hello, World!"}, 200


def load_config():
    try:
        with open("config.json") as config_file:
            config = json.load(config_file)
        logging.info("Configuration loaded from config.json")
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logging.error("Error loading config.json: %s", e)
        config = {}
    return config

if __name__ == "__main__":
    config = load_config()
    port = config.get("port", 5000)
    app.run(host="0.0.0.0", port=port)
