import pandas as pd
from plotly.subplots import make_subplots
import plotly.graph_objects as go

def create_multi_pane_chart(df: pd.DataFrame, ticker: str, selected_indicators: list, chart_colors: dict):
    """
    Creates a customizable, multi-pane Plotly chart with candlesticks, volume, and selected indicators.
    This is a simplified version with problematic UI features reverted.
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
        increasing_line_color=chart_colors.get('bullish_candle', '#26a69a'),
        decreasing_line_color=chart_colors.get('bearish_candle', '#ef5350')
    ), row=1, col=1)

    fig.add_trace(go.Bar(
        x=df.index,
        y=df['volume'],
        name='Volume',
        marker_color='rgba(128,128,128,0.3)'
    ), row=1, col=1, secondary_y=True)
    fig.update_yaxes(showticklabels=False, secondary_y=True)

    # --- 4. Dynamically Add Indicator Subplots ---
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
                    fig.add_trace(go.Bar(x=df.index, y=df[col_name], name=col_name, marker_color=color), row=current_row, col=1)
                else:
                    fig.add_trace(go.Scatter(x=df.index, y=df[col_name], name=col_name, mode='lines', line=dict(color=color)), row=current_row, col=1)

    # --- 5. Finalize Layout ---
    fig.update_layout(
        height=400 + (150 * num_indicators),
        showlegend=False,
        plot_bgcolor=chart_colors.get('background', '#ffffff'),
        paper_bgcolor=chart_colors.get('background', '#ffffff'),
        font_color='gray',
        xaxis=dict(rangeslider=dict(visible=False)),
        yaxis=dict(autorange=True, fixedrange=False)
    )

    # Adjust subplot title positions to be on the top left
    for annotation in fig['layout']['annotations']:
        annotation['x'] = 0
        annotation['xanchor'] = 'left'

    return fig
