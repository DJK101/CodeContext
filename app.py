import logging

from flask import Flask

from lib.block_timer import BlockTimer
from lib.config import Config
from lib.constants import HTTP

config = Config(__file__)
logger = logging.getLogger(__name__)
app = Flask(__name__)


@app.route("/")
def index():
    return {"status": "success", "message": "Hello, World!"}, HTTP.OK

@app.route("/timer")
def timer():
    with BlockTimer():
        for i in range(1000000):
            x = i + 1
    return {"status": "success"}, HTTP.OK


if __name__ == "__main__":
    logger.info("Running app on port: %s", config.server_c.port)
    app.run(host="0.0.0.0", port=config.server_c.port, debug=True)
    logger.info("App run successfully")
