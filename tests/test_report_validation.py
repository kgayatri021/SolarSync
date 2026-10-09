import pytest
import io
import openpyxl
import pandas as pd
from src.pdf_generator import generate_pdf_decision_report
from src.report_generator import generate_excel_decision_report
from src.solar_engine import SolarEngine
from src.demand_engine import DemandEngine
from src.cost_engine import CostEngine
from src.workforce_optimizer import WorkforceOptimizer
from src.scheduler import SolarSyncScheduler
from src.data_loader import load_all_datasets

def test_pdf_and_excel_generation_integrity():
    datasets = load_all_datasets()
    solar_eng = SolarEngine(datasets["solar_weather"], datasets["factories"])
    demand_eng = DemandEngine(datasets["jobs"], datasets["machines"], datasets["tariffs"], datasets["workforce"])
    cost_eng = CostEngine(datasets["tariffs"])
    work_opt = WorkforceOptimizer(datasets["workforce"], datasets["machines"])
    scheduler = SolarSyncScheduler(solar_eng, cost_eng, work_opt, datasets["machines"], datasets["factories"])

    fac_id = "FAC_016"
    target_date = "2026-08-10"
    fac_jobs = demand_eng.get_jobs_for_factory_and_date(fac_id, target_date)
    res = scheduler.optimize_schedule(fac_id, target_date, fac_jobs, time_limit_seconds=5)

    # 1. Test PDF Generation
    pdf_bytes = generate_pdf_decision_report(res, factory_info={"factory_name": "Test Factory", "district": "Visakhapatnam"})
    assert pdf_bytes is not None
    assert len(pdf_bytes) > 500
    assert pdf_bytes.startswith(b"%PDF")

    # 2. Test Excel Generation
    excel_bytes = generate_excel_decision_report(res)
    assert excel_bytes is not None
    assert len(excel_bytes) > 1000
    assert excel_bytes.startswith(b"PK")

    # Read back Excel workbook to verify sheets and values
    wb = openpyxl.load_workbook(io.BytesIO(excel_bytes))
    sheet_names = wb.sheetnames
    expected_sheets = ["Summary", "Recommended Schedule", "Energy Impact", "Cost Impact", "Workforce", "Scenario", "Validation"]
    for s_name in expected_sheets:
        assert s_name in sheet_names, f"Sheet {s_name} missing from generated Excel report."

    # Verify Summary sheet values
    summary_ws = wb["Summary"]
    assert "SOLAR SYNC" in str(summary_ws["A1"].value)
    assert fac_id in str(summary_ws["A2"].value)
