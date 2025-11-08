import pandas as pd
from plotly.subplots import make_subplots
import plotly.graph_objects as go

def create_multi_pane_chart(df: pd.DataFrame, ticker: str, selected_indicators: list):
    """
    Creates a customizable, multi-pane Plotly chart with candlesticks, volume, and selected indicators.
    This version includes a highly targeted fix for the y-axis autoscaling issue.
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
    subplot_titles = [ticker.upper()] + indicators_to_plot
    row_heights = [0.7] + [0.3] * num_indicators
    fig = make_subplots(
        rows=num_indicators + 1,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=row_heights,
        specs=[[{"secondary_y": True}]] + [[{"secondary_y": False}]] * num_indicators,
        subplot_titles=subplot_titles
    )

    # --- 3. Add Price Candlestick and Volume ---
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

    fig.add_trace(go.Bar(
        x=df.index,
        y=df['volume'],
        name='Volume',
        marker_color='rgba(128,128,128,0.3)'
    ), row=1, col=1, secondary_y=True)

    # --- 4. Dynamically Add Indicator Subplots ---
    for i, indicator_name in enumerate(indicators_to_plot):
        current_row = i + 2
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

    # --- 5. Finalize Layout ---
    fig.update_layout(
        height=400 + (150 * num_indicators),
        showlegend=False,
        plot_bgcolor='#ffffff',
        paper_bgcolor='#ffffff',
        font_color='gray',
        xaxis=dict(rangeslider=dict(visible=False)),
    )

    # --- 6. Explicitly Enable Autoscaling on All Y-Axes (Targeted Approach) ---
    # Apply autoscaling to the main price chart's primary y-axis
    fig.update_yaxes(autorange=True, fixedrange=False, row=1, col=1, secondary_y=False)
    # Apply autoscaling to the volume chart's secondary y-axis
    fig.update_yaxes(autorange=True, fixedrange=False, row=1, col=1, secondary_y=True, showticklabels=False)

    # Apply autoscaling to each indicator subplot's y-axis
    for i in range(num_indicators):
        fig.update_yaxes(autorange=True, fixedrange=False, row=i + 2, col=1)

    # Adjust subplot title positions to be on the top left
    for annotation in fig['layout']['annotations']:
        annotation['x'] = 0
        annotation['xanchor'] = 'left'

    return fig
