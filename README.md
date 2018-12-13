# Streaming Infrastructure

## Goal
The goal of the project is to build a streaming architecture to process a high amount of cash receipts and provide insights on data using a dashboard.

## Getting started
Install [Docker](https://www.docker.com/get-started) and [Docker Compose](https://docs.docker.com/compose/install/) (automatically installed with Docker in latest versions).
Run `docker-compose up` to run the images (or `docker-compose up -d` in detached mode). Run `docker-compose build` to re-build the images.

If running in detached mode, you can use `docker-compose ps` to see the processes currently running and `docker-compose stop` to stop them.

Useful links: [Docker Compose Getting Started](https://docs.docker.com/compose/gettingstarted/), [Dockerfile reference](https://docs.docker.com/engine/reference/builder/), [Docker Docs](https://docs.docker.com/), [Docker Getting Started](https://docs.docker.com/get-started/).

## Architecture

### Receipts generator
The first task is to generate receipts samples. We use Python for that and a sample of the JSON generated is in [generator/example.json](https://github.com/BScong/streaming-infrastructure/blob/master/generator/example.json). The receipts are then sent to the system entrypoint by an endpoint (REST API).

### Entrypoint
The entrypoint to the system is a REST API deployed on port 3000.
To send a receipt to the system, send a POST request on `localhost:3000/receipt` with the header `Content-Type` set to `application/json`. Then put the receipt JSON as the body.

The API is deployed in Node.js with [Express.js](https://expressjs.com/). We chose that solution because it is easy to implement and very fast (due to the asynchronous nature of Node.js).

### Message broker
For the message broker, we studied different solutions, including RabbitMQ and Apache Kafka.

#### Comparison between Apache Kafka and RabbitMQ

|                         | Apache Kafka                                                                                                       | RabbitMQ                                                                                                                        |
|-------------------------|--------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------|
| Storage                 | Mainly on disk. High amount of values that are store and not consumed immediately.                                 | Mostly on RAM. Works best if values are consumed quickly.                                                                       |
| Routing and logic       | Dumb routing. The clients need to handle the logic (i.e. keeping track of the offset)                              | Complex routing possible. A lot of logic can be handled by RabbitMQ.                                                            |
| Implementation and docs | Young project, few documentation. No official Docker image. For other languages, unofficial clients are available. | Very well documented. An official Docker Image is available and multiple official clients are available in different languages. |
| Dependencies            | Apache Zookeeper                                                                                                   | None                                                                                                                            |
| Scalability             | Horizontal. We can add Kafka nodes.                                                                                | Vertical. We can add more RAM.                                                                                                  |
| Performance             | 100k+ requests/sec                                                                                                 | 20k+ requests/sec (per queue)                                                                                                   |


#### Our choice
We chose to go with RabbitMQ for several reasons:
 - We believe that we must consume data quickly to show real-time analytics, so storage on RAM is better and faster for that usage
 - A basic routing could work for us, but RabbitMQ is better documented and has official Docker images.
 - We like the fact that RabbitMQ keeps track of which message was delivered, and that we won't have to handle that logic.
 - We believe that performance-wise, RabbitMQ is sufficient for our needs.
 - Implementation is made easy for RabbitMQ and docs are complete

#### References
 - [Message-oriented Middleware for Scalable Data Analytics Architectures, NICOLAS NANNONI](http://kth.diva-portal.org/smash/get/diva2:813137/FULLTEXT01.pdf)
 - [Comparatif RabbitMQ / Kafka](https://blog.ippon.fr/2018/03/27/comparatif-rabbitmq-kafka/)
 - [What are the differences between Apache Kafka and RabbitMQ?, Quora](https://www.quora.com/What-are-the-differences-between-Apache-Kafka-and-RabbitMQ)
 - [Understanding When to use RabbitMQ or Apache Kafka, Pivotal](https://content.pivotal.io/blog/understanding-when-to-use-rabbitmq-or-apache-kafka)
 - [Docker image for rabbitmq](https://docs.docker.com/samples/library/rabbitmq/)
 - [RabbitMQ docs](https://www.rabbitmq.com/documentation.html)

#### Implementation
For the implementation, we use [RabbitMQ with Exchanges (Pub/Sub)](https://www.rabbitmq.com/tutorials/tutorial-three-python.html).
We will use several clients, including Python, NodeJS and Java.

For the exchanges, we have:
 - `receipts`: entrypoint for publishing receipts, every receipt JSON is sent on this exchange, and is then consumed by analytics and persistence (database).
 - `count`: published by analytics to increase the current realtime count/sum of receipts, consumed by frontend.
 - `categories`: published by analytics to increase the current realtime count/sum of products for each category. Consumed by frontend.

Some example code for Java and Python are available in the [utils folder](https://github.com/BScong/streaming-infrastructure/tree/master/utils). They are inspired from [RabbitMQ tutorials](https://github.com/rabbitmq/rabbitmq-tutorials).
