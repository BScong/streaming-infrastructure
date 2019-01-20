package fr.zhong.streaming;

import org.apache.storm.Config;
import org.apache.storm.StormSubmitter;
import org.apache.storm.generated.*;
import org.apache.storm.spout.SpoutOutputCollector;
import org.apache.storm.task.TopologyContext;
import org.apache.storm.task.OutputCollector;
import org.apache.storm.topology.BasicOutputCollector;
import org.apache.storm.topology.IRichBolt;
import org.apache.storm.topology.OutputFieldsDeclarer;
import org.apache.storm.topology.TopologyBuilder;
import org.apache.storm.topology.base.BaseWindowedBolt;
import org.apache.storm.topology.base.BaseWindowedBolt.Duration;
import org.apache.storm.topology.base.BaseBasicBolt;
import org.apache.storm.topology.base.BaseRichSpout;
import org.apache.storm.windowing.TupleWindow;
import org.apache.storm.tuple.Fields;
import org.apache.storm.tuple.Tuple;
import org.apache.storm.tuple.Values;
import org.apache.storm.utils.NimbusClient;
import org.apache.storm.utils.Utils;

import com.google.gson.*;

import java.util.Map;
import java.util.HashMap;
import java.util.List;

import java.text.ParseException;
import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.util.Calendar;
import java.util.Date;

public class TimeBolt extends BaseWindowedBolt {
      private OutputCollector collector;

      @Override
      public void prepare(Map stormConf, TopologyContext context, OutputCollector collector) {
          this.collector = collector;
      }

      @Override
      public void execute(TupleWindow inputWindow) {
          int sum = 0;
          List<Tuple> tuplesInWindow = inputWindow.get();
          long averageMsCreation = 0;
          long averageMsSystem = 0;
          Date nowDate = new Date();
          long now = nowDate.getTime();
          int count = tuplesInWindow.size();
          if (tuplesInWindow.size() > 0) {
              for (Tuple tuple : tuplesInWindow) {
                try{
                    String sentence = tuple.getString(0);
                    JsonObject jobj = new Gson().fromJson(sentence, JsonObject.class);
                    String dateString = jobj.get("date").getAsString();
                    long dateSystem = jobj.get("receivedTime").getAsLong()*1000;

                    DateFormat df = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");
                    Date date = df.parse(dateString);
                    long millis = date.getTime();

                    averageMsCreation += now-millis;
                    averageMsSystem += now-dateSystem;
                  } catch(Exception e){
                    count-=1;
                    e.printStackTrace();
                  }
              }
              collector.emit(new Values("averageMsCreation", averageMsCreation/(float)count));
              collector.emit(new Values("averageMsSystem", averageMsSystem/(float)count));

          }
      }

      @Override
      public void declareOutputFields(OutputFieldsDeclarer declarer) {
          declarer.declare(new Fields("metric","value"));
      }
  }
