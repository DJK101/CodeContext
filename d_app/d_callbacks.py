import logging

import pandas as pd
import plotly.express as px
from dash import Dash, Input, Output, State
from sqlalchemy import select

from lib.constants import GRAPH_COLUMN_NAMES
from lib.helper.device import get_device_metrics, get_device_names
from lib.helper.metric import get_metric_names
from lib.models import Device, DeviceSnapshot
from lib.timed_session import TimedSession

logger = logging.getLogger(__name__)


def update_graph(n_clicks, device_name: str, metric_name: str):
    logger.debug(device_name)
    dto_metrics = get_device_metrics(device_name, metric_name, 1000)

    device_metrics = [
        {GRAPH_COLUMN_NAMES[0]: met[0], GRAPH_COLUMN_NAMES[1]: met[1]}
        for met in dto_metrics
    ]
    df = pd.DataFrame(device_metrics, columns=GRAPH_COLUMN_NAMES)
    logger.debug("Ram Usage Dataframe:\n%s", df)

    return px.line(df, x=GRAPH_COLUMN_NAMES[0], y=GRAPH_COLUMN_NAMES[1])


def update_device_list(n_clicks: int):
    device_names = get_device_names()
    logger.info("Got device names for dropdown: %s", device_names)
    return device_names


def update_metric_list(n_clicks: int):
    metric_names = get_metric_names()
    logger.info("Got device names for dropdown: %s", metric_names)
    return metric_names

def init_callbacks(app: Dash):
    app.callback(
        Output("graph-content", "figure"),
        Input("refresh-graph", "n_clicks"),
        [State("device-selection", "value"), State("metric-selection", "value")],
    )(update_graph)
    app.callback(
        Output("device-selection", "options"), Input("refresh-device-names", "n_clicks")
    )(update_device_list)
    app.callback(
        Output("metric-selection", "options"), Input("refresh-metric-names", "n_clicks")
    )(update_metric_list)
