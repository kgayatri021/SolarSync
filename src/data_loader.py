import os
import sys
import pandas as pd
from typing import Dict

if os.path.exists(r'D:\python_packages') and r'D:\python_packages' not in sys.path:
    sys.path.insert(0, r'D:\python_packages')

from src.utils import get_data_path
from src.logger import logger

try:
    import streamlit as st
    cache_decorator = st.cache_data
except (ImportError, Exception):
    def cache_decorator(func):
        return func

@cache_decorator
def load_factories() -> pd.DataFrame:
    path = get_data_path("factories.csv")
    df = pd.read_csv(path)
    logger.info(f"Loaded {len(df)} factories from {path}")
    return df

@cache_decorator
def load_machines() -> pd.DataFrame:
    path = get_data_path("machines.csv")
    df = pd.read_csv(path)
    # Fill missing maintenance status with "None"
    df["maintenance_status"] = df["maintenance_status"].fillna("None")
    logger.info(f"Loaded {len(df)} machines from {path}")
    return df

@cache_decorator
def load_production_jobs() -> pd.DataFrame:
    path = get_data_path("production_jobs.csv")
    df = pd.read_csv(path)
    # Parse release & deadline to datetime
    df["job_release_time"] = pd.to_datetime(df["job_release_time"])
    df["deadline"] = pd.to_datetime(df["deadline"])
    if "earliest_start_time" in df.columns:
        df["earliest_start_time"] = pd.to_datetime(df["earliest_start_time"])
    if "latest_start_time" in df.columns:
        df["latest_start_time"] = pd.to_datetime(df["latest_start_time"])
    logger.info(f"Loaded {len(df)} production jobs from {path}")
    return df

@cache_decorator
def load_workforce() -> pd.DataFrame:
    path = get_data_path("workforce.csv")
    df = pd.read_csv(path)
    logger.info(f"Loaded {len(df)} workforce records from {path}")
    return df

@cache_decorator
def load_solar_weather() -> pd.DataFrame:
    path = get_data_path("solar_weather.csv")
    df = pd.read_csv(path)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["date"] = pd.to_datetime(df["date"])
    logger.info(f"Loaded {len(df)} solar weather records from {path}")
    return df

@cache_decorator
def load_electricity_tariffs() -> pd.DataFrame:
    path = get_data_path("electricity_tariffs.csv")
    df = pd.read_csv(path)
    logger.info(f"Loaded {len(df)} tariff records from {path}")
    return df

@cache_decorator
def load_production_energy_history() -> pd.DataFrame:
    path = get_data_path("production_energy_history.csv")
    df = pd.read_csv(path)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["date"] = pd.to_datetime(df["date"])
    logger.info(f"Loaded {len(df)} historical energy records from {path}")
    return df

def load_all_datasets() -> Dict[str, pd.DataFrame]:
    """Loads all 7 datasets into a dictionary."""
    return {
        "factories": load_factories(),
        "machines": load_machines(),
        "jobs": load_production_jobs(),
        "workforce": load_workforce(),
        "solar_weather": load_solar_weather(),
        "tariffs": load_electricity_tariffs(),
        "history": load_production_energy_history()
    }
