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


public class SplitCategories extends BaseBasicBolt {
  @Override
  public void execute(Tuple tuple, BasicOutputCollector collector) {
    String sentence = tuple.getString(0);
    try{
      JsonObject jobj = new Gson().fromJson(sentence, JsonObject.class);
      JsonArray products = jobj.get("lines").getAsJsonArray();

      for (JsonElement el : products) {
        JsonObject product = 	el.getAsJsonObject();
        String category = product.get("productCategoryName").getAsString();
        String valueString = product.get("settlementAmount").getAsString();
        int value = Integer.parseInt(valueString.replace(".",""));
        collector.emit(new Values(category, value));
      }
    }
    catch(Exception e){
      e.printStackTrace();
    }
  }

  @Override
  public void declareOutputFields(OutputFieldsDeclarer declarer) {
    declarer.declare(new Fields("category", "value"));
  }
}
