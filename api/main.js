// Kudos to https://github.com/carlhoerberg
// Taken from https://gist.github.com/carlhoerberg/006b01ac17a0a94859ba

var amqp = require('amqplib/callback_api');
console.log('Starting API...');
var express = require('express')
var app = express();
app.use(express.json())

// if the connection is closed or fails to be established at all, we will reconnect
var amqpConn = null;
function start() {
  amqp.connect('amqp://rabbitmq' + "?heartbeat=60", function(err, conn) {
    if (err) {
      console.error("[AMQP]", err.message);
      return setTimeout(start, 1000);
    }
    conn.on("error", function(err) {
      if (err.message !== "Connection closing") {
        console.error("[AMQP] conn error", err.message);
      }
    });
    conn.on("close", function() {
      console.error("[AMQP] reconnecting");
      return setTimeout(start, 1000);
    });

    console.log("[AMQP] connected");
    amqpConn = conn;

    whenConnected();
  });
}

function whenConnected() {
  startPublisher();
}

var pubChannel = null;
var offlinePubQueue = [];
function startPublisher() {
  amqpConn.createConfirmChannel(function(err, ch) {
    if (closeOnErr(err)) return;
    ch.on("error", function(err) {
      console.error("[AMQP] channel error", err.message);
    });
    ch.on("close", function() {
      console.log("[AMQP] channel closed");
    });

    pubChannel = ch;
    while (true) {
      var m = offlinePubQueue.shift();
      if (!m) break;
      publish(m[0], m[1], m[2]);
    }
  });
}

// method to publish a message, will queue messages internally if the connection is down and resend later
function publish(exchange, routingKey, content) {
  try {
    pubChannel.publish(exchange, routingKey, content, { persistent: true },
                       function(err, ok) {
                         if (err) {
                           console.error("[AMQP] publish", err);
                           offlinePubQueue.push([exchange, routingKey, content]);
                           pubChannel.connection.close();
                           return setTimeout(start, 1000);
                         }
                       });
  } catch (e) {
    console.error("[AMQP] publish", e.message);
    offlinePubQueue.push([exchange, routingKey, content]);
    return setTimeout(start, 1000);
  }
}

function closeOnErr(err) {
  if (!err) return false;
  console.error("[AMQP] error", err);
  amqpConn.close();
  return true;
}

start();
var count = 0
app.post('/receipt', function(req,res){
  count++;
  /*if(count%20==0){
    console.log('Receipts received: ' + count);
  }*/
  // TODO: add timestamp
  var message = req.body;
  message.receivedTime = new Date().getTime()/1000;
  publish('receipts','',new Buffer(JSON.stringify(message)));
  res.sendStatus(200);
});

app.listen(3000, () => console.log(`App listening on port 3000!`))
