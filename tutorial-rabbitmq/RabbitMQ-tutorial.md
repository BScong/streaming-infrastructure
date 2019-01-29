# RabbitMQ tutorial

## What is RabbitMQ?
RabbitMQ is the most widely deployed open source message broker.
A message broker is used as a communication mean inside a system. It can be used to exchange, to route messages and data over a network in an asynchronous manner.

## RabbitMQ features
RabbitMQ has the typical message broker asynchronous messaging system. RabbitMQ implements the AMQP (Advanced Message Queuing Protocol), which is a standard already widely used by multiple librairies.

Due to the open source nature of RabbitMQ, it is also fairly easy to develop and to add plugins to RabbitMQ. Management and monitoring tools can also be added to RabbitMQ. It also has an extensive developer community and multiple languages are supported (Java, .NET, PHP, Python, JavaScript, Ruby, Go…).

An Enterprise version and Cloud-ready version are also available, supported by Pivotal which is the main company behind RabbitMQ.

High availability and high throughput can be achieved by deploying distributed versions of RabbitMQ, with several clusters.

## Comparison between Apache Kafka and RabbitMQ

|                         | Apache Kafka                                                                                                       | RabbitMQ                                                                                                                        |
|-------------------------|--------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------|
| Storage                 | Mainly on disk. High amount of values that are store and not consumed immediately.                                 | Mostly on RAM. Works best if values are consumed quickly.                                                                       |
| Routing and logic       | Dumb routing. The clients need to handle the logic (i.e. keeping track of the offset)                              | Complex routing possible. A lot of logic can be handled by RabbitMQ.                                                            |
| Implementation and docs | Young project, few documentation. No official Docker image. For other languages, unofficial clients are available. | Very well documented. An official Docker Image is available and multiple official clients are available in different languages. |
| Dependencies            | Apache Zookeeper                                                                                                   | None                                                                                                                           
| Performance             | 100k+ requests/sec                                                                                                 | 20k+ requests/sec (per queue)                                                                                                   |

## RabbitMQ server deployment
### Classic installation
The installation is very easy and instructions are available on [RabbitMQ website](https://www.rabbitmq.com/).

Following instructions are for installing and starting RabbitMQ on MacOS with Brew (package manager):
```
brew update
brew install rabbitmq
rabbitmq-server
```
### Docker deployment
Docker deployment is even easier. The Dockerfile is only one line:
```
FROM rabbitmq:3.7.8
```

## Getting Started
RabbitMQ client librairies are available in multiple languages. This tutorial will focus on Python 3.
This tutorial will present how to deploy a Pub/Sub type architecture as presented in the following figure.

![Pub/Sub Architecture](pubsub.png)

This architecture is useful for our use case. We receive a lot of receipts that we publish to RabbitMQ. Some clients then subscribe to this exchange to store them or to generate realtime analytics on them.

### Connection to RabbitMQ
The Python Client for RabbitMQ is `pika`. To install `pika`, type `pip install pika`.

To connect to RabbitMQ and open a channel:
```python
import pika

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
```

To disconnect:
```python
connection.close()
```

### Exchange declaration
To publish or consume messages from RabbitMQ, we have to declare an exchange (node marked with `X` in the figure).

```python
channel.exchange_declare(exchange='receipts',exchange_type='fanout')
```

### Produce messages
You can produce and send messages to an exchange with a simple line:
```python
message = "{'amount':7.99}"
channel.basic_publish(exchange='receipts',routing_key='',body=message)
```

### Consume messages
To consume messages from an exchange, we first have to define queues from which we will consume. An exchange with the `fanout` type will send messages to all the queues linked to this exchange.

We can let RabbitMQ chose a random and unique queue name for us:
```python
result = channel.queue_declare(exclusive=True)
queue_name = result.method.queue
```

Then, we can bind this queue to our channel:
```python
channel.queue_bind(exchange='receipts', queue=queue_name)
```

To consume messages, we have to define a callback function, which will be called each time a message is received. Here, we will just print the message:
```python
def callback(ch, method, properties, body):
    print(" [x] Received: %r" % json.loads(body))
```

We can then bind the callback to the consumer and start consuming:
```python
channel.basic_consume(callback, queue=queue_name, no_ack=True)

channel.start_consuming()
```

## Putting it all together

### Producer code

```python
import pika

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.exchange_declare(exchange='receipts',
                         exchange_type='fanout')

message = "{'amount':7.99}"
channel.basic_publish(exchange='receipts',
                      routing_key='',
                      body=message)

connection.close()
```

### Consumer code

```python
import pika
import json

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.exchange_declare(exchange='receipts', exchange_type='fanout')

result = channel.queue_declare(exclusive=True)
queue_name = result.method.queue

channel.queue_bind(exchange='logs', queue=queue_name)

def callback(ch, method, properties, body):
    print(" [x] Received: %r" % json.loads(body))

channel.basic_consume(callback, queue=queue_name, no_ack=True)

channel.start_consuming()
```

## Advanced features
Advanced features are available with RabbitMQ, such as:
 - Routing and Topics: messages can be routed to different nodes

![Routing](direct-exchange.png)
![Topics](topics.png)
 - Request/Reply architecture. Queues can be used to build an architecture requiring a reply from the Consumer
![Request/Reply](request-reply.png)
 - Authentication and Authorisation
 - Monitoring
 - Clustering

## Conclusion
As we saw in this tutorial, RabbitMQ is a lightweight message broker and very easy to deploy.

The basic functions of a message broker are easy to implement. The big community, the number of languages supported make a great developer experience.

For advanced use cases, advanced features are available and plugins can be added. They can also be developed for RabbitMQ as it is open source. Scalability and high availability are also possible with RabbitMQ, they can be achieved with a distributed deployment and clustering.

## References
Documentation and RabbitMQ website: [rabbitmq.com](https://www.rabbitmq.com).

Images from [rabbitmq.com](https://www.rabbitmq.com).
