from dash import html, Dash, dcc
from flask import Flask
from d_app.d_callbacks import init_callbacks
import pandas as pd
import plotly.express as px
from lib.helper.device import get_device_names
from lib.helper.metric import get_metric_names
from lib.timed_session import TimedSession
import logging
from lib.models import Device
from sqlalchemy import select

logger = logging.getLogger(__name__)


def init_dash_app(flask_app: Flask) -> Dash:
    # Initialize the Dash app
    d_app = Dash(__name__, server=flask_app, url_base_pathname="/dash/")

    device_names = get_device_names()
    metric_names = get_metric_names()

    # Define the layout
    d_app.layout = [
        html.H1(children="Dashboard", style={"textAlign": "center"}),
        html.Div(
            [
                dcc.Dropdown(device_names, id="device-selection"),
                html.Button("Refresh device list", id="refresh-device-names", n_clicks=0),
            ]
        ),
        html.Div(
            [
                dcc.Dropdown(metric_names, id="metric-selection"),
                html.Button("Refresh metric list", id="refresh-metric-names", n_clicks=0),
            ]
        ),
        html.Button("Submit", id="refresh-graph", n_clicks=0),
        dcc.Graph(id="graph-content"),
    ]

    init_callbacks(d_app)
    return d_app
