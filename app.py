import logging
from typing import Any

from flask import Flask, make_response, request

from lib.functions.aggregator import create_aggregator
import lib.functions.device as device_funcs
import lib.functions.snapshot as metric_funcs
from d_app import d_app
from lib.cache import Cache
from lib.config import Config
from lib.constants import HTTP
from lib.datamodels import DTO_Aggregator, DTO_DataSnapshot, DTO_Device
from lib.models import Device, Log
from lib.timed_session import TimedSession

config = Config(__name__)
cache = Cache(config.cache_c)
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
            cache_key = "device" + str(device_id)
            response = cache.cache_data(cache_key, device_funcs.get_device, [device_id])
            return response

        case HTTP.METHOD.PUT:
            device_data = DTO_Device.from_dict(body)
            return device_funcs.create_device(device_data)

        case HTTP.METHOD.DELETE:
            device_id = body["device_id"]
            cache_key = "device" + str(device_id)
            cache.expire_data(cache_key)
            return device_funcs.delete_device()

    return make_response({"message": "Invalid method type"}, HTTP.STATUS.BAD_REQUEST)


@app.route("/snapshot", methods=[HTTP.METHOD.PUT, HTTP.METHOD.GET])
def snapshot():
    if request.json is None:
        return make_response("Must include a body", HTTP.STATUS.BAD_REQUEST)
    body: dict[str, Any] = request.json
    device_id = body["device_id"]
    cache_key = "metrics" + str(device_id)

    match request.method:
        case HTTP.METHOD.GET:
            return cache.cache_data(cache_key, metric_funcs.get_metrics, [device_id])
        case HTTP.METHOD.PUT:
            cache.expire_data(cache_key)
            dto_snapshot = DTO_DataSnapshot.from_dict(body)
            return metric_funcs.create_snapshot(device_id, dto_snapshot)

    return make_response({"message": "Invalid method type"}, HTTP.STATUS.BAD_REQUEST)


@app.route("/aggregator", methods=[HTTP.METHOD.PUT])
def aggregator():
    body: dict[str, Any] = request.get_json()

    match request.method:
        case HTTP.METHOD.PUT:
            try:
                dto_aggregator = DTO_Aggregator.from_dict(body)
                return create_aggregator(dto_aggregator)
            except KeyError as e:
                logger.error("Aggregator request sent with incomplete body: %s", e)
                return make_response(
                    {"message": f"Missing key in body at {e}"}, HTTP.STATUS.BAD_REQUEST
                )

    return make_response({"message": "Invalid method type"}, HTTP.STATUS.BAD_REQUEST)


if __name__ == "__main__":
    logger.info("Running app on port: %s", config.server_c.port)
    app.run(host="127.0.0.1", port=config.server_c.port)
    logger.info("App run successfully")
