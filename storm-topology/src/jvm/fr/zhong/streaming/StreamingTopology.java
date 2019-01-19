/**
 * Inspired by Apache Storm Starter Examples
 * https://github.com/apache/storm/tree/master/examples/storm-starter
 */
package fr.zhong.streaming;

import fr.zhong.streaming.*;

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

public class StreamingTopology {
  public static void kill(Nimbus.Client client, String name) throws Exception {
    KillOptions opts = new KillOptions();
    opts.set_wait_secs(0);
    client.killTopologyWithOpts(name, opts);
  }

  public static void main(String[] args) throws Exception {

    TopologyBuilder builder = new TopologyBuilder();

    builder.setSpout("spout", new RabbitMQSpout("rabbitmq", "receipts"), 4);

    builder.setBolt("sum", new ExtractSum(), 2).shuffleGrouping("spout");
    builder.setBolt("reduceSum", new ReduceSum(), 1).shuffleGrouping("sum");
    builder.setBolt("sendSum", new SendStringToRabbitMQ("rabbitmq","count"), 1).shuffleGrouping("reduceSum");

    builder.setBolt("splitCategories", new SplitCategories(), 2).shuffleGrouping("spout");
    builder.setBolt("sumCategories", new SumCategories(), 4).fieldsGrouping("splitCategories", new Fields("category"));
    builder.setBolt("reduceCategories", new ReduceCategories(), 1).shuffleGrouping("sumCategories");
    builder.setBolt("sendCategories", new SendStringToRabbitMQ("rabbitmq","categories"), 1).shuffleGrouping("reduceCategories");


    Config conf = new Config();
    conf.registerMetricsConsumer(org.apache.storm.metric.LoggingMetricsConsumer.class);

    String name = "StreamingTopology";
    if (args != null && args.length > 0) {
        name = args[0];
    }

    conf.setNumWorkers(1);
    StormSubmitter.submitTopologyWithProgressBar(name, conf, builder.createTopology());

    Map clusterConf = Utils.readStormConfig();
    clusterConf.putAll(Utils.readCommandLineOpts());
    Nimbus.Client client = NimbusClient.getConfiguredClient(clusterConf).getClient();
  }
}
