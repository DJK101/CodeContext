from typing import List

from sqlalchemy import select

from lib.models import DeviceMetric
from lib.timed_session import TimedSession


def get_metric_names() -> List[str]:
    with TimedSession("get_metric_names") as session:
        stmt = select(DeviceMetric.name).distinct()
        result = session.execute(stmt).scalars()
        return list(result)
