from logging import getLogger
from typing import Any

from flask import Response, make_response, request
from sqlalchemy.exc import IntegrityError

from lib.constants import HTTP
from lib.models import Device, DeviceMetric
from lib.timed_session import TimedSession

logger = getLogger(__name__)


def create_device() -> Response:
    device_info: Any
    try:
        device_info = request.json
    except Exception as e:
        logger.error(e)
        return make_response({"message": str(e)}, 200)
    with TimedSession("create_device") as session:
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
            return make_response(
                {"message": f"request body missing key: {ke}"}, HTTP.STATUS.BAD_REQUEST
            )

        try:
            session.add(device)
            session.flush()
        except IntegrityError as ie:
            session.rollback()
            logger.error("Device creation failed: %s", ie)
            return {
                "message": f"Device name already exists: '{ie.params[0]}'"  # type: ignore
            }, HTTP.STATUS.CONFLICT
    return make_response({"message": "device created"}, HTTP.STATUS.OK)


def delete_device() -> Response:
    body: Any = request.json
    with TimedSession("delete_device") as session:
        device: Device | None = session.get(Device, body["device_id"])
        if device is None:
            return make_response(
                {"message": "no device matches id"}, HTTP.STATUS.BAD_REQUEST
            )
        session.delete(device)
    return make_response(
        {"message": f"Deleted device with id '{body['device_id']}'"}, HTTP.STATUS.OK
    )
