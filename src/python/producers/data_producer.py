import logging, random, uuid, json, time
from datetime import datetime, timezone
from confluent_kafka import Producer

logging.basicConfig(
    level = logging.INFO,
    format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# --- Kafka Producer Configuration (Placeholder) ---
KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"
KAFKA_TOPIC = "raw_stock_ticks"

class Stock:
    """A stateful class to represent and simulate a single stock's trading behavior."""
    def __init__(self, ticker: str, initial_price: float, issued_shares_crore: float):
        self.ticker = ticker
        self.price = initial_price
        self.issued_shares = issued_shares_crore
        self.last_update = datetime.now(timezone.utc)

    def generate_trade(self) -> dict:
        """
        Generates a new trade by applying a realistic fluctuation to its current price.
        """
        # Simulating a realistic price fluctuation (random walk)
        price_change_percent = random.gauss(0.00039, 0.005) # mu=0.00039 to reflect over the long term, due to factors like economic growth, inflation, and companies reinvesting profits, the market has a positive bias., sigma=0.5%
        self.price *= (1+price_change_percent)

        # Add a small chance of a larger volatility jump
        if random.random() < 0.01:
            self.price *= (1+random.gauss(0, 0.02))
        
        self.price = round(self.price, 2)

        # Generating bid/ask prices realistically around the new price
        spread = self.price*random.uniform(0.0005, 0.002)
        bid_price = round(self.price-spread, 2)
        ask_price = round(self.price+spread)

        # Assembling the full trade message using the new stateful price
        now = datetime.now(timezone.utc)
        return {
            "event_type" : "stock_trade",
            "trade_id" : str(uuid.uuid4()),
            "ticker" : self.ticker,
            "exchange" : "NSE",
            "trade_details" : {
                "LTP" : self.price,
                "volume" : random.randint(1,5000),
                "trade_time_utc" : now.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z',
                "market_cap" : round(self.price*self.issued_shares, 2)
            },
            "order_book_snapshot" : {
                "bids" : [
                    {"price" : bid_price, "quantity" : random.randint(1,5000)},
                    {"price" : bid_price*random.uniform(0.995, 0.999), "quantity" : random.randint(1,5000)}
                ],
                "asks" : [
                    {"price" : ask_price, "quantity" : random.randint(1,5000)},
                    {"price" : ask_price*random.uniform(1.001, 1.005), "quantity" : random.randint(1,5000)}
                ],
            },
            "data_source" : "simulated_feed_v2.0_stateful",
            "ingestion_timestamp_utc" : datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
        }


# --- Portfolio of Stateful Stocks ---
TICKER_PORTFOLIO = {
    # Top Tier by Market Cap
    "RELIANCE.NS":   Stock("RELIANCE.NS", 2950.00, 676.6),
    "TCS.NS":        Stock("TCS.NS", 4100.50, 361.8),
    "HDFCBANK.NS":   Stock("HDFCBANK.NS", 1550.75, 791.5),
    "INFY.NS":       Stock("INFY.NS", 1650.20, 415.0),
    "ICICIBANK.NS":  Stock("ICICIBANK.NS", 1100.00, 702.3),
    
    # Other Nifty 50 Majors
    "HINDUNILVR.NS": Stock("HINDUNILVR.NS", 2500.00, 235.0),
    "SBIN.NS":       Stock("SBIN.NS", 830.00, 892.5),
    "BAJFINANCE.NS": Stock("BAJFINANCE.NS", 7200.00, 65.3),
    "BHARTIARTL.NS": Stock("BHARTIARTL.NS", 1250.00, 564.7),
    "LT.NS":         Stock("LT.NS", 3600.00, 140.0),
    "KOTAKBANK.NS":  Stock("KOTAKBANK.NS", 1750.00, 198.8),
    
    # Other Popular Stocks
    "ASIANPAINT.NS": Stock("ASIANPAINT.NS", 2900.00, 95.9),
    "NESTLEIND.NS":  Stock("NESTLEIND.NS", 2500.00, 9.6),
    "MARUTI.NS":     Stock("MARUTI.NS", 12700.00, 30.2),
    "ZOMATO.NS":     Stock("ZOMATO.NS", 190.50, 883.6)
}

def create_kafka_producer():
    """Creates and returns a Confluent Kafka Producer instance."""
    try:
        producer = Producer({
            "bootstrap.servers" : KAFKA_BOOTSTRAP_SERVERS,
            # TODO: Add security configurations here  
        })
        logger.info("Kafka Producer created successfully.")
        return producer
    except Exception as e:
        logger.error(f"Failed to create Kafka producer: {e}")
        raise

def generate_stock_trade() -> dict:
    """
    Selects a random stock from the stateful portfolio and generates its next trade.
    """
    random_ticker = random.choice(list(TICKER_PORTFOLIO.keys()))
    stock_to_trade = TICKER_PORTFOLIO[random_ticker]
    return stock_to_trade.generate_trade()

def delivery_report(err, msg):
    """Callback function for message delivery reports."""
    if err is not None:
        logger.error(f'Message delivery failed: {err}')
    else:
        logger.info(f'Message delivered to {msg.topic()} [{msg.partition()}] at offset {msg.offset()}')


# --- Main Execution ---
def main():
    """Main function to run the data producer."""
    producer = create_kafka_producer()
    try:
        while True:
            stock_trade = generate_stock_trade()
            logger.info(f"Generated trade for {stock_trade['ticker']}: Price=${stock_trade['trade_details']['price']:.2f}")

            producer.produce(
                KAFKA_TOPIC,
                key = stock_trade["ticker"],
                value = json.dumps(stock_trade).encode("utf-8"),
                callback = delivery_report
            )
            producer.poll(0)
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Producer stopped by user.")
    finally:
        logger.info("Flushing messages...")
        producer.flush()

if __name__ == "__main__":
    main()
