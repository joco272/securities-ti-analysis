# Configuration for time intervals and their data source mapping

# Mapping of desired intervals to yfinance source intervals
# Format: {desired_interval: (yfinance_interval, resample_rule)}
# If resample_rule is None, no resampling is needed
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

# List of available intervals for the UI
AVAILABLE_INTERVALS = list(INTERVAL_CONFIG.keys())

def get_source_interval(interval: str) -> str:
    """
    Get the yfinance source interval for a given desired interval.
    
    Args:
        interval: The desired interval (e.g., '45m', '4h')
        
    Returns:
        The yfinance source interval to fetch
    """
    if interval not in INTERVAL_CONFIG:
        raise ValueError(f"Unsupported interval: {interval}. Available: {AVAILABLE_INTERVALS}")
    return INTERVAL_CONFIG[interval]['source_interval']

def get_resample_rule(interval: str) -> str:
    """
    Get the pandas resample rule for a given interval.
    
    Args:
        interval: The desired interval (e.g., '45m', '4h')
        
    Returns:
        The pandas resample rule, or None if no resampling needed
    """
    if interval not in INTERVAL_CONFIG:
        raise ValueError(f"Unsupported interval: {interval}. Available: {AVAILABLE_INTERVALS}")
    return INTERVAL_CONFIG[interval]['resample_rule']

def needs_resampling(interval: str) -> bool:
    """
    Check if an interval requires resampling.
    
    Args:
        interval: The desired interval
        
    Returns:
        True if resampling is needed, False otherwise
    """
    return get_resample_rule(interval) is not None
