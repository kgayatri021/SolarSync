import os
import sys
import pandas as pd
import numpy as np
from typing import Dict, List, Optional

if os.path.exists(r'D:\python_packages') and r'D:\python_packages' not in sys.path:
    sys.path.insert(0, r'D:\python_packages')

from src.logger import logger

class DemandEngine:
    def __init__(
        self, 
        jobs_df: pd.DataFrame, 
        machines_df: pd.DataFrame, 
        tariffs_df: pd.DataFrame,
        workforce_df: pd.DataFrame
    ):
        self.jobs_df = jobs_df.copy()
        self.machines_df = machines_df.copy()
        self.tariffs_df = tariffs_df.copy()
        self.workforce_df = workforce_df.copy()

        # Build lookup dicts for high performance
        self.machine_map = self.machines_df.set_index("machine_id").to_dict(orient="index")

    def enrich_job_details(self, job_row: pd.Series) -> pd.Series:
        """Enriches a production job record with machine specifications and expected energy/cost metrics."""
        row = job_row.copy()
        mid = row["eligible_machine_id"]
        mach = self.machine_map.get(mid, {})

        rated_kw = float(mach.get("rated_power_kw", 10.0))
        prod_rate = float(mach.get("production_rate_units_per_hour", 100.0))
        qty = float(row.get("quantity_required", 100))

        # Runtime estimation
        if pd.notna(row.get("estimated_duration_hours")) and float(row.get("estimated_duration_hours")) > 0:
            duration = float(row.get("estimated_duration_hours"))
        else:
            duration = qty / prod_rate if prod_rate > 0 else 1.0
        
        row["duration_hours"] = duration

        # Energy consumption (kWh)
        if pd.notna(row.get("energy_required_kwh")) and float(row.get("energy_required_kwh")) > 0:
            energy_kwh = float(row.get("energy_required_kwh"))
        else:
            energy_kwh = rated_kw * duration
        
        row["derived_energy_kwh"] = energy_kwh
        row["machine_rated_power_kw"] = rated_kw

        # Average labour rate for factory
        fid = row["factory_id"]
        fac_workers = self.workforce_df[self.workforce_df["factory_id"] == fid]
        if not fac_workers.empty:
            avg_labour_rate = fac_workers["hourly_labour_cost"].mean()
        else:
            avg_labour_rate = 150.0 # Default standard rate

        workers_req = int(row.get("workers_required", 1))
        row["expected_labour_cost_rs"] = duration * workers_req * avg_labour_rate
        
        # Standard average electricity rate (~₹7.5/kWh baseline estimate)
        row["expected_electricity_cost_rs"] = energy_kwh * 7.50
        row["expected_total_cost_rs"] = row["expected_labour_cost_rs"] + row["expected_electricity_cost_rs"]

        return row

    def get_jobs_for_factory_and_date(self, factory_id: str, target_date: str) -> pd.DataFrame:
        """Filters jobs for a specific factory released on target_date or active range."""
        target_dt = pd.to_datetime(target_date)
        
        # Match exact release date first for daily batch scheduling
        exact_mask = (self.jobs_df["factory_id"] == factory_id) & (
            self.jobs_df["job_release_time"].dt.date == target_dt.date()
        )
        subset = self.jobs_df[exact_mask].copy()

        if subset.empty:
            # Match active range if exact release date empty
            range_mask = (self.jobs_df["factory_id"] == factory_id) & (
                (self.jobs_df["job_release_time"].dt.date <= target_dt.date()) &
                (self.jobs_df["deadline"].dt.date >= target_dt.date())
            )
            subset = self.jobs_df[range_mask].head(10).copy()

        if subset.empty:
            # Fallback: get first 10 jobs for factory
            subset = self.jobs_df[self.jobs_df["factory_id"] == factory_id].head(10).copy()

        enriched = subset.apply(self.enrich_job_details, axis=1)
        return enriched
