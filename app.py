import logging
from typing import Any

from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from lib.block_timer import BlockTimer
from lib.config import Config
from lib.constants import HTTP
from lib.models import Base, Log

config = Config(__file__)
logger = logging.getLogger(__name__)
app = Flask(__name__)


@app.route("/", methods=["GET"])
def index():
    return {"status": "success", "message": "Hello, World!"}, HTTP.OK


@app.route("/timer", methods=["GET"])
def timer():
    with BlockTimer():
        for i in range(1000000):
            x = i + 1
            x = x + 1
    return {"status": "success"}, HTTP.OK


@app.route("/db")
def db_test() -> tuple[dict[str, Any], int]:
    logger.warning("Test log")
    engine = create_engine("sqlite:///dev.db")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        logs = session.query(Log).all()
        logs_list = [log.as_dict() for log in logs]
    return {"status": "success", "logs": logs_list}, HTTP.OK


if __name__ == "__main__":
    logger.info("Running app on port: %s", config.server_c.port)
    app.run(host="0.0.0.0", port=config.server_c.port)
    logger.info("App run successfully")
