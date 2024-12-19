from dash import html, Dash, dcc, dash_table
from flask import Flask
from d_app.d_callbacks import init_callbacks
from lib.helper.device import get_device_names
from lib.helper.metric import get_metric_names
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


def init_dash_app(flask_app: Flask) -> Dash:
    # Initialize the Dash app
    d_app = Dash(__name__, server=flask_app, url_base_pathname="/dash/")

    device_names = get_device_names()

    # Define the layout
    d_app.layout = [
        html.H1(children="Dashboard", style={"textAlign": "center"}),
        html.Div(
            [
                dcc.Dropdown(device_names, id="device-selection"),
                html.Button(
                    "Refresh device list", id="refresh-device-names", n_clicks=0
                ),
            ]
        ),
        html.Div(
            [
                dcc.Dropdown([], id="metric-selection"),
                html.Button(
                    "Refresh metric list", id="refresh-metric-names", n_clicks=0
                ),
            ]
        ),
        dcc.Dropdown(
            id="graph-limit",
            options=[
                {"label": str(size), "value": size}
                for size in [10, 20, 50, 100, 500, 1000]
            ],
            value=10,  # Default page size
            style={"marginLeft": "10px"},
        ),
        dcc.Graph(id="graph-content"),
        html.Div(
            [
                html.Button("Update Table", id="update-button", n_clicks=0),
                html.Div(
                    [
                        html.Span("Start date and time:"),
                        dcc.DatePickerSingle(
                            id="start-date-display",
                            date=datetime.now().strftime("%Y-%m-%d"),
                            display_format="YYYY-MM-DD",
                            style={"marginLeft": "10px"},
                        ),
                        dcc.Input(
                            id="start-time-display",
                            type="time",
                            value=datetime.now().strftime("%H:%M"),
                            style={"marginLeft": "10px"},
                        ),
                    ],
                    style={"display": "flex", "flexDirection": "column"},
                ),
                html.Div(
                    [
                        html.Span("End date and time:"),
                        dcc.DatePickerSingle(
                            id="end-date-display",
                            date=(datetime.now() - timedelta(days=1)).strftime(
                                "%Y-%m-%d"
                            ),
                            display_format="YYYY-MM-DD",
                            style={"marginLeft": "10px"},
                        ),
                        dcc.Input(
                            id="end-time-display",
                            type="time",
                            value=datetime.now().strftime("%H:%M"),
                            style={"marginLeft": "10px"},
                        ),
                    ],
                    style={"display": "flex", "flexDirection": "column"},
                ),
                dcc.Dropdown(
                    id="page-size-dropdown",
                    options=[
                        {"label": str(size), "value": size}
                        for size in [10, 20, 50, 100]
                    ],
                    value=10,  # Default page size
                    style={"marginLeft": "10px"},
                ),
            ],
            style={"display": "flex", "alignItems": "center"},
        ),
        dash_table.DataTable(
            id="data-table",
            page_action="custom",
            page_current=0,
            page_size=10,
        ),
        html.Button("Agent Action", id="agent-action", n_clicks=0),
    ]
    init_callbacks(d_app)
    return d_app
