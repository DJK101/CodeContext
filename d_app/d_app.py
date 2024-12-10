from dash import html, Dash, dcc
from flask import Flask
from d_app.d_callbacks import init_callbacks, metrics
import pandas as pd
import plotly.express as px



def init_dash_app(flask_app: Flask) -> Dash:
    # Initialize the Dash app
    d_app = Dash(__name__, server=flask_app, url_base_pathname="/dash/")

    # Define the layout
    d_app.layout = [
        html.H1(children="Dashboard", style={"textAlign": "center"}),
        dcc.Dropdown(metrics.device_id.unique(), "1", id="dropdown-selection"),
        dcc.Graph(id="graph-content"),
    ]

    init_callbacks(d_app)
    return d_app
