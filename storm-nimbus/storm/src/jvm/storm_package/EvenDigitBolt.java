public class EvenDigitBolt extends BaseRichBolt
{
  // To output tuples from this bolt to the next bolt.
  OutputCollector collector;

  public void execute(Tuple tuple)
  {
    // Get the 1st column 'random-digit' from the tuple
    int randomDigit = tuple.getInt(0);

    if (randomDigit % 2 == 0) {
      collector.emit(new Values(randomDigit));
    }
  }

  public void declareOutputFields(OutputFieldsDeclarer declarer)
  {
    // Tell Storm the schema of the output tuple for this bolt.
    // It consists of a single column called 'even-digit'
    declarer.declare(new Fields("even-digit"));
  }
}
