import sys
import os

# Add the project root to the python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.plotting.charts import create_multi_pane_chart
from src.data_processing.data_query import fetch_data_with_indicators

if __name__ == '__main__':
    # This block is for testing the charting function locally
    ticker_to_test = "MSFT" # Use a ticker we know has data
    interval_to_test = "1d"
    indicators_to_test = ["MACD", "RSI", "Awesome Oscillator"]

    print(f"Fetching data for {ticker_to_test} to test charting...")
    test_df = fetch_data_with_indicators(ticker_to_test, interval_to_test)

    if not test_df.empty:
        print("Data fetched. Creating chart...")
        fig = create_multi_pane_chart(test_df, indicators_to_test)
        # This will open the chart in your default web browser
        fig.show()
        print("Chart displayed.")
    else:
        print(f"Could not fetch data for {ticker_to_test}. You may need to run the main app first to populate the database.")
