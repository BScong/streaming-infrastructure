public class RandomDigitSpout extends BaseRichSpout
{
  // To output tuples from spout to the next stage bolt
  SpoutOutputCollector collector;

  public void nextTuple()
  {
    int randomDigit = ThreadLocalRandom.current().nextInt(0, 10);

    // Emit the digit to the next stage bolt
    collector.emit(new Values(randomDigit));
  }

  public void declareOutputFields(OutputFieldsDeclarer outputFieldsDeclarer)
  {
    // Tell Storm the schema of the output tuple for this spout.
    // It consists of a single column called 'random-digit'.
    outputFieldsDeclarer.declare(new Fields("random-digit"));
  }
}
