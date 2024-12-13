import logging
from typing import Any

from flask import Flask, Response, make_response, request

import lib.functions.device as device_funcs
import lib.functions.metric as metric_funcs
from d_app import d_app
from lib.config import Config
from lib.constants import HTTP
from lib.models import Log
from lib.timed_session import TimedSession
from lib.cache import Cache

config = Config(__file__)
logger = logging.getLogger(__name__)
app = Flask(__name__)
d_app.init_dash_app(app)


@app.route("/", methods=[HTTP.METHOD.GET])
def index():
    return {"message": "Hello, World!"}, HTTP.STATUS.OK


@app.route("/db")
def db_test() -> tuple[dict[str, Any], int]:
    with TimedSession("db_test") as session:
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


@app.route("/device", methods=[HTTP.METHOD.PUT, HTTP.METHOD.DELETE, HTTP.METHOD.GET])
def device():
    if request.json is None:
        return make_response("Must include a body", HTTP.STATUS.BAD_REQUEST)
    body: dict[str, Any] = request.json
    match request.method:
        case HTTP.METHOD.GET:
            device_id = body["device_id"]
            return Cache.cache_data(
                "device" + device_id, device_funcs.get_device, [device_id]
            )
        case HTTP.METHOD.PUT:
            return device_funcs.create_device()
        case HTTP.METHOD.DELETE:
            return device_funcs.delete_device()

    return make_response({"message": "Invalid method type"}, HTTP.STATUS.BAD_REQUEST)


@app.route("/metric", methods=[HTTP.METHOD.PUT, HTTP.METHOD.GET])
def metric():
    match request.method:
        case HTTP.METHOD.GET:
            return metric_funcs.get_metrics()
        case HTTP.METHOD.PUT:
            return metric_funcs.create_metric()

    return make_response({"message": "Invalid method type"}, HTTP.STATUS.BAD_REQUEST)


if __name__ == "__main__":
    logger.info("Running app on port: %s", config.server_c.port)
    app.run(host="127.0.0.1", port=config.server_c.port)
    logger.info("App run successfully")
