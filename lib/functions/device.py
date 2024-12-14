from logging import getLogger
from os import name
from typing import Any

from flask import Response, make_response, request
from lib.datamodels import DTO_Device
from sqlalchemy.exc import IntegrityError

from lib.constants import HTTP
from lib.models import Device, DeviceSnapshot, DeviceProperty
from lib.timed_session import TimedSession

logger = getLogger(__name__)


def create_device(device_data: DTO_Device) -> Response:
    with TimedSession("create_device") as session:
        device: Device
        try:
            device = Device(name=device_data.name)
            for prop in device_data.properties:
                device_property = DeviceProperty(
                    name=prop.name, value=prop.value, device=device
                )
                device.properties.append(device_property)

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
                {"message": f"No device matches id {body['device_id']}"},
                HTTP.STATUS.BAD_REQUEST,
            )
        session.delete(device)
    return make_response(
        {"message": f"Deleted device with id '{body['device_id']}'"}, HTTP.STATUS.OK
    )


def get_device(device_id: int) -> Response:
    with TimedSession("get_device") as session:
        device = session.get(Device, device_id)
        if device is None:
            return make_response(
                {"message": f"No device matches id {device_id}"},
                HTTP.STATUS.BAD_REQUEST,
            )
        return make_response(device.as_dict(), HTTP.STATUS.OK)
