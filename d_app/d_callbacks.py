import logging

import pandas as pd
import plotly.express as px
from dash import Dash, Input, Output
from sqlalchemy import select

from lib.timed_session import Session
from lib.models import Device, DeviceMetric

logger = logging.getLogger(__name__)

def update_graph(value: str):
    with Session.begin() as session:
        logger.debug(value)
        stmt = (
            select(DeviceMetric.recorded_time, DeviceMetric.ram_usage)
            .join(Device, DeviceMetric.device_id == Device.id)
            .where(Device.name == value)
        )
        device_metrics = [{"Recorded Time": met[0], "Ram Usage (MB)": met[1]//1_000_000} for met in session.execute(stmt)]
        df = pd.DataFrame(device_metrics, columns=["Recorded Time", "Ram Usage (MB)"])
        logger.debug("Ram Usage Dataframe:\n%s", df)

    return px.line(df, x="Recorded Time", y="Ram Usage (MB)")


def init_callbacks(app: Dash):
    app.callback(
        Output("graph-content", "figure"), Input("dropdown-selection", "value")
    )(update_graph)
