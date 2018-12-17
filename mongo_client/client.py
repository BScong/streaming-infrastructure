import pprint
import datetime
import time
import pika
import json
from pymongo import MongoClient

client = MongoClient('mongo', 27017)
db = client.receipt_database
collection = db.receipt

print('Starting...')
time.sleep(15)


print('Started.')
connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
channel = connection.channel()

channel.exchange_declare(exchange='receipts',
                         exchange_type='fanout')
result = channel.queue_declare(exclusive=True)
queue_name = result.method.queue
channel.queue_bind(exchange='receipts',
                   queue=queue_name)


def callback(ch, method, properties, body):
    collection.insert_one(json.loads(body))
    pprint.pprint(collection.count_documents({}))


channel.basic_consume(callback,
                      queue=queue_name,
                      no_ack=True)

print(' [*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()



'''
post = {"author": "Mike","text": "My first blog post!","tags": ["mongodb", "python", "pymongo"], "date": datetime.datetime.utcnow()}
collection.insert_one(post)

pprint.pprint(collection.find_one())
'''