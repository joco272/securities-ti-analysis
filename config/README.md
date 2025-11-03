# Interval Configuration

This document describes the interval configuration system for the Securities Technical Indicators Analysis application.

## Overview

The application supports multiple time intervals for technical indicator calculations. Some intervals are natively supported by the yfinance data provider, while others are implemented through data resampling.

## Configured Intervals

### 15-Minute Interval (`15m`)
- **Native Support**: Yes
- **Data Source**: yfinance 15-minute data
- **Use Case**: High-frequency trading analysis, short-term patterns

### 45-Minute Interval (`45m`)
- **Native Support**: No (resampled)
- **Data Source**: yfinance 15-minute data → resampled to 45 minutes
- **Use Case**: Medium-term intraday analysis

### 4-Hour Interval (`4h`)
- **Native Support**: No (resampled)
- **Data Source**: yfinance 1-hour data → resampled to 4 hours
- **Use Case**: Swing trading, multi-day pattern recognition

## How Resampling Works

When an interval is not natively supported by yfinance, the application:

1. Fetches higher-resolution data from yfinance
2. Uses pandas resampling to aggregate the data
3. Applies proper OHLCV aggregation:
   - **Open**: First value in the period
   - **High**: Maximum value in the period
   - **Low**: Minimum value in the period
   - **Close**: Last value in the period
   - **Volume**: Sum of all volumes in the period

## Configuration File

Intervals are configured in `config/intervals.py`:

```python
INTERVAL_CONFIG = {
    '15m': {
        'source_interval': '15m',
        'resample_rule': None,
        'description': '15-minute intervals (native support)'
    },
    '45m': {
        'source_interval': '15m',
        'resample_rule': '45min',
        'description': '45-minute intervals (resampled from 15m)'
    },
    '4h': {
        'source_interval': '1h',
        'resample_rule': '4H',
        'description': '4-hour intervals (resampled from 1h)'
    }
}
```

## Adding New Intervals (Developers)

To add a new interval:

1. Edit `config/intervals.py`
2. Add an entry to `INTERVAL_CONFIG` dictionary:

```python
'2h': {
    'source_interval': '1h',      # yfinance interval to fetch
    'resample_rule': '2H',         # pandas resample rule
    'description': '2-hour intervals (resampled from 1h)'
}
```

3. The new interval will automatically appear in the Streamlit UI

### Valid yfinance Intervals

- Intraday: `1m`, `2m`, `5m`, `15m`, `30m`, `60m`, `90m`, `1h`
- Daily and above: `1d`, `5d`, `1wk`, `1mo`, `3mo`

### Valid Pandas Resample Rules

- Minutes: `15min`, `30min`, `45min`
- Hours: `2H`, `4H`, `6H`
- Days: `2D`, `3D`
- Weeks: `W`

## Future Enhancement

A user interface will be developed to allow non-technical users to add and configure intervals through the web application without editing configuration files.

## Usage in Code

```python
from config.intervals import (
    AVAILABLE_INTERVALS,
    get_source_interval,
    get_resample_rule,
    needs_resampling
)

# Get list of all available intervals
intervals = AVAILABLE_INTERVALS  # ['15m', '45m', '4h']

# Check if an interval needs resampling
if needs_resampling('45m'):
    source = get_source_interval('45m')  # '15m'
    rule = get_resample_rule('45m')      # '45min'
    # Fetch source data and resample
```

## Testing

Run the test suite to verify interval configuration:

```bash
python /tmp/test_intervals.py
```

## Implementation Files

- `config/intervals.py` - Interval configuration and helper functions
- `src/data_processing/data_retrieval.py` - Data fetching and resampling logic
- `src/app.py` - Streamlit UI integration
