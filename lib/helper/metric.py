from typing import List

from sqlalchemy import select, func
from datetime import datetime

from lib.models import DeviceMetric, DeviceSnapshot, Device
from lib.timed_session import TimedSession

from logging import getLogger

logger = getLogger(__name__)


def get_metric_names() -> List[str]:
    with TimedSession("get_metric_names") as session:
        stmt = select(DeviceMetric.name).distinct()
        result = session.execute(stmt).scalars()
        return list(result)


def get_count_of_metrics(
    device_name: str | None,
    start_datetime: datetime | None = None,
    end_datetime: datetime | None = None,
) -> int:
    with TimedSession("get_count_of_metrics") as session:
        query = (
            session.query(func.count(DeviceMetric.id)).join(DeviceSnapshot).join(Device)
        )
        if device_name:
            query = query.filter(Device.name == device_name)
        if start_datetime:
            query = query.filter(DeviceSnapshot.timestamp_utc <= start_datetime)
        if device_name:
            query = query.filter(DeviceSnapshot.timestamp_utc >= end_datetime)
        count = query.scalar()

        logger.debug("Count of metrics: %d", count)
    return count
