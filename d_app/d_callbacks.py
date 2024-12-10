from dash import Dash, Output, Input
import plotly.express as px
import pandas as pd

metrics_dict = {
    "device_id": [1, 1, 1],
    "disk_usage": [10, 97777127424, 97777127424],
    "id": [1, 2, 3],
    "ram_usage": [10, 7100694528, 7141351424],
    "recorded_time": [
        "2024-12-09T14:46:15.043000",
        "2024-12-09T14:46:47.833851",
        "2024-12-09T14:46:49.887812",
    ],
}
metrics = pd.DataFrame.from_dict(metrics_dict)


def update_graph(value: int):
    dff = metrics[metrics.device_id == value]
    return px.line(dff, x="recorded_time", y="ram_usage")


def init_callbacks(app: Dash):
    app.callback(
        Output("graph-content", "figure"), Input("dropdown-selection", "value")
    )(update_graph)
