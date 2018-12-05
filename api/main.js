#!/usr/bin/env node
console.log('Starting API...');

var express = require('express')
var app = express();
app.use(express.json())
var amqp = require('amqplib/callback_api');

app.post('/receipt', function(req,res){
  console.log('Received receipt');
  // TODO: add timestamp
  var message = req.body;
  sendReceipt(JSON.stringify(message), 'hello');
  res.sendStatus(200);
});

function sendReceipt(message, queue){
  amqp.connect('amqp://rabbitmq', function(err, conn) {
    conn.createChannel(function(err, ch) {
      ch.assertQueue(queue, {durable: false});
      ch.sendToQueue(queue, new Buffer(message));
      console.log(" [x] Sent message to " + queue);
    });
    setTimeout(function() {conn.close();}, 500);
  });
};

app.listen(3000, () => console.log(`App listening on port 3000!`))
