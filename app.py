import datetime

import pandas as pd
import plotly.express as px
from dash import dcc, html, Input, Output, dash

from db_connect import db_create_connection

# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options


# site setup
app = dash.Dash(__name__)
server = app.server
app.title = "pi-enviro brought to you by techgeek.biz"

app.layout = html.Div(children=[html.H1(children="pi-enviro", className="header-title"),
                                html.P(children="Brought to you by techgeek.biz", className="header-description"),
                                html.Div(id='graph-content'),
                                dcc.Interval(id='interval-component', interval=145000),
                                ])


@app.callback(Output('graph-content', 'children'),
              Input('interval-component', 'n_intervals'))
def update_line_chart(n):
    # db connect db get records
    database = r"data.db"
    db_file = database
    conn = db_create_connection(db_file)
    cur = conn.cursor()
    df = pd.read_sql("SELECT * FROM enviro ORDER BY id DESC LIMIT 50000", conn)
    df.sort_values("datetime", inplace=True)
    conn.close()

    temperature = px.line(df, x=df['datetime'], y=df['temperature'])
    pressure = px.line(df, x=df['datetime'], y=df['pressure'])
    humidity = px.line(df, x=df['datetime'], y=df['humidity'])
    light = px.line(df, x=df['datetime'], y=df['light'])
    oxidised = px.line(df, x=df['datetime'], y=df['oxidised'])
    reduced = px.line(df, x=df['datetime'], y=df['reduced'])
    nh3 = px.line(df, x=df['datetime'], y=df['nh3'])
    pm1 = px.line(df, x=df['datetime'], y=df['pm1'])
    pm25 = px.line(df, x=df['datetime'], y=df['pm25'])
    pm10 = px.line(df, x=df['datetime'], y=df['pm10'])
    decibels = px.line(df, x=df['datetime'], y=df['decibels'])
    now = datetime.datetime.now()

    return 'Intervals: {} since: {}:{}:{}'.format(
        n,
        now.hour,
        now.minute,
        now.second
    ), \
           dcc.Graph(figure=temperature), \
           dcc.Graph(figure=pressure), \
           dcc.Graph(figure=humidity), \
           dcc.Graph(figure=light), \
           dcc.Graph(figure=oxidised), \
           dcc.Graph(figure=reduced), \
           dcc.Graph(figure=nh3), \
           dcc.Graph(figure=pm1), \
           dcc.Graph(figure=pm10), \
           dcc.Graph(figure=pm25), \
           dcc.Graph(figure=decibels)


app.run_server(debug=True)
