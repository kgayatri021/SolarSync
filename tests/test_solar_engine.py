import os
import sys
import pytest

if os.path.exists(r'D:\python_packages') and r'D:\python_packages' not in sys.path:
    sys.path.insert(0, r'D:\python_packages')

from src.data_loader import load_factories, load_solar_weather
from src.solar_engine import SolarEngine

def test_solar_engine_profile():
    factories = load_factories()
    solar_df = load_solar_weather()
    engine = SolarEngine(solar_df, factories)
    
    profile = engine.get_solar_profile_for_factory("FAC_001", "2026-08-01")
    assert len(profile) == 24
    assert "solar_available_kw" in profile.columns
    assert (profile["solar_available_kw"] >= 0).all()

def test_solar_physics_behavior():
    factories = load_factories()
    solar_df = load_solar_weather()
    engine = SolarEngine(solar_df, factories)
    
    arr = engine.get_hourly_solar_array("FAC_001", "2026-08-01")
    assert len(arr) == 24
    # Night time solar (hours 0-4) should be ~0
    assert arr[0] <= 1.0
    assert arr[23] <= 1.0
    # Midday solar (hours 11-13) should be peak
    assert arr[12] > arr[0]
