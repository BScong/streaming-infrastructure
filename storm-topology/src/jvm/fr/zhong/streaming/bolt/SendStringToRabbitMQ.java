package fr.zhong.streaming;

import com.rabbitmq.client.Channel;
import com.rabbitmq.client.Connection;
import com.rabbitmq.client.ConnectionFactory;
import com.rabbitmq.client.DeliverCallback;

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

public class SendStringToRabbitMQ extends BaseBasicBolt {
  Channel _chan;
  String exchangeName;
  String host;
  String queueName;

  public SendStringToRabbitMQ(String host, String exchange){
    this.host = host;
    this.exchangeName = exchange;
  }

  @Override
  public void prepare(Map conf, TopologyContext context) {
      _chan = getRabbitMQChannel(host, exchangeName);
  }


  @Override
  public void execute(Tuple tuple, BasicOutputCollector collector) {
    String sentence = tuple.getString(0);
    try {
        _chan.basicPublish(this.exchangeName, "", null, sentence.getBytes("UTF-8"));
        //System.out.println(" [x] Sent '" + sentence + "'");
    } catch(Exception e){
      _chan = getRabbitMQChannel(host, exchangeName);
      e.printStackTrace();
    }
  }

  @Override
  public void declareOutputFields(OutputFieldsDeclarer declarer) {
  }

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

}
