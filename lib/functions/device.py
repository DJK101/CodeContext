from logging import getLogger
from typing import Any

from flask import Response, make_response, request
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound

from lib.constants import HTTP
from lib.datamodels import DTO_Device
from lib.models import Aggregator, Device, DeviceProperty, DeviceSnapshot
from lib.timed_session import TimedSession

logger = getLogger(__name__)


def find_or_create_device(device_data: DTO_Device, aggregator: Aggregator) -> Device:
    with TimedSession("find_or_create_device") as session:
        try:
            stmt = select(Device).where(Device.name == device_data.name)
            return session.execute(stmt).scalar_one()
        except NoResultFound:
            session.rollback()
            # logger.info("No device found, creating '%s'...", device_data.name)

        return create_device(device_data, aggregator)


def create_device(device_data: DTO_Device, aggregator: Aggregator) -> Device:
    device = Device(name=device_data.name, aggregator=aggregator)

    for property_data in device_data.properties:
        device_property = DeviceProperty(
            name=property_data.name, value=property_data.value, device=device
        )
        device.properties.append(device_property)

    for snapshot_data in device_data.data_snapshots:
        snapshot = DeviceSnapshot(
            device=device, timestamp_utc=snapshot_data.timestamp_utc
        )
        device.snapshots.append(snapshot)

    return device


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
