import pytest
import datetime
import pandas as pd
import numpy as np

from src.data_loader import load_all_datasets
from src.solar_engine import SolarEngine
from src.demand_engine import DemandEngine
from src.cost_engine import CostEngine
from src.workforce_optimizer import WorkforceOptimizer
from src.scheduler import SolarSyncScheduler
from src.result_engine import evaluate_result_state
from src.pdf_generator import generate_pdf_decision_report
from src.report_generator import generate_excel_decision_report

def test_multi_factory_multi_date_validation():
    """Audits calculations, formulas, PDF, and Excel reports across multiple factories and dates."""
    datasets = load_all_datasets()
    solar_eng = SolarEngine(datasets["solar_weather"], datasets["factories"])
    demand_eng = DemandEngine(datasets["jobs"], datasets["machines"], datasets["tariffs"], datasets["workforce"])
    cost_eng = CostEngine(datasets["tariffs"])
    work_opt = WorkforceOptimizer(datasets["workforce"], datasets["machines"])
    scheduler = SolarSyncScheduler(solar_eng, cost_eng, work_opt, datasets["machines"], datasets["factories"])

    test_factories = ["FAC_001", "FAC_002", "FAC_005", "FAC_007", "FAC_016"]
    test_dates = ["2026-08-10", "2026-08-15", "2026-08-20"]

    for fac_id in test_factories:
        for dt_str in test_dates:
            jobs = demand_eng.get_jobs_for_factory_and_date(fac_id, dt_str)
            if jobs.empty:
                continue

            res = scheduler.optimize_schedule(fac_id, dt_str, jobs)
            base_m = res.baseline_metrics
            opt_m = res.optimized_metrics
            comp = res.comparison

            # 1. Formula Check: total_energy = solar_energy + grid_energy
            assert abs(base_m.total_energy_kwh - (base_m.solar_energy_used_kwh + base_m.grid_energy_used_kwh)) < 0.1, \
                f"Baseline energy formula failed for {fac_id} {dt_str}"
            
            if res.solver_status in ("OPTIMAL", "FEASIBLE"):
                assert abs(opt_m.total_energy_kwh - (opt_m.solar_energy_used_kwh + opt_m.grid_energy_used_kwh)) < 0.1, \
                    f"Optimized energy formula failed for {fac_id} {dt_str}"

            # 2. Result State Evaluation
            base_st = [b.start_hour for b in res.baseline_jobs]
            opt_st = [s.start_hour for s in res.scheduled_jobs]
            shifted_count = sum(1 for i in range(len(base_st)) if base_st[i] != opt_st[i])

            state = evaluate_result_state(
                solver_status=res.solver_status,
                shifted_count=shifted_count,
                baseline_grid_kwh=base_m.grid_energy_used_kwh,
                optimized_grid_kwh=opt_m.grid_energy_used_kwh,
                baseline_solar_kwh=base_m.solar_energy_used_kwh,
                optimized_solar_kwh=opt_m.solar_energy_used_kwh,
                baseline_cost_rs=base_m.electricity_cost_rs,
                optimized_cost_rs=opt_m.electricity_cost_rs
            )

            # Directional validations
            cost_diff = opt_m.electricity_cost_rs - base_m.electricity_cost_rs
            if cost_diff > 0.01:
                assert state.code == "NO_BENEFIT", f"Positive cost diff should be NO_BENEFIT for {fac_id} {dt_str}"
            elif shifted_count > 0 and cost_diff < -0.01:
                assert state.code == "IMPROVED", f"Cost reduction should be IMPROVED for {fac_id} {dt_str}"

            # 3. Report Generation Check
            pdf_bytes = generate_pdf_decision_report(res, {"factory_name": f"Factory {fac_id}"})
            excel_bytes = generate_excel_decision_report(res)

            assert len(pdf_bytes) > 2000, f"PDF report too small for {fac_id} {dt_str}"
            assert pdf_bytes.startswith(b"%PDF"), f"Invalid PDF header for {fac_id} {dt_str}"
            assert len(excel_bytes) > 5000, f"Excel report too small for {fac_id} {dt_str}"
            assert excel_bytes.startswith(b"PK"), f"Invalid Excel header for {fac_id} {dt_str}"

if __name__ == "__main__":
    test_multi_factory_multi_date_validation()
    print("Multi-factory & multi-date validation passed 100%!")
