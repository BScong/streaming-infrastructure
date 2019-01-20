import datetime
import json

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


connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()
channel.exchange_declare(exchange='count',
                         exchange_type='fanout')
result = channel.queue_declare(exclusive=True)
queue_name = result.method.queue
channel.queue_bind(exchange='count',
                   queue=queue_name)

channel_cat = connection.channel()
channel_cat.exchange_declare(exchange='categories',
                       exchange_type='fanout')

cat = channel_cat.queue_declare(exclusive=True)
queue_name_cat = cat.method.queue
channel_cat.queue_bind(exchange='categories',
                   queue=queue_name_cat)

categories = ['Alimentation','Boissons','Cigarettes','DepotVentes','Confiseris','FranceTelecom','Grattage','Jounaux','Jouets','Jeux','Librairie','Loto',
              'Papetrie','Piles','Paysafecard','PCS','Plans','Photocopies','TabacaRouler','Tabletterie','TicketsPremium','TimbresFiscaux','TimbresPoste','Telephonie','Transcash','UniversalMobile',
              'Carterie','Cdiscount','Intercall','Kertel','P.Q.N.','P.Q.R.','SFR','DeveloppementPhotos','Publications','Pains']
#
global data

data = {
        'time':[datetime.datetime.now()],
        'sum': [0]
}

global data_cat
data_cat = dict((i,0) for i in categories)


def updateSum(val):
    data['time'].append(datetime.datetime.now())
    data['sum'].append(val['sum'])
    print(data)
    #np.save('dataSum',data)


def callback(ch, method, properties, body):
    #print(" [x] Received %r" % json.loads(body))
    updateSum(json.loads(body))

channel.basic_consume(callback, queue_name, no_ack=True)



def updateCat(category):
    for cat, val in category.items():
        data_cat[cat] = val
    #print(data_cat)
    #df = pd.DataFrame.from_dict(data_cat)
    #print(df)


def callback_cat(ch, method, properties, body):
    #print(" [x] Received cat %r" % json.loads(body))
    category = json.loads(body)
    updateCat(category)

channel_cat.basic_consume(callback_cat, queue_name_cat, no_ack=True)


app.layout = html.Div(
    html.Div([
        html.H4('Sales Live Feed'),
        html.Div(id='live-update-text'),
        dcc.Graph(id='live-update-graph'),
        dcc.Interval(
            id='interval-component',
            interval=1000, # in milliseconds
            n_intervals=0
        )
    ])
)

@app.callback(Output('live-update-text', 'children'),
              [Input('interval-component', 'n_intervals')])
def interfaceSum(n):
    #data = np.load('dataSum.npy').item()
    style = {'padding': '5px', 'fontSize': '16px'}
    return [
        html.Span('Chiffre d\'affaire: {}'.format(data['sum'][-1]), style=style)
    ]

@app.callback(Output('live-update-graph', 'figure'),
              [Input('interval-component', 'n_intervals')])
def display(n):
    #data_cat = np.load('dataCat.npy').item()
    print(data_cat)
    fig = plotly.tools.make_subplots(rows=2, cols=1, vertical_spacing=0.2)
    fig['layout']['margin'] = {
        'l': 30, 'r': 10, 'b': 30, 't': 10
    }
    fig['layout']['legend'] = {'x': 0, 'y': 1, 'xanchor': 'left'}

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
    return fig


def start_multi():
    executor = ThreadPoolExecutor(max_workers=3)

    executor.submit(channel_cat.start_consuming)
    executor.submit(channel.start_consuming)
    executor.submit(app.run_server(debug=True))

if __name__ == '__main__':
    start_multi()
    #app.run_server(debug=True)

