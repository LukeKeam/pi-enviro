# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import dash
from dash import Dash, html, dcc
import pandas as pd
import numpy as np
from dash.dependencies import Output, Input
from db_connect import db_create_connection

# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options
# db connect
database = r"data.db"
db_file = database
conn = db_create_connection(db_file)
cur = conn.cursor()

# db get records
data = pd.read_sql("SELECT * FROM enviro ORDER BY id DESC LIMIT 50000", conn)
data.sort_values("datetime", inplace=True)

# site setup
app = dash.Dash(__name__)
server = app.server
app.title = "pi-enviro brought to you by techgeek.biz"

# html
app.layout = dash.dcc.Interval(id='interval', interval=14500)
html.Div(
    children=[
        html.Div(children=[html.H1(children="pi-enviro", className="header-title"),
                           html.P(children="Brought to you by techgeek.biz",
                                  className="header-description", ), ], className="header", ),
        html.Div(children=[
            html.Div(dcc.Graph(figure={"data": [{
                "x": data["datetime"],
                "y": data["temperature"],
                "type": "lines", }, ], "layout": {"title": "temperature"}, }, ), ),
            html.Div(dcc.Graph(figure={"data": [{
                "x": data["datetime"],
                "y": data["pressure"],
                "type": "lines", }, ], "layout": {"title": "pressure"}, }, ), ),
            html.Div(dcc.Graph(figure={"data": [{
                "x": data["datetime"],
                "y": data["humidity"],
                "type": "lines", }, ], "layout": {"title": "humidity"}, }, ), ),
            html.Div(dcc.Graph(figure={"data": [{
                "x": data["datetime"],
                "y": data["light"],
                "type": "lines", }, ], "layout": {"title": "light"}, }, ), ),
            html.Div(dcc.Graph(figure={"data": [{
                "x": data["datetime"],
                "y": data["oxidised"],
                "type": "lines", }, ], "layout": {"title": "oxidised"}, }, ), ),
            html.Div(dcc.Graph(figure={"data": [{
                "x": data["datetime"],
                "y": data["reduced"],
                "type": "lines", }, ], "layout": {"title": "reduced"}, }, ), ),
            html.Div(dcc.Graph(figure={"data": [{
                "x": data["datetime"],
                "y": data["nh3"],
                "type": "lines", }, ], "layout": {"title": "nh3"}, }, ), ),
            html.Div(dcc.Graph(figure={"data": [{
                "x": data["datetime"],
                "y": data["pm1"],
                "type": "lines", }, ], "layout": {"title": "pm1"}, }, ), ),
            html.Div(dcc.Graph(figure={"data": [{
                "x": data["datetime"],
                "y": data["pm25"],
                "type": "lines", }, ], "layout": {"title": "pm25"}, }, ), ),
            html.Div(dcc.Graph(figure={"data": [{
                "x": data["datetime"],
                "y": data["pm10"],
                "type": "lines", }, ], "layout": {"title": "pm10"}, }, ), ),
            html.Div(dcc.Graph(figure={"data": [{
                "x": data["datetime"],
                "y": data["decibels"],
                "type": "lines", }, ], "layout": {"title": "decibels"}, }, ), ),
        ], className="wrapper",
        ),
    ]
)

if __name__ == "__main__":
    app.run_server(debug=True)
