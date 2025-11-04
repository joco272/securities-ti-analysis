import pandas as pd
from plotly.subplots import make_subplots
import plotly.graph_objects as go

def create_multi_pane_chart(df: pd.DataFrame, selected_indicators: list):
    """
    Creates a multi-pane Plotly chart with candlesticks, volume, and selected indicators.

    Args:
        df: DataFrame containing OHLCV and all calculated indicator data.
        selected_indicators: A list of indicator names to display.

    Returns:
        A Plotly Figure object.
    """

    # --- 1. Define which indicators will be plotted ---
    # We create a mapping to handle multi-line indicators like MACD
    indicator_map = {
        "MACD": ["macd", "macdsignal"],
        "RSI": ["rsi"],
        "MFI": ["mfi"],
        "Stochastic RSI": ["stoch_rsi_k", "stoch_rsi_d"],
        "OBV": ["obv"],
        "A/D": ["ad"],
        "Awesome Oscillator": ["ao"]
    }

    indicators_to_plot = [name for name in selected_indicators if name in indicator_map]
    num_indicators = len(indicators_to_plot)

    # --- 2. Create the subplot figure ---
    # We need one row for the price/volume and one for each indicator
    # The main price chart will be larger
    row_heights = [0.6] + [0.4] * num_indicators
    fig = make_subplots(
        rows=num_indicators + 1,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.02,
        row_heights=row_heights
    )

    # --- 3. Add Price Candlestick and Volume ---
    # Add Candlestick trace to the first row
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df['open'],
        high=df['high'],
        low=df['low'],
        close=df['close'],
        name='Price'
    ), row=1, col=1)

    # Add Volume bar chart to the first row on a secondary y-axis
    fig.add_trace(go.Bar(
        x=df.index,
        y=df['volume'],
        name='Volume',
        marker_color='rgba(0,0,100,0.3)'
    ), row=1, col=1)

    # --- 4. Dynamically add indicator subplots ---
    current_row = 2
    for indicator_name in indicators_to_plot:
        columns = indicator_map[indicator_name]

        # Special case for bar charts like Awesome Oscillator
        if indicator_name == "Awesome Oscillator":
            colors = ['green' if val >= 0 else 'red' for val in df['ao']]
            fig.add_trace(go.Bar(x=df.index, y=df['ao'], name=indicator_name, marker_color=colors), row=current_row, col=1)
        else:
            # Plot each column associated with the indicator as a line
            for col in columns:
                if col in df.columns:
                    fig.add_trace(go.Line(x=df.index, y=df[col], name=col), row=current_row, col=1)

        current_row += 1

    # --- 5. Finalize layout ---
    fig.update_layout(
        title_text="Stock Analysis",
        height=400 + (200 * num_indicators), # Adjust height based on number of indicators
        xaxis_rangeslider_visible=False, # Hide the range slider on the bottom plot
        showlegend=True
    )
    # Hide the range slider on the main price chart specifically
    fig.update_xaxes(rangeslider_visible=False, row=1, col=1)

    return fig

