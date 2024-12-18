from datetime import datetime
import logging
from typing import Any, List

import pandas as pd
import plotly.express as px
from dash import Dash, Input, Output, State
from flask import session

from lib.helper import metric
from lib.helper.device import (
    get_all_device_metrics,
    get_device_metrics_by_name,
    get_device_names,
    get_latest_device_timestamp,
)
from lib.helper.metric import get_count_of_metrics, get_metric_names

logger = logging.getLogger(__name__)


def update_graph(n_clicks, device_name: str, metric_name: str):
    logger.info("Updating graph...")
    metrics_list = get_device_metrics_by_name(device_name, metric_name, 1000)

    device_metrics = [
        {"Recorded time": met[0], metric_name: met[1]} for met in metrics_list
    ]
    df = pd.DataFrame(device_metrics, columns=["Recorded time", metric_name])

    return px.line(df, x="Recorded time", y=metric_name)


def update_device_list(n_clicks: int):
    device_names = get_device_names()
    logger.info("Got device names for dropdown: %s", device_names)
    return device_names


def update_metric_list(n_clicks: int, device_name: str):
    metric_names = get_metric_names(device_name)
    logger.info("Got device names for dropdown: %s", metric_names)
    return metric_names


def update_table(
    n_clicks: int,
    page: int,
    page_size: int,
    device_name: str,
    start_date_str: str,
    start_time_str: str,
    end_date_str: str,
    end_time_str: str,
):
    logger.debug("start time: %s start date: %s", start_time_str, start_date_str)
    start_time = datetime.strptime(start_date_str + start_time_str, "%Y-%m-%d%H:%M:%S")
    end_time = datetime.strptime(end_date_str + end_time_str, "%Y-%m-%d%H:%M:%S")
    # page index starts from 0, so we have to increment by one
    metrics_list = get_all_device_metrics(
        device_name,
        start_datetime=start_time,
        end_datetime=end_time,
        page=page + 1,
        page_size=page_size * 2,
    )

    total_metrics = get_count_of_metrics(
        device_name, start_datetime=start_time, end_datetime=end_time
    )
    logger.debug("Total metrics: %s", total_metrics)
    total_pages = total_metrics // page_size
    logger.debug("Total pages: %s", total_pages)

    columns = ["Device", "Recorded time"]
    all_metrics: List[dict[str, Any]] = []

    for i in range(0, len(metrics_list) - 1, 2):
        metrics = [metrics_list[i], metrics_list[i + 1]]

        all_metrics.append(
            {
                "Device": metrics[0][0],
                "Recorded time": metrics[0][1],
                metrics[0][2]: metrics[0][3],
                metrics[1][2]: metrics[1][3],
            }
        )
        if metrics[0][2] not in columns:
            columns.append(metrics[0][2])
        if metrics[1][2] not in columns:
            columns.append(metrics[1][2])
    # all_metrics = [
    #     {"Device": met[0], "Recorded time": met[1], met[2]: met[3]}
    #     for met in metrics_list
    # ]

    df = pd.DataFrame(all_metrics, columns=list(columns))
    return (
        df.to_dict("records"),
        [{"name": col, "id": col} for col in df.columns],
        total_pages,
    )


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
        Output("metric-selection", "options"),
        Input("refresh-metric-names", "n_clicks"),
        Input("device-selection", "value"),
    )(update_metric_list)

    app.callback(
        Output("data-table", "data"),  # Update the table data
        Output("data-table", "columns"),
        Output("data-table", "page_count"),
        # Update the table columns
        Input("update-button", "n_clicks"),
        Input("data-table", "page_current"),
        Input("page-size-dropdown", "value"),
        Input("device-selection", "value"),
        # Trigger on button click
        State("start-date-display", "date"),
        State("start-time-display", "value"),
        State("end-date-display", "date"),
        State("end-time-display", "value"),
    )(update_table)
    logger.info("All callbacks initialized")
