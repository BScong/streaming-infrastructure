package fr.zhong.streaming;

import com.rabbitmq.client.Channel;
import com.rabbitmq.client.Connection;
import com.rabbitmq.client.ConnectionFactory;
import com.rabbitmq.client.DeliverCallback;
import com.rabbitmq.client.GetResponse;

import org.apache.storm.Config;
import org.apache.storm.StormSubmitter;
import org.apache.storm.generated.*;
import org.apache.storm.spout.SpoutOutputCollector;
import org.apache.storm.task.TopologyContext;
import org.apache.storm.topology.BasicOutputCollector;
import org.apache.storm.topology.IRichBolt;
import org.apache.storm.topology.OutputFieldsDeclarer;
import org.apache.storm.topology.TopologyBuilder;
import org.apache.storm.topology.base.BaseBasicBolt;
import org.apache.storm.topology.base.BaseRichSpout;
import org.apache.storm.tuple.Fields;
import org.apache.storm.tuple.Tuple;
import org.apache.storm.tuple.Values;
import org.apache.storm.utils.NimbusClient;
import org.apache.storm.utils.Utils;

import com.google.gson.*;

import java.util.Map;
import java.util.HashMap;
import java.util.Random;
import java.util.concurrent.ThreadLocalRandom;

public class RabbitMQSpout extends BaseRichSpout {
  SpoutOutputCollector _collector;
  Random _rand;
  Channel _chan;
  String exchangeName;
  String host;
  String queueName;
  boolean autoAck = true;

  public Channel getRabbitMQChannel(String host, String s){
    try{

      ConnectionFactory factory = new ConnectionFactory();
      factory.setHost(host);
      //factory.setAutomaticRecoveryEnabled(true);
      Connection connection = factory.newConnection();
      Channel channel = connection.createChannel();
      channel.exchangeDeclare(s, "fanout");
      this.queueName = channel.queueDeclare().getQueue();
      channel.queueBind(this.queueName, s, "");
      System.out.println("Connected");
      return channel;
    } catch(Exception e){
      e.printStackTrace();
    }
    return null;
  }

  RabbitMQSpout(String host, String exchange)
   {
      this.host = host;
      this.exchangeName = exchange;

   }

  @Override
  public void open(Map conf, TopologyContext context, SpoutOutputCollector collector) {
    _collector = collector;
    _rand = ThreadLocalRandom.current();
    _chan = getRabbitMQChannel(host, exchangeName);
  }

  @Override
  public void nextTuple() {
    try {
      if(!_chan.isOpen()){
        _chan = getRabbitMQChannel(host, exchangeName);
      }
      GetResponse response = _chan.basicGet(this.queueName, this.autoAck);
      if (response == null) {
          // No message retrieved.
      } else {
          //AMQP.BasicProperties props = response.getProps();
          String message = new String(response.getBody(), "UTF-8");
          long deliveryTag = response.getEnvelope().getDeliveryTag();
          _collector.emit(new Values(message));
      }
    } catch(Exception e){
      try{
       Thread.sleep(2 * 1000);
     }catch(Exception ex){}
       _chan = getRabbitMQChannel(host, exchangeName);
       e.printStackTrace();
    }
  }

  @Override
  public void ack(Object id) {
      //Ignored
  }

  @Override
  public void fail(Object id) {
    // Ignored
    // _collector.emit(new Values(id), id);
  }

  @Override
  public void declareOutputFields(OutputFieldsDeclarer declarer) {
    declarer.declare(new Fields("sentence"));
  }
}
