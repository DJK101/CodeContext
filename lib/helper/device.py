from datetime import datetime
from logging import getLogger
from typing import Any, List, Tuple

from flask import Response, make_response, request
from sqlalchemy import delete, func, select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import aliased

from lib.block_timer import BlockTimer
from lib.constants import HTTP
from lib.datamodels import DTO_Device, DTO_Metric
from lib.models import Aggregator, Device, DeviceMetric, DeviceProperty, DeviceSnapshot
from lib.timed_session import TimedSession

logger = getLogger(__name__)


def create_device(device_data: DTO_Device, aggregator_id: int) -> DTO_Device:
    with TimedSession("create_device") as session:
        device = Device(name=device_data.name, aggregator_id=aggregator_id)

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

        session.add(device)

        return device.as_dto()


def get_device(device_name: str) -> DTO_Device:
    with TimedSession("get_device") as session:
        stmt = select(Device).where(Device.name == device_name)
        device = session.execute(stmt).scalar_one()
        return device.as_dto()


def update_device(device_name: str, device_data: DTO_Device) -> DTO_Device:
    with TimedSession("update_device") as session:
        stmt = select(Device).where(Device.name == device_name)
        device = session.execute(stmt).scalar_one()
        device.name = device_data.name

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

        return device.as_dto()


def delete_device(device_name: str) -> None:
    with TimedSession("delete_device") as session:
        stmt = delete(Device).where(Device.name == device_name)
        session.delete(stmt)


def get_device_names(limit: int = 20) -> List[str]:
    with TimedSession("get_device_names") as session:
        stmt = select(Device.name).limit(limit)
        result = session.execute(stmt).scalars()
        return list(result)


def get_device_metrics(
    device_name: str, metric_name: str, limit: int = 20
) -> List[Tuple[int, datetime]]:
    with TimedSession("get_device_metrics") as session:
        count = session.query(DeviceMetric).count()
        logger.debug("Number of rows in table: %s", count)

        stmt = (
            select(DeviceSnapshot.timestamp_utc, DeviceMetric.value)
            .join(DeviceSnapshot)
            .join(Device)
            .where(Device.name == device_name)
            .where(DeviceMetric.name == metric_name)
            .limit(limit)
        )
        result = session.execute(stmt).all()
        metrics: List[Tuple[int, datetime]] = [(row[0], row[1]) for row in result]
        return metrics


def get_all_device_metrics(
    device_name: str, start_id: int | None = None, page: int = 1, page_size: int = 20
):
    with TimedSession("get_all_device_metrics") as session:
        logger.debug("Requested page %s", page)
        offset = (page - 1) * page_size

        stmt = (
            select(
                Device.name,
                DeviceSnapshot.timestamp_utc,
                DeviceMetric.name,
                DeviceMetric.value,
            )
            .select_from(Device)  # Explicitly set the starting table
            .join(
                DeviceSnapshot, DeviceSnapshot.device_id == Device.id
            )  # Explicit ON clause
            .join(
                DeviceMetric, DeviceMetric.snapshot_id == DeviceSnapshot.id
            )  # Explicit ON clause
            .where(Device.name == device_name)
        )

        if start_id:
            stmt = stmt.where(DeviceSnapshot.id <= start_id)

        stmt = stmt.order_by(DeviceSnapshot.id.desc()).offset(offset).limit(page_size)

        result = session.execute(stmt).all()
        metrics: List[List[Any]] = [[column for column in row] for row in result]
        return metrics


def get_latest_device_snapshot_id():
    with TimedSession("get_latest_device_id") as session:
        stmt = select(DeviceSnapshot.id).order_by(DeviceSnapshot.id.desc())
        return session.execute(stmt).scalar()
