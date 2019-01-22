import datetime
import json
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly
from dash.dependencies import Input, Output
from concurrent.futures import ThreadPoolExecutor

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

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
    'time': [datetime.datetime.now()],
    'sum': [0],
    'count': 0
}

global data_cat
data_cat = {}

global data_metrics_storm
data_metrics_storm = {
    'averagePerMinute': [0],
    'time': [datetime.datetime.now()],
    'averageMsSystem': 0
}

global data_metrics_db
data_metrics_db = {
    "connectionDelay": 0,
    "networkDelay": 0
}


def updateSum(val):
    if val['count'] > data['count']:
        data['time'].append(datetime.datetime.now())
        data['sum'].append(val['sum'])
        data['count'] = val['count']


def callback(ch, method, properties, body):
    #print(" [x] Received %r" % json.loads(body))
    updateSum(json.loads(body))


def updateCat(category):
    for cat, val in category.items():
        data_cat[cat] = val


def callback_cat(ch, method, properties, body):
    # print(" [x] Received cat %r" % json.loads(body))
    category = json.loads(body)
    updateCat(category)


def updateStorm(data):
    data_metrics_storm['time'].append(datetime.datetime.now())
    data_metrics_storm['averagePerMinute'].append(data['averagePerMinute'])
    data_metrics_storm['averageMsSystem'] = data['averageMsSystem']


def callback_storm(ch, method, properties, body):
    # print(" [x] Received storm %r" % json.loads(body))
    updateStorm(json.loads(body))


def updateDB(data):
    data_metrics_db['connectionDelay'] = data['connectionDelay']
    data_metrics_db['networkDelay'] = data['networkDelay']


def callback_db(ch, method, properties, body):
    updateDB(json.loads(body))


channel.basic_consume(callback, queue_name, no_ack=True)
channel_cat.basic_consume(callback_cat, queue_name_cat, no_ack=True)
channel_metrics_storm.basic_consume(callback_storm, queue_name_metrics_storm, no_ack=True)
channel_metrics_db.basic_consume(callback_db, queue_name_metrics_db, no_ack=True)

colors = {
    'coffee': '#c2ac93',
    'vanilla': '#e9d6c0',
    'text': '#ffffff',
}

app.layout = html.Div(
    html.Div(style={
        'backgroundColor': colors['vanilla']},
        children=[
            html.H1('Bakery Sales Live Feed',
                    style={'backgroundColor': colors['vanilla'],
                           'textAlign': 'center',
                           }),
            html.Div(id='live-update-text',
                     style={'backgroundColor': colors['coffee'],
                            'textAlign': 'center',
                            'color': colors['text']
                            }),
            dcc.Graph(id='live-update-graph', animate=False),
            dcc.Interval(
                id='interval-component',
                interval=1000,  # in milliseconds
                n_intervals=0
            ),

        ])
)


@app.callback(Output('live-update-text', 'children'),
              [Input('interval-component', 'n_intervals')])
def interfaceSum(n):
    style = {'padding': '30px', 'fontSize': '24px'}
    return [
        html.Span('Daily revenue: {}'.format(data['sum'][-1]), style=style),
        html.Span('Number of receipts: {}'.format(data['count']), style=style),
        html.Span('Ingested tickets/minute : {}'.format(data_metrics_storm['averagePerMinute'][-1]), style=style),
        html.Span('Network delay : {:.6f}'.format(data_metrics_db['networkDelay']), style=style)
    ]


@app.callback(Output('live-update-graph', 'figure'),
              [Input('interval-component', 'n_intervals')])
def display(n):
    fig = plotly.tools.make_subplots(rows=2, cols=2, specs=[[{}, {}], [{'colspan': 2}, None]],
                                     subplot_titles=('Revenue',
                                                     'Sales per category',
                                                     'Receipts ingested per minute'))
    # fig['layout']['margin'] = {
    #     'l': 30, 'r': 10, 'b': 30, 't': 10
    # }
    # fig['layout']['legend'] = {'x': 0, 'y': 1, 'xanchor': 'left', 'orientation':'h'}
    fig['layout']['showlegend'] = False
    fig['layout']['height'] = 1000

    fig.append_trace({
        'x': data['time'],
        'y': data['sum'],
        'name': 'Revenue',
        'mode': 'lines+markers',
        'line': {'color': colors['coffee']},
        'type': 'scatter',
    }, 1, 1)

    fig.append_trace({
        'x': list(data_cat.keys()),
        'y': list(data_cat.values()),
        'name': 'Sales Categories',
        'type': 'bar',
        'marker': {'color': colors['coffee']},
    }, 1, 2)

    fig.append_trace({
        'x': data_metrics_storm['time'],
        'y': data_metrics_storm['averagePerMinute'],
        'name': 'Avg receipts ingested/min',
        'mode': 'lines+markers',
        'line': {'color': colors['coffee']},
        'type': 'scatter'
    }, 2, 1)

    fig['layout']['xaxis1'].update(title='Time')
    fig['layout']['yaxis1'].update(title='Total revenue')
    fig['layout']['xaxis2'].update(title='Sales Category')
    fig['layout']['yaxis2'].update(title='Total Sales')
    fig['layout']['xaxis3'].update(title='Time')
    fig['layout']['yaxis3'].update(title='Receipts ingested')

    return fig


def start_multi():
    executor = ThreadPoolExecutor(max_workers=5)
    executor.submit(channel.start_consuming)
    executor.submit(channel_cat.start_consuming)
    executor.submit(channel_metrics_storm.start_consuming)
    executor.submit(channel_metrics_db.start_consuming)
    executor.submit(app.run_server(host='0.0.0.0', debug=True, port=8050))


if __name__ == '__main__':
    start_multi()
