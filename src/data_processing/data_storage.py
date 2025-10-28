from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import pandas as pd
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import INFLUXDB_URL, INFLUXDB_TOKEN, INFLUXDB_ORG, INFLUXDB_BUCKET
from database import get_influxdb_client

def write_indicators_to_influxdb(ticker: str, interval: str, data: pd.DataFrame):
    """
    Writes the indicator data to InfluxDB.

    Args:
        ticker: The stock ticker symbol.
        interval: The data interval (e.g., '15m', '4h', '1d').
        data: A pandas DataFrame with the indicator data.
    """
    client = get_influxdb_client()
    write_api = client.write_api(write_options=SYNCHRONOUS)

    for timestamp, row in data.iterrows():
        point = Point("indicators") \
            .tag("ticker", ticker) \
            .tag("interval", interval) \
            .field("open", row["Open"]) \
            .field("high", row["High"]) \
            .field("low", row["Low"]) \
            .field("close", row["Close"]) \
            .field("volume", row["Volume"]) \
            .field("macd", row["macd"]) \
            .field("macdsignal", row["macdsignal"]) \
            .field("macdhist", row["macdhist"]) \
            .field("mfi", row["mfi"]) \
            .field("rsi", row["rsi"]) \
            .time(timestamp)
        write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=point)

    print(f"Successfully wrote {len(data)} data points to InfluxDB for {ticker} at {interval} interval.")

if __name__ == '__main__':
    # This block is for testing purposes and will be removed later.
    from data_retrieval import fetch_ohlcv
    from indicators import calculate_indicators

    ticker = 'AAPL'
    start_date = '2023-12-01'
    end_date = '2023-12-31'
    interval = '1d'

    try:
        ohlcv_data = fetch_ohlcv(ticker, start_date, end_date, interval)
        if not ohlcv_data.empty:
            indicators_df = calculate_indicators(ohlcv_data).dropna()
            write_indicators_to_influxdb(ticker, interval, indicators_df)
        else:
            print(f"No data found for {ticker} in the specified date range.")
    except Exception as e:
        print(f"An error occurred: {e}")
