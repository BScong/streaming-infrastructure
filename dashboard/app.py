import datetime
import json

from time import sleep

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly
from dash.dependencies import Input, Output
#import numpy as np
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
#from flask_caching import Cache


external_stylesheets = [
    # Dash CSS
    'https://codepen.io/chriddyp/pen/bWLwgP.css',
    # Loading screen CSS
    'https://codepen.io/chriddyp/pen/brPBPO.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
# cache = Cache(app.server, config={
#     'CACHE_TYPE': 'filesystem',
#     'CACHE_DIR': 'cache-directory'
# })
# TIMEOUT = 60

#cache.init_app(app.server, config=CACHE_CONFIG)

import pika
print('Started.')



def get_channel(exchange_name):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
    channel = connection.channel()
    channel.exchange_declare(exchange=exchange_name,
                             exchange_type='fanout')
    result = channel.queue_declare(exclusive=True)
    queue_name = result.method.queue
    channel.queue_bind(exchange=exchange_name,
                       queue=queue_name)
    return channel, queue_name

channel, queue_name = get_channel('count')
channel_cat, queue_name_cat = get_channel('categories')
channel_metrics_storm, queue_name_metrics_storm = get_channel('metrics-storm')
channel_metrics_db, queue_name_metrics_db = get_channel('metrics-db')

global data
data = {
        'time':[datetime.datetime.now()],
        'sum': [0],
        'count': 0
}

global data_cat
data_cat = {}


example_metrics_storm = {
    "averageMsSystem":0,
    "averageMsCreation":0,
    "averagePerMinute":0
}
example_metrics_db = {
    "connectionDelay":0,
    "networkDelay":0
}

global data_metrics_storm
data_metrics_storm = {
    'averagePerMinute': [0],
    'time':[datetime.datetime.now()],
    'averageMsSystem': 0
}


global data_metrics_db


def updateSum(val):
    if val['count']>data['count']:
        data['time'].append(datetime.datetime.now())
        data['sum'].append(val['sum'])
        data['count'] = val['count']


def callback(ch, method, properties, body):
    print(" [x] Received %r" % json.loads(body))
    updateSum(json.loads(body))

channel.basic_consume(callback, queue_name, no_ack=True)



def updateCat(category):
    for cat, val in category.items():
        data_cat[cat] = val



def callback_cat(ch, method, properties, body):
    #print(" [x] Received cat %r" % json.loads(body))
    category = json.loads(body)
    updateCat(category)

channel_cat.basic_consume(callback_cat, queue_name_cat, no_ack=True)

def updateStorm(data):
    data_metrics_storm['time'].append(datetime.datetime.now())
    data_metrics_storm['averagePerMinute'].append(data['averagePerMinute'])
    data_metrics_storm['averageMsSystem'] = data['averageMsSystem']


def callback_storm(ch, method, properties, body):
    #print(" [x] Received storm %r" % json.loads(body))
    updateStorm(json.loads(body))

channel_metrics_storm.basic_consume(callback_storm,queue_name_metrics_storm, no_ack=True)


app.layout = html.Div(
    html.Div([
        html.H4('Sales Live Feed'),
        html.Div(id='live-update-text'),
        dcc.Graph(id='live-update-graph',animate=True),
        dcc.Interval(
            id='interval-component-graph',
            interval=2000, # in milliseconds
            n_intervals=0
        ),
        dcc.Interval(
            id='interval-component',
            interval=1000, # in milliseconds
            n_intervals=0
        ),


    ])

)

@app.callback(Output('live-update-text', 'children'),
              [Input('interval-component', 'n_intervals')])
def interfaceSum(n):
    #data = np.load('dataSum.npy').item()
    style = {'padding': '20px', 'fontSize': '24px'}
    return [
        html.Span('Daily revenue: {}'.format(data['sum'][-1]), style=style),
        html.Span('Number of receipts: {}'.format(data['count']), style=style),
        html.Span('Average ingested/min : {}'.format(data_metrics_storm['averagePerMinute'][-1]), style=style)

    ]

@app.callback(Output('live-update-graph', 'figure'),
               [Input('interval-component', 'n_intervals')])
def display(n):
    #data_cat = np.load('dataCat.npy').item()
    #print(data_cat)
    fig = plotly.tools.make_subplots(rows=2, cols=2, vertical_spacing=0.2)
    fig['layout']['margin'] = {
        'l': 30, 'r': 10, 'b': 30, 't': 30
    }
    fig['layout']['legend'] = {'x': 1, 'y': 0, 'xanchor': 'right'}

    fig.append_trace({
        'x': data['time'],
        'y': data['sum'],
        'name': 'Chiffre d\'affaire',
        'mode': 'lines+markers',
        'type': 'scatter'
    }, 1, 1)


    fig.append_trace({
        'x': list(data_cat.keys()),
        'y': list(data_cat.values()),
        'name': 'Sales Categories',
        'type': 'bar'
    }, 2, 1)

    fig.append_trace({
        'x': data_metrics_storm['time'],
        'y': data_metrics_storm['averagePerMinute'],
        'name': 'Avg receipts ingested/min',
        'mode': 'lines+markers',
        'type': 'scatter'
    }, 1, 2)

    return fig


def start_multi():
    executor = ThreadPoolExecutor(max_workers=4)

    executor.submit(channel.start_consuming)
    executor.submit(channel_cat.start_consuming)
    executor.submit(channel_metrics_storm.start_consuming)
    executor.submit(app.run_server(host='0.0.0.0',debug=True, port=8050))

if __name__ == '__main__':
    start_multi()
