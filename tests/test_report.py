import os
import sys
import pytest

if os.path.exists(r'D:\python_packages') and r'D:\python_packages' not in sys.path:
    sys.path.insert(0, r'D:\python_packages')

from src.data_loader import load_all_datasets
from src.solar_engine import SolarEngine
from src.demand_engine import DemandEngine
from src.cost_engine import CostEngine
from src.workforce_optimizer import WorkforceOptimizer
from src.scheduler import SolarSyncScheduler
from src.report_generator import generate_excel_decision_report

def test_excel_report_generation():
    """Unit test for Section 44: Verifies Excel decision report generation (.xlsx)."""
    datasets = load_all_datasets()
    solar_engine = SolarEngine(datasets["solar_weather"], datasets["factories"])
    demand_engine = DemandEngine(datasets["jobs"], datasets["machines"], datasets["tariffs"], datasets["workforce"])
    cost_engine = CostEngine(datasets["tariffs"])
    workforce_optimizer = WorkforceOptimizer(datasets["workforce"], datasets["machines"])
    scheduler = SolarSyncScheduler(solar_engine, cost_engine, workforce_optimizer, datasets["machines"], datasets["factories"])

    jobs = demand_engine.get_jobs_for_factory_and_date("FAC_016", "2026-08-10")
    res = scheduler.optimize_schedule("FAC_016", "2026-08-10", jobs)

    excel_data = generate_excel_decision_report(res)
    assert excel_data is not None
    assert len(excel_data) > 0
    # PK magic bytes for zip/xlsx
    assert excel_data[:2] == b'PK'
