import logging
from typing import Any

from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from lib.block_timer import BlockTimer
from lib.config import Config
from lib.constants import HTTP
from lib.models import Base, Log

config = Config(__file__)
logger = logging.getLogger(__name__)
app = Flask(__name__)

engine = create_engine("sqlite:///dev.db")
Base.metadata.create_all(engine)
Session = sessionmaker(engine)


@app.route("/", methods=[HTTP.METHOD.GET])
def index():
    return {"message": "Hello, World!"}, HTTP.STATUS.OK


@app.route("/timer", methods=[HTTP.METHOD.GET])
def timer():
    time = 0
    with BlockTimer() as bt:
        for i in range(1000000):
            x = i + 1
            x = x + 1
            time = bt.end_time - bt.start_time
    return {"message": ("executed in %s nanonseconds", time)}, HTTP.STATUS.OK


@app.route("/db")
def db_test() -> tuple[dict[str, Any], int]:
    with Session.begin() as session:
        logs = session.query(Log).all()
        logs_list = [log.as_dict() for log in logs]

    return {"logs": logs_list}, HTTP.STATUS.OK


@app.route("/test/<string:log_type>", methods=[HTTP.METHOD.GET])
def log_test(log_type: str):
    match log_type:
        case "INFO":
            logger.info("Test info log")
        case "WARNING":
            logger.warning("Test warning log")
        case "ERROR":
            logger.error("Test error log")
        case _:
            return {"message": "invlaid log type"}, HTTP.STATUS.BAD_REQUEST
    return {"logtype": log_type}, HTTP.STATUS.OK


if __name__ == "__main__":
    logger.info("Running app on port: %s", config.server_c.port)
    app.run(host="0.0.0.0", port=config.server_c.port)
    logger.info("App run successfully")
