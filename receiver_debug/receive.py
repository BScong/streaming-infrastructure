import time
import json
print('Starting...')
time.sleep(15)

import pika
print('Started.')
connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
channel = connection.channel()

channel.exchange_declare(exchange='categories',
                         exchange_type='fanout')
result = channel.queue_declare(exclusive=True)
queue_name = result.method.queue
channel.queue_bind(exchange='categories',
                   queue=queue_name)

def callback(ch, method, properties, body):
    print(" [x] Received %r" % json.loads(body))

channel.basic_consume(callback,
                      queue=queue_name,
                      no_ack=True)

print(' [*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()
