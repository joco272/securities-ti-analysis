import pandas as pd
from plotly.subplots import make_subplots
import plotly.graph_objects as go

def create_multi_pane_chart(df: pd.DataFrame, ticker: str, selected_indicators: list):
    """
    Creates a multi-pane Plotly chart with candlesticks, volume, and selected indicators.
    This version gives Volume its own subplot to fix the y-axis autoscaling bug.
    """
    # --- 1. Define Indicator Plotting Logic ---
    indicator_map = {
        "MACD": [
            {"col": "macd", "type": "line", "color": "#009688"},
            {"col": "macdsignal", "type": "line", "color": "#ff5722"},
            {"col": "macdhist", "type": "bar", "color": "#607d8b"}
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
    # We now add one more row for the Volume chart.
    num_rows = num_indicators + 2
    subplot_titles = [ticker.upper(), "Volume"] + indicators_to_plot

    # Adjust row heights: 60% for price, 20% for volume, 20% for each indicator
    row_heights = [0.6] + [0.2] * (num_indicators + 1)

    fig = make_subplots(
        rows=num_rows,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=row_heights,
        subplot_titles=subplot_titles
    )

    # --- 3. Add Price Candlestick ---
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df['open'],
        high=df['high'],
        low=df['low'],
        close=df['close'],
        name='Price',
        increasing_line_color='#26a69a',
        decreasing_line_color='#ef5350'
    ), row=1, col=1)

    # --- 4. Add Volume to its own Subplot ---
    fig.add_trace(go.Bar(
        x=df.index,
        y=df['volume'],
        name='Volume',
        marker_color='rgba(128,128,128,0.5)'
    ), row=2, col=1)

    # --- 5. Dynamically Add Indicator Subplots ---
    # Indicators now start from row 3
    for i, indicator_name in enumerate(indicators_to_plot):
        current_row = i + 3
        plots = indicator_map[indicator_name]
        for plot_info in plots:
            col_name = plot_info["col"]
            if col_name in df.columns:
                plot_type = plot_info["type"]
                color = plot_info.get("color")
                if plot_type == "bar":
                    fig.add_trace(go.Bar(x=df.index, y=df[col_name], name=col_name, marker_color=color), row=current_row, col=1)
                else:
                    fig.add_trace(go.Scatter(x=df.index, y=df[col_name], name=col_name, mode='lines', line=dict(color=color)), row=current_row, col=1)

    # --- 6. Finalize Layout ---
    fig.update_layout(
        height=200 + (150 * num_rows), # Adjust height based on number of rows
        showlegend=False,
        plot_bgcolor='#ffffff',
        paper_bgcolor='#ffffff',
        font_color='gray',
        xaxis=dict(rangeslider=dict(visible=False)),
        # Ensure all y-axes are not fixed now that the conflicting secondary_y is gone
        yaxis=dict(autorange=True, fixedrange=False),
        yaxis2=dict(autorange=True, fixedrange=False),
        yaxis3=dict(autorange=True, fixedrange=False),
        yaxis4=dict(autorange=True, fixedrange=False), # Add more if more indicators are possible
        yaxis5=dict(autorange=True, fixedrange=False)
    )

    # Adjust subplot title positions to be on the top left
    for annotation in fig['layout']['annotations']:
        annotation['x'] = 0
        annotation['xanchor'] = 'left'

    return fig
