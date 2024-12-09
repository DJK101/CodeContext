import logging
from typing import Any, List

from dateutil import parser
from flask import Flask, request
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from lib.block_timer import BlockTimer
from lib.config import Config
from lib.constants import HTTP
from lib.models import Base, Device, DeviceMetric, Log

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


@app.route("/device/", methods=[HTTP.METHOD.PUT])
def create_device():
    device_info: Any
    try:
        device_info = request.json
    except Exception as e:
        logger.error(e)
        return {"message": str(e)}
    with Session.begin() as session:
        device: Device
        try:
            device = Device(
                name=device_info["name"],
                cores=device_info["cores"],
                ram_total=device_info["ram_total"],
                disk_total=device_info["disk_total"],
            )
        except KeyError as ke:
            logger.error("Device creation failed, missing args in JSON: %s", ke)
            return {
                "message": f"request body missing key: {ke}"
            }, HTTP.STATUS.BAD_REQUEST

        session.add(device)
    return {"message": "device created"}, HTTP.STATUS.OK


@app.route("/metric/<int:device_id>", methods=[HTTP.METHOD.PUT])
def create_metric(device_id: int):
    metric_info: Any = request.json
    logger.info("metric_info in request: %s", metric_info)
    with Session.begin() as session:
        try:
            metric = DeviceMetric(
                device_id=device_id,
                recorded_time=parser.isoparse(metric_info["recorded_time"]),
                ram_usage=metric_info["ram_usage"],
                disk_usage=metric_info["disk_usage"],
            )
            session.add(metric)
        except KeyError as ke:
            logger.error("Device creation failed, missing args in JSON: %s", ke)
            return {
                "message": f"request body missing key: {ke}"
            }, HTTP.STATUS.BAD_REQUEST
        except ValueError as ve:
            logger.error(
                "Device creation request failed, timestamp in wrong format. Given: '%s'",
                metric_info["recorded_time"],
            )
            return {
                "message": f"request body missing key: {ve}"
            }, HTTP.STATUS.BAD_REQUEST

    return {
        "message": f"successfully added metric to device with id: {device_id}"
    }, HTTP.STATUS.OK


@app.route("/device-metrics/<int:device_id>", methods=[HTTP.METHOD.GET])
def get_metrics(device_id: int):
    with Session.begin() as session:
        device: Device | None = session.scalar(
            select(Device).where(Device.id == device_id)
        )
        if device is None:
            return {"message": "no device matches id"}, HTTP.STATUS.BAD_REQUEST
        metrics: List[DeviceMetric] = device.metrics
        metrics_list: list[dict[str, Any]] = [metric.as_dict() for metric in metrics]
        return {"metrics": metrics_list}, HTTP.STATUS.OK


if __name__ == "__main__":
    logger.info("Running app on port: %s", config.server_c.port)
    app.run(host="127.0.0.1", port=config.server_c.port)
    logger.info("App run successfully")
