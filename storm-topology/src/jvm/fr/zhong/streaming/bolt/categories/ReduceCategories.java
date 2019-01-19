package fr.zhong.streaming;

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

public class ReduceCategories extends BaseBasicBolt {
  Map<String, Double> sums = new HashMap<String, Double>();

  @Override
  public void execute(Tuple tuple, BasicOutputCollector collector) {
    String category = tuple.getString(0);
    Integer currentSum = tuple.getInteger(1);
    Double sum = currentSum/100.0;
    sums.put(category, sum);
    Gson gsonObj = new Gson();
    String sentence = gsonObj.toJson(sums);
    collector.emit(new Values(sentence));
  }

  @Override
  public void declareOutputFields(OutputFieldsDeclarer declarer) {
    declarer.declare(new Fields("sentence"));
  }
}
