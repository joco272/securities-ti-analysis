import pandas as pd
from plotly.subplots import make_subplots
import plotly.graph_objects as go

def create_multi_pane_chart(df: pd.DataFrame, ticker: str, selected_indicators: list, chart_colors: dict):
    """
    Creates a customizable, multi-pane Plotly chart with candlesticks, volume, and selected indicators.

    Args:
        df: DataFrame containing OHLCV and all calculated indicator data.
        ticker: The stock ticker symbol (e.g., 'AAPL').
        selected_indicators: An ordered list of indicator names to display.
        chart_colors: A dictionary containing color settings for chart elements.

    Returns:
        A Plotly Figure object.
    """
    # --- 1. Define Indicator Plotting Logic ---
    indicator_map = {
        "MACD": [
            {"col": "macd", "type": "line", "color_key": "macd_line"},
            {"col": "macdsignal", "type": "line", "color_key": "macdsignal_line"},
            {"col": "macdhist", "type": "bar", "color_key": "macdhist"}
        ],
        "RSI": [{"col": "rsi", "type": "line"}],
        "MFI": [{"col": "mfi", "type": "line"}],
        "Stochastic RSI": [{"col": "stoch_rsi.k", "type": "line"}, {"col": "stoch_rsi.d", "type": "line"}],
        "OBV": [{"col": "obv", "type": "line"}],
        "A/D": [{"col": "ad", "type": "line"}],
        "Awesome Oscillator": [{"col": "ao", "type": "bar"}]
    }

    indicators_to_plot = [name for name in selected_indicators if name in indicator_map]
    num_indicators = len(indicators_to_plot)

    # --- 2. Create the Subplot Figure ---
    row_heights = [0.7] + [0.3] * num_indicators
    fig = make_subplots(
        rows=num_indicators + 1,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=row_heights,
        specs=[[{"secondary_y": True}]] + [[{"secondary_y": False}]] * num_indicators
    )

    # --- 3. Add Price Candlestick and Volume ---
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df['open'],
        high=df['high'],
        low=df['low'],
        close=df['close'],
        name='Price',
        increasing_line_color=chart_colors.get('bullish_candle', '#26a69a'),
        decreasing_line_color=chart_colors.get('bearish_candle', '#ef5350')
    ), row=1, col=1)

    fig.add_trace(go.Bar(
        x=df.index,
        y=df['volume'],
        name='Volume',
        marker_color='rgba(128,128,128,0.3)'
    ), row=1, col=1, secondary_y=True)
    fig.update_yaxes(showticklabels=False, secondary_y=True) # Hide volume labels

    # Add ticker label to the main price pane
    fig.add_annotation(
        text=ticker.upper(),
        xref="paper", yref="y domain",
        x=0.01, y=0.95,
        showarrow=False,
        font=dict(size=14, color="gray"),
        align="left"
    )

    # --- 4. Dynamically Add Indicator Subplots in Selected Order ---
    for i, indicator_name in enumerate(indicators_to_plot):
        current_row = i + 2
        plots = indicator_map[indicator_name]

        for plot_info in plots:
            col_name = plot_info["col"]
            if col_name in df.columns:
                plot_type = plot_info["type"]
                color_key = plot_info.get("color_key")
                color = chart_colors.get(color_key) if color_key else None

                if plot_type == "bar":
                    # Special coloring for histogram-style bars
                    if indicator_name in ["MACD", "Awesome Oscillator"]:
                        colors = [color if val >= 0 else chart_colors.get('bearish_candle', 'red') for val in df[col_name]]
                    else:
                        colors = color
                    fig.add_trace(go.Bar(x=df.index, y=df[col_name], name=col_name, marker_color=colors), row=current_row, col=1)
                else: # Default to line
                    fig.add_trace(go.Scatter(x=df.index, y=df[col_name], name=col_name, mode='lines', line=dict(color=color)), row=current_row, col=1)

        # Add a title annotation to each indicator pane
        fig.add_annotation(
            text=indicator_name,
            xref="paper", yref=f"y{current_row} domain",
            x=0.01, y=0.95,
            showarrow=False,
            font=dict(size=12, color="gray"),
            align="left"
        )


    # --- 5. Finalize Layout with Custom Colors and Crosshairs ---
    fig.update_layout(
        title_text="Stock Analysis",
        height=400 + (150 * num_indicators),
        showlegend=False,
        plot_bgcolor=chart_colors.get('background', '#ffffff'),
        paper_bgcolor=chart_colors.get('background', '#ffffff'),
        font_color='gray',
        xaxis=dict(
            rangeslider=dict(visible=False),
            type='date'
        ),
        yaxis=dict(
            autorange=True,
            fixedrange=False # Allow zooming
        )
    )

    # Configure the crosshair
    # Vertical line across all panes
    fig.update_xaxes(showspikes=True, spikemode='across', spikesnap='cursor', spikethickness=1, spikedash='dot')
    # Horizontal line on the hovered pane only
    fig.update_yaxes(showspikes=True, spikethickness=1, spikedash='dot')
    # Set hovermode to 'closest' to enable per-pane interactions
    fig.update_layout(hovermode='closest')

    return fig
