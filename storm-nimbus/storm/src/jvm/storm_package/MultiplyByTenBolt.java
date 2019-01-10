public class MultiplyByTenBolt extends BaseRichBolt
{
  OutputCollector collector;

  public void execute(Tuple tuple)
  {
    // Get 'even-digit' from the tuple.
    int evenDigit = tuple.getInt(0);

    collector.emit(new Values(evenDigit * 10));
  }

  public void declareOutputFields(OutputFieldsDeclarer declarer)
  {
    declarer.declare(new Fields("even-digit-multiplied-by-ten"));
  }
}
