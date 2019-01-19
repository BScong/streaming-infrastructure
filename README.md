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

### Apache Storm

#### Debugging

Run `docker-compose build` to build.
Run `docker-compose -f docker-compose_b.yml up --scale storm-supervisor=3` to run with 3 supervisors.
When everything is running, UI should be available at localhost:8080.

To deploy a jar:
 - Generate jar locally from `/storm-topology` with `mvn clean install` and `mvn package`. Copy the jar in `storm-submit/topology-jar`.
 - SSH into storm-submit: Find the storm-submit container id with `docker ps` then execute `docker exec -it STORM-SUBMIT-ID bash`.
 - In the container, `cd ../topology-jar`
 - Import the jar: `storm jar /topology-jar/streaming-topology-1.2.2.jar fr.zhong.streaming.StreamingTopology StreamingTopology` (syntax: `storm jar JAR_PATH TOPOLOGY_CLASS NAME`) or you can also run `./import.sh`
 - Refresh localhost:8080 and topology should appear and be running.

### Storage of the data
For the database we studied solutions such as MongoDB and Hadoop.

#### Comparison between MongoDB and Hadoop

|                         | Hadoop                                                                                                       | MongoDB                                                                                                                        |
|-------------------------|--------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------|
| Design                 | It is designed to replace RDBMS systems, to process and analyse huge volumes of data.                                 | It is a framework comprised of a software ecosystem, not basically meant to replace RDBMS systems but more as a complement help in archiving data.                                                                       |
| Strength       | Robust and flexible solution.                              | Excels in multi-threaded distribution.                                                            |
| Stotage Format | Stores data in collections, in binary JSON format.  | Stores data in any format. |
| Memory Handling            | Efficient because it is written in C++.                                                                                                   | Better ability to optimize space utilisation.                                                                                                                            |
| Use cases             | More popular for real-time data needs.                                                                                | Efficient for batch jobs.                                                                                                  |

#### Our choice
MongoDB seemed to be a better bet in our case:
 - Firstly, although they are both databases MongoDB is designed to replace RDBMS, while Hadoop acts more as a supplement to help process big volumes of data.  
 - In our case, we need a simple and robust solution to store our data, without the need of a lot of processing.
 - The receipts are already generated in JSON so it suits well Mongo's format.
 - We are not handling huge amounts of data at once, so we don't particularly need efficient batch performance but more of a real-time solution.
 - MongoDB is more simple to use, and in our case we don't need a complex solution but only basic features.


#### References
 - [Hadoop Vs. MongoDB: Which Platform is Better for Handling Big Data?](https://aptude.com/blog/entry/hadoop-vs-mongodb-which-platform-is-better-for-handling-big-data/)
 - [Find Out The 9 Best Comparison Between Hadoop vs MongoDB](https://www.educba.com/hadoop-vs-mongodb/)
 - [Apache Hadoop vs MongoDB: Which Is More Secure?](https://www.upguard.com/articles/apache-hadoop-vs.-mongodb-which-is-more-secure)
 
