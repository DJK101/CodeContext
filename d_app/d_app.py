from dash import html, Dash, dcc
from flask import Flask
from d_app.d_callbacks import init_callbacks
import pandas as pd
import plotly.express as px
from lib.timed_session import TimedSession
import logging
from lib.models import Device
from sqlalchemy import select

logger = logging.getLogger(__name__)


def init_dash_app(flask_app: Flask) -> Dash:
    # Initialize the Dash app
    d_app = Dash(__name__, server=flask_app, url_base_pathname="/dash/")

    device_names: list[str]
    with TimedSession("get_device_names") as session:
        logger.info("Getting device names for dropdown")
        stmt = select(Device.name).distinct()
        device_names = list(session.execute(stmt).scalars().all())
        logger.debug("List of devices: %s", device_names)

    # Define the layout
    d_app.layout = [
        html.H1(children="Dashboard", style={"textAlign": "center"}),
        dcc.Dropdown(device_names, "DJ-Legion", id="dropdown-selection"),
        dcc.Graph(id="graph-content"),
    ]

    init_callbacks(d_app)
    return d_app
