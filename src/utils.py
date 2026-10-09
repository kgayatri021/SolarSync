import os
import sys
import pandas as pd

if os.path.exists(r'D:\python_packages') and r'D:\python_packages' not in sys.path:
    sys.path.insert(0, r'D:\python_packages')

def get_data_path(filename: str) -> str:
    """
    Returns the absolute or relative path to a dataset CSV file.
    Checks data/ first, then fallback to root directory.
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_path = os.path.join(base_dir, "data", filename)
    if os.path.exists(data_path):
        return data_path
    
    root_path = os.path.join(base_dir, filename)
    if os.path.exists(root_path):
        return root_path
        
    # Relative fallback
    if os.path.exists(os.path.join("data", filename)):
        return os.path.join("data", filename)
    return filename

def format_currency(val: float) -> str:
    """Format a number as Indian Rupees (INR)."""
    if pd.isna(val):
        return "₹0"
    return f"₹{val:,.2f}"

def format_kwh(val: float) -> str:
    """Format kWh with thousand separators."""
    if pd.isna(val):
        return "0 kWh"
    return f"{val:,.1f} kWh"

def parse_time_str(time_str: str) -> float:
    """Converts 'HH:MM', 'HH:MM:SS', or 'YYYY-MM-DD HH:MM:SS' string into float hours (e.g., '08:30' -> 8.5)."""
    if not isinstance(time_str, str) or not time_str.strip():
        return 0.0
    try:
        dt = pd.to_datetime(time_str.strip())
        return float(dt.hour) + float(dt.minute) / 60.0 + float(dt.second) / 3600.0
    except Exception:
        pass
    parts = time_str.strip().split(':')
    try:
        hours = float(parts[0])
        minutes = float(parts[1]) if len(parts) > 1 else 0.0
        seconds = float(parts[2]) if len(parts) > 2 else 0.0
        return hours + (minutes / 60.0) + (seconds / 3600.0)
    except (ValueError, IndexError):
        return 0.0

def hour_to_time_str(hour_float: float) -> str:
    """Converts float hours (e.g. 14.5) to '14:30' string."""
    h = int(hour_float) % 24
    m = int(round((hour_float - int(hour_float)) * 60))
    if m == 60:
        h = (h + 1) % 24
        m = 0
    return f"{h:02d}:{m:02d}"
