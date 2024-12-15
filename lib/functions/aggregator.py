from logging import getLogger
from flask import Response, make_response
from lib.datamodels import DTO_Aggregator, DTO_Device
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from lib.constants import HTTP
from lib.functions.device import create_device, find_or_create_device
from lib.models import Aggregator, Device, DeviceMetric, DeviceProperty, DeviceSnapshot
from lib.timed_session import TimedSession

logger = getLogger(__name__)


def create_aggregator_snapshot(aggregator_data: DTO_Aggregator) -> DTO_Aggregator:
    with TimedSession("create_aggregator_snapshot") as session:
        stmt = select(Aggregator).where(Aggregator.name == aggregator_data.name)
        aggregator = session.execute(stmt).scalar()

        if not aggregator:
            aggregator = Aggregator(
                name=aggregator_data.name,
            )
            session.add(aggregator)

        for device_data in aggregator_data.devices:
            device = get_or_create_device(session, device_data, aggregator)
            add_device_properties_and_snapshots(session, device, device_data)

        return aggregator.as_dto()


def get_or_create_device(
    session: Session, device_data: DTO_Device, aggregator: Aggregator
) -> Device:
    stmt = select(Device).where(Device.name == device_data.name)
    device = session.execute(stmt).scalar()

    if not device:
        device = Device(name=device_data.name, aggregator=aggregator)
        session.add(device)

    return device


def add_device_properties_and_snapshots(
    session: Session, device: Device, device_data: DTO_Device
) -> None:
    for property_data in device_data.properties:
        logger.debug(
            "Adding property '%s' to '%s'", property_data.name, device_data.name
        )
        existing_property = next(
            (prop for prop in device.properties if prop.name == property_data.name),
            None,
        )

        if existing_property and existing_property.value == property_data.value:
            continue

        if existing_property:
            existing_property.value = property_data.value
        else:
            device_property = DeviceProperty(
                name=property_data.name, value=property_data.value, device=device
            )
            session.add(device_property)

    for snapshot_data in device_data.data_snapshots:
        device_snapshot = DeviceSnapshot(
            device=device, timestamp_utc=snapshot_data.timestamp_utc
        )
        session.add(device_snapshot)

        for metric_data in snapshot_data.metrics:
            device_metric = DeviceMetric(
                name=metric_data.name, value=metric_data.value, snapshot=device_snapshot
            )
            session.add(device_metric)
