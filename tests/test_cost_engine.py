import os
import sys
import numpy as np
import pytest

if os.path.exists(r'D:\python_packages') and r'D:\python_packages' not in sys.path:
    sys.path.insert(0, r'D:\python_packages')

from src.data_loader import load_electricity_tariffs
from src.cost_engine import CostEngine, ScheduleMetrics

def test_cost_engine_calculations():
    tariffs = load_electricity_tariffs()
    engine = CostEngine(tariffs)

    demand = np.full(24, 100.0) # 100 kW demand flat
    solar = np.zeros(24) # 0 solar
    solar[10:14] = 100.0 # 100 kW solar during 10..13

    metrics = engine.calculate_schedule_metrics(demand, solar)
    assert metrics.total_energy_kwh == 2400.0
    assert metrics.solar_energy_used_kwh == 400.0
    assert metrics.grid_energy_used_kwh == 2000.0
    assert metrics.electricity_cost_rs > 0.0

def test_critical_solar_energy_percentage_fix():
    """Unit test for Section 7: Verifies relative solar energy increase percentage formula."""
    tariffs = load_electricity_tariffs()
    engine = CostEngine(tariffs)

    # Simulated baseline metrics (67.6 kWh solar) vs optimized (130.0 kWh solar)
    base_metrics = ScheduleMetrics(
        total_energy_kwh=1000.0,
        solar_energy_used_kwh=67.6,
        grid_energy_used_kwh=932.4,
        solar_utilization_percent=10.0,
        grid_dependency_percent=93.2,
        electricity_cost_rs=6000.0,
        labour_cost_rs=1000.0,
        overtime_cost_rs=0.0,
        total_operating_cost_rs=7000.0
    )
    
    opt_metrics = ScheduleMetrics(
        total_energy_kwh=1000.0,
        solar_energy_used_kwh=130.0,
        grid_energy_used_kwh=870.0,
        solar_utilization_percent=19.2,
        grid_dependency_percent=87.0,
        electricity_cost_rs=5500.0,
        labour_cost_rs=1000.0,
        overtime_cost_rs=0.0,
        total_operating_cost_rs=6500.0
    )

    comp = engine.compare_schedules(base_metrics, opt_metrics)
    
    # Relative solar energy increase must equal ~92.31%
    expected_pct = round((130.0 - 67.6) / 67.6 * 100.0, 2)
    assert comp.solar_increase_percent == expected_pct
    assert comp.solar_increase_percent == 92.31
    assert comp.solar_utilization_improvement_percent == 9.2 # percentage points diff
