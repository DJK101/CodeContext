from logging import getLogger
from typing import Any

from dateutil import parser
from flask import Response, make_response, request
from lib.datamodels import DTO_DataSnapshot, DTO_Metric

from lib.constants import HTTP
from lib.models import Device, DeviceMetric, DeviceSnapshot
from lib.timed_session import TimedSession

logger = getLogger(__name__)


def create_snapshot(device_id: int, snapshot_data: DTO_DataSnapshot) -> Response:
    with TimedSession("create_snapshot") as session:
        try:
            device = session.get(Device, device_id)

            if device is None:
                raise ValueError(f"Device with ID {device_id} not found")

            snapshot = DeviceSnapshot(
                device=device,
                recorded_time=snapshot_data.timestamp_utc,
            )

            for metric in snapshot_data.metrics:
                device_metric = DeviceMetric(
                    name=metric.name, value=metric.value, snapshot=snapshot
                )
                snapshot.metrics.append(device_metric)

            session.add(snapshot)
        except KeyError as ke:
            logger.error("Metric creation failed, missing args in JSON: %s", ke)
            return make_response(
                {"message": f"Request body missing key: {ke}"}, HTTP.STATUS.BAD_REQUEST
            )

        return make_response(
            {"message": f"Added data snapshot for {snapshot.device.name}"},
            HTTP.STATUS.OK,
        )


def get_metrics(device_id: int):
    with TimedSession("get_metrics") as session:
        device: Device | None = session.get(Device, device_id)
        if device is None:
            return {
                "message": f"no device matches id '{device_id}'"
            }, HTTP.STATUS.BAD_REQUEST
        metrics: list[DeviceSnapshot] = (
            session.query(DeviceSnapshot)
            .filter(DeviceSnapshot.device_id == device_id)
            .limit(50)
            .all()
        )
        metrics_list: list[dict[str, Any]] = [metric.as_dict() for metric in metrics]
        return {"metrics": metrics_list}, HTTP.STATUS.OK
