from typing import List

from sqlalchemy import select, func

from lib.models import DeviceMetric, DeviceSnapshot, Device
from lib.timed_session import TimedSession


def get_metric_names() -> List[str]:
    with TimedSession("get_metric_names") as session:
        stmt = select(DeviceMetric.name).distinct()
        result = session.execute(stmt).scalars()
        return list(result)


def get_count_of_metrics(device_name: str | None, start_id: int) -> int:
    with TimedSession("get_count_of_metrics") as session:
        query = (
            session.query(func.count(DeviceMetric.id)).join(DeviceSnapshot).join(Device).filter(DeviceSnapshot.id <= start_id)
        )
        if device_name:
            query = query.filter(Device.name == device_name)
        count = query.scalar()
    return count
