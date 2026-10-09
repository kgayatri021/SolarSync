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
from src.recommender import RecommendationEngine

def test_recommendation_engine():
    ds = load_all_datasets()
    solar_eng = SolarEngine(ds["solar_weather"], ds["factories"])
    demand_eng = DemandEngine(ds["jobs"], ds["machines"], ds["tariffs"], ds["workforce"])
    cost_eng = CostEngine(ds["tariffs"])
    work_opt = WorkforceOptimizer(ds["workforce"], ds["machines"])
    scheduler = SolarSyncScheduler(solar_eng, cost_eng, work_opt, ds["machines"], ds["factories"])
    recommender = RecommendationEngine()

    jobs = demand_eng.get_jobs_for_factory_and_date("FAC_001", "2026-08-01")
    res = scheduler.optimize_schedule("FAC_001", "2026-08-01", jobs, time_limit_seconds=5)

    recs = recommender.generate_recommendations(res)
    assert len(recs) == len(jobs)
    assert hasattr(recs[0], "reason")
    assert hasattr(recs[0], "estimated_savings_rs")
