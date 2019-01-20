import pprint
import datetime
import time
import pika
import json
from pymongo import MongoClient
import requests

client = MongoClient('mongo', 27017)
db = client.receipt_database
collection = db.receipt

db.receipt.delete_many({})
print('Starting...')
time.sleep(10)


print('Started.')
connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
channel = connection.channel()

channel.exchange_declare(exchange='receipts',
                         exchange_type='fanout')
result = channel.queue_declare(exclusive=True)
queue_name = result.method.queue
channel.queue_bind(exchange='receipts',
                   queue=queue_name)

channel.exchange_declare(exchange='metrics-db',
                         exchange_type='fanout')
result = channel.queue_declare(queue = 'api', exclusive=True)
channel.queue_bind(exchange='metrics-db',
                   queue='api')

def callback(ch, method, properties, body):
    collection.insert_one(json.loads(body))
    message = json.loads(body)
    connectionDelay = time.time() - datetime.datetime.strptime(message['date'], '%Y-%m-%d %H:%M:%S').timestamp()
    networkDelay = time.time() - message['receivedTime']
    message["connectionDelay"] = connectionDelay
    message["networkDelay"] = networkDelay
    metrics = {
        'connectionDelay' : connectionDelay,
        'networkDelay' : networkDelay
    }
    metrics = json.dumps(metrics)
    channel.basic_publish(exchange='metrics-db',
                      routing_key='',
                      body=metrics)


channel.basic_consume(callback,
                      queue=queue_name,
                      no_ack=True)

print(' [*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()

