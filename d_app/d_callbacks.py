import logging

import pandas as pd
import plotly.express as px
from dash import Dash, Input, Output, State
from flask import session
from sqlalchemy import select

from lib.constants import GRAPH_COLUMN_NAMES
from lib.helper.device import (
    get_all_device_metrics,
    get_device_metrics,
    get_device_names,
    get_latest_device_snapshot_id,
)
from lib.helper.metric import get_count_of_metrics, get_metric_names
from lib.models import Device, DeviceSnapshot
from lib.timed_session import TimedSession

logger = logging.getLogger(__name__)


def reset_start_id(n_clicks: int):
    session.pop("start_id", None)

def update_table(page: int, page_size: int, device_name: str):
    if not session.get("start_id"):
        start_id = get_latest_device_snapshot_id()
        session["start_id"] = start_id

    start_id = session.get("start_id")
    # page index starts from 0, so we have to increment by one
    metrics_list = get_all_device_metrics(device_name, start_id, page + 1, page_size)

    total_metrics = get_count_of_metrics(device_name, start_id)
    logger.debug("Total metrics: %s", total_metrics)
    total_pages = total_metrics // page_size
    logger.debug("Total pages: %s", total_pages)

    all_metrics = [
        {"Device": met[0], "Recorded time": met[1], "Name": met[2], "Value": met[3]}
        for met in metrics_list
    ]
    df = pd.DataFrame(all_metrics, columns=["Device", "Recorded time", "Name", "Value"])
    return (
        df.to_dict("records"),
        [{"name": col, "id": col} for col in df.columns],
        total_pages,
    )


def update_graph(n_clicks, device_name: str, metric_name: str):
    metrics_list = get_device_metrics(device_name, metric_name, 1000)

    device_metrics = [
        {"Recorded time": met[0], metric_name: met[1]} for met in metrics_list
    ]
    df = pd.DataFrame(device_metrics, columns=["Recorded time", metric_name])

    return px.line(df, x="Recorded time", y=metric_name)


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
        State("device-selection", "value"),
        State("metric-selection", "value"),
    )(update_graph)

    app.callback(
        Output("device-selection", "options"), Input("refresh-device-names", "n_clicks")
    )(update_device_list)

    app.callback(
        Output("metric-selection", "options"), Input("refresh-metric-names", "n_clicks")
    )(update_metric_list)

    app.callback(
        Output("data-table", "data"),  # Update the table data
        Output("data-table", "columns"),
        Output("data-table", "page_count"),
        # Update the table columns
        Input("data-table", "page_current"),
        Input("data-table", "page_size"),
        Input("device-selection", "value"),
        # Trigger on button click
    )(update_table)

    app.callback(
        Input("update-button", "n_clicks"),
    )(reset_start_id)
