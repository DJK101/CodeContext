import logging

from flask import Flask

from lib.block_timer import BlockTimer
from lib.config import Config

config = Config(__file__)
logger = logging.getLogger(__name__)
app = Flask(__name__)


@app.route("/")
def index():
    with BlockTimer():
        logging.info("Test message, 10,000 for loop")
        for i in range(10000):
            x = i + 1
    return {"status": "success", "message": "Hello, World!"}, 200


if __name__ == "__main__":
    logger.info("Running app on port: %s", config.server_c.port)
    app.run(host="0.0.0.0", port=config.server_c.port)
    logger.info("App run successfully")
