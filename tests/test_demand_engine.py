import os
import sys
import pytest

if os.path.exists(r'D:\python_packages') and r'D:\python_packages' not in sys.path:
    sys.path.insert(0, r'D:\python_packages')

from src.data_loader import load_production_jobs, load_machines, load_electricity_tariffs, load_workforce
from src.demand_engine import DemandEngine

def test_demand_engine():
    jobs = load_production_jobs()
    machines = load_machines()
    tariffs = load_electricity_tariffs()
    workforce = load_workforce()

    engine = DemandEngine(jobs, machines, tariffs, workforce)
    fac_jobs = engine.get_jobs_for_factory_and_date("FAC_001", "2026-08-01")
    assert not fac_jobs.empty
    assert "derived_energy_kwh" in fac_jobs.columns
    assert "expected_total_cost_rs" in fac_jobs.columns
