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

public class ReduceMetrics extends BaseBasicBolt {
  Map<String, Float> metrics = new HashMap<String, Float>();
  int count = 0;

  @Override
  public void execute(Tuple tuple, BasicOutputCollector collector) {
    String category = tuple.getString(0);
    float value = tuple.getFloat(1);
    metrics.put(category, value);
    count++;
    if(count>20){
      count = 0;
      Gson gsonObj = new Gson();
      String sentence = gsonObj.toJson(metrics);
      collector.emit(new Values(sentence));
    }
  }

  @Override
  public void declareOutputFields(OutputFieldsDeclarer declarer) {
    declarer.declare(new Fields("sentence"));
  }
}
