from logging import getLogger
from typing import Any

from dateutil import parser
from flask import Response, make_response, request

from lib.constants import HTTP
from lib.models import Device, DeviceMetric
from lib.timed_session import TimedSession

logger = getLogger(__name__)


def create_metric() -> Response:
    body: Any = request.json
    logger.info("metric_info in request: %s", body)
    with TimedSession("create_metric") as session:
        try:
            metric = DeviceMetric(
                device_id=body["device_id"],
                recorded_time=parser.isoparse(body["recorded_time"]),
                ram_usage=body["ram_usage"],
                disk_usage=body["disk_usage"],
            )
            session.add(metric)
        except KeyError as ke:
            logger.error("Metric creation failed, missing args in JSON: %s", ke)
            return make_response(
                {"message": f"Request body missing key: {ke}"}, HTTP.STATUS.BAD_REQUEST
            )
        except ValueError as ve:
            logger.error(
                "Metric creation request failed, timestamp in wrong format. Given: '%s'",
                body["recorded_time"],
            )
            return make_response(
                {"message": f"Timestamp in wrong format: {ve}"}, HTTP.STATUS.BAD_REQUEST
            )

    return make_response(
        {"message": f"Added metric to device with id: {body['device_id']}"},
        HTTP.STATUS.OK,
    )


def get_metrics(device_id: int):
    with TimedSession("get_metrics") as session:
        device: Device | None = session.get(Device, device_id)
        if device is None:
            return {
                "message": f"no device matches id '{device_id}'"
            }, HTTP.STATUS.BAD_REQUEST
        metrics: list[DeviceMetric] = (
            session.query(DeviceMetric)
            .filter(DeviceMetric.device_id == device_id)
            .limit(50)
            .all()
        )
        metrics_list: list[dict[str, Any]] = [metric.as_dict() for metric in metrics]
        return {"metrics": metrics_list}, HTTP.STATUS.OK
