import logging

import pandas as pd
import plotly.express as px
from dash import Dash, Input, Output
from sqlalchemy import select

from lib.constants import GRAPH_COLUMN_NAMES
from lib.models import Device, DeviceSnapshot
from lib.timed_session import TimedSession

logger = logging.getLogger(__name__)


def update_graph(value: str):
    with TimedSession("update_graph") as session:
        logger.debug(value)
        stmt = (
            select(DeviceSnapshot.recorded_time, DeviceSnapshot.metrics)
            .join(Device, DeviceSnapshot.device_id == Device.id)
            .where(Device.name == value)
        )
        device_metrics = [
            {GRAPH_COLUMN_NAMES[0]: met[0], GRAPH_COLUMN_NAMES[1]: met[1]}
            for met in session.execute(stmt)
        ]
        df = pd.DataFrame(device_metrics, columns=GRAPH_COLUMN_NAMES)
        logger.debug("Ram Usage Dataframe:\n%s", df)

    return px.line(df, x=GRAPH_COLUMN_NAMES[0], y=GRAPH_COLUMN_NAMES[1])


def init_callbacks(app: Dash):
    app.callback(
        Output("graph-content", "figure"), Input("dropdown-selection", "value")
    )(update_graph)
