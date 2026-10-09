import os
import sys
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass, field

if os.path.exists(r'D:\python_packages') and r'D:\python_packages' not in sys.path:
    sys.path.insert(0, r'D:\python_packages')

from src.logger import logger

@dataclass
class DatasetCheckResult:
    dataset_name: str
    row_count: int
    col_count: int
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SystemValidationReport:
    is_healthy: bool
    results: Dict[str, DatasetCheckResult] = field(default_factory=dict)
    summary_errors: List[str] = field(default_factory=list)

def validate_factories(df: pd.DataFrame, machines_df: pd.DataFrame = None, workforce_df: pd.DataFrame = None) -> DatasetCheckResult:
    errors = []
    warnings = []
    metrics = {}
    
    # 1. Unique ID
    if df["factory_id"].duplicated().any():
        dup_ids = df[df["factory_id"].duplicated()]["factory_id"].tolist()
        errors.append(f"Duplicate factory_ids found: {dup_ids}")
        
    # 2. Capacity & Demand range checks
    if (df["contracted_demand_kw"] > df["grid_connection_capacity_kw"]).any():
        invalid = df[df["contracted_demand_kw"] > df["grid_connection_capacity_kw"]]["factory_id"].tolist()
        errors.append(f"Contracted demand > Grid capacity in factories: {invalid}")
        
    if (df["installed_solar_capacity_kw"] < 0).any():
        errors.append("Negative installed solar capacity found.")
        
    if (df["battery_capacity_kwh"] < 0).any():
        errors.append("Negative battery capacity found.")

    # 3. Related machine & worker counts check
    if machines_df is not None:
        mach_counts = machines_df.groupby("factory_id").size()
        for idx, row in df.iterrows():
            fid = row["factory_id"]
            actual = mach_counts.get(fid, 0)
            declared = row["number_of_machines"]
            if actual != declared:
                errors.append(f"Factory {fid} declared {declared} machines, but found {actual} in machines.csv")
                
    if workforce_df is not None:
        work_counts = workforce_df.groupby("factory_id").size()
        for idx, row in df.iterrows():
            fid = row["factory_id"]
            actual = work_counts.get(fid, 0)
            declared = row["number_of_workers"]
            if actual != declared:
                errors.append(f"Factory {fid} declared {declared} workers, but found {actual} in workforce.csv")

    metrics["total_factories"] = len(df)
    metrics["total_solar_capacity_kw"] = float(df["installed_solar_capacity_kw"].sum())
    metrics["total_grid_capacity_kw"] = float(df["grid_connection_capacity_kw"].sum())
    
    return DatasetCheckResult(
        dataset_name="FACTORIES",
        row_count=len(df),
        col_count=len(df.columns),
        is_valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
        metrics=metrics
    )

def validate_machines(df: pd.DataFrame, factories_df: pd.DataFrame = None) -> DatasetCheckResult:
    errors = []
    warnings = []
    metrics = {}
    
    if df["machine_id"].duplicated().any():
        errors.append("Duplicate machine_ids found.")
        
    if factories_df is not None:
        valid_fids = set(factories_df["factory_id"])
        orphan = df[~df["factory_id"].isin(valid_fids)]["factory_id"].tolist()
        if orphan:
            errors.append(f"Orphan machine factory_ids found: {set(orphan)}")
            
    if (df["rated_power_kw"] <= 0).any():
        errors.append("Non-positive rated_power_kw found.")
        
    if (df["standby_power_kw"] >= df["rated_power_kw"]).any():
        errors.append("Standby power >= rated power found in machines.")
        
    if (df["production_rate_units_per_hour"] <= 0).any():
        errors.append("Non-positive production rate found.")

    if (df["workers_required"] < 1).any():
        errors.append("Workers required < 1 found in machines.")

    sched_count = (df["maintenance_status"] == "Scheduled").sum()
    metrics["scheduled_maintenance_machines"] = int(sched_count)
    metrics["total_machines"] = len(df)

    return DatasetCheckResult(
        dataset_name="MACHINES",
        row_count=len(df),
        col_count=len(df.columns),
        is_valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
        metrics=metrics
    )

def validate_workforce(df: pd.DataFrame, factories_df: pd.DataFrame = None) -> DatasetCheckResult:
    errors = []
    warnings = []
    metrics = {}
    
    if df["worker_id"].duplicated().any():
        errors.append("Duplicate worker_ids found.")

    if factories_df is not None:
        valid_fids = set(factories_df["factory_id"])
        orphan = df[~df["factory_id"].isin(valid_fids)]["factory_id"].tolist()
        if orphan:
            errors.append(f"Orphan worker factory_ids found: {set(orphan)}")

    if (df["hourly_labour_cost"] <= 0).any():
        errors.append("Non-positive hourly labour cost found.")

    metrics["total_workers"] = len(df)
    metrics["avg_labour_cost"] = float(df["hourly_labour_cost"].mean())
    return DatasetCheckResult(
        dataset_name="WORKFORCE",
        row_count=len(df),
        col_count=len(df.columns),
        is_valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
        metrics=metrics
    )

def validate_production_jobs(df: pd.DataFrame, factories_df: pd.DataFrame = None, machines_df: pd.DataFrame = None) -> DatasetCheckResult:
    errors = []
    warnings = []
    metrics = {}

    if df["job_id"].duplicated().any():
        errors.append("Duplicate job_ids found.")

    if factories_df is not None:
        valid_fids = set(factories_df["factory_id"])
        orphan_fac = df[~df["factory_id"].isin(valid_fids)]
        if not orphan_fac.empty:
            errors.append(f"Orphan job factory_ids found: {len(orphan_fac)}")

    if machines_df is not None:
        mach_factory_map = dict(zip(machines_df["machine_id"], machines_df["factory_id"]))
        mismatched_factory = 0
        for _, row in df.iterrows():
            mid = row["eligible_machine_id"]
            jid_fac = row["factory_id"]
            if mid in mach_factory_map and mach_factory_map[mid] != jid_fac:
                mismatched_factory += 1
        if mismatched_factory > 0:
            errors.append(f"Job assigned to machine belonging to different factory in {mismatched_factory} records.")

    # Datetime consistency
    rel = pd.to_datetime(df["job_release_time"])
    dl = pd.to_datetime(df["deadline"])
    if (rel >= dl).any():
        errors.append("job_release_time >= deadline found in jobs.")

    metrics["total_jobs"] = len(df)
    metrics["shiftable_jobs"] = int(df["can_shift"].sum())
    metrics["high_priority_jobs"] = int((df["priority"] == "High").sum() + (df["priority"] == "Urgent").sum())
    
    return DatasetCheckResult(
        dataset_name="PRODUCTION JOBS",
        row_count=len(df),
        col_count=len(df.columns),
        is_valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
        metrics=metrics
    )

def validate_solar_weather(df: pd.DataFrame) -> DatasetCheckResult:
    errors = []
    warnings = []
    metrics = {}

    if df.duplicated(subset=["timestamp", "location"]).any():
        errors.append("Duplicate timestamp & location combinations in solar_weather.")

    # Solar capacity factor range [0, 1]
    if (df["solar_capacity_factor"] < 0).any() or (df["solar_capacity_factor"] > 1.05).any():
        errors.append("Solar capacity factor outside [0, 1] range.")

    # Night-time solar check (Hours 0-4 and 20-23 should have minimal solar factor)
    night_records = df[df["hour"].isin([0, 1, 2, 3, 21, 22, 23])]
    if (night_records["solar_capacity_factor"] > 0.1).any():
        warnings.append("Night-time solar capacity factor > 0.1 observed in some records.")

    # Check peak hours (11-14) have highest average solar
    midday_avg = df[df["hour"].isin([11, 12, 13])]["solar_capacity_factor"].mean()
    evening_avg = df[df["hour"].isin([20, 21, 22])]["solar_capacity_factor"].mean()
    if evening_avg > midday_avg:
        errors.append("Unphysical solar pattern detected: Evening solar factor exceeds midday peak!")

    metrics["total_hours"] = len(df)
    metrics["peak_midday_solar_factor"] = float(midday_avg)
    metrics["unique_locations"] = int(df["location"].nunique())

    return DatasetCheckResult(
        dataset_name="SOLAR WEATHER",
        row_count=len(df),
        col_count=len(df.columns),
        is_valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
        metrics=metrics
    )

def validate_electricity_tariffs(df: pd.DataFrame) -> DatasetCheckResult:
    errors = []
    warnings = []
    metrics = {}

    if (df["energy_rate_rs_per_kwh"] <= 0).any():
        errors.append("Non-positive energy rate in tariffs.")

    metrics["tariff_records"] = len(df)
    return DatasetCheckResult(
        dataset_name="ELECTRICITY TARIFFS",
        row_count=len(df),
        col_count=len(df.columns),
        is_valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
        metrics=metrics
    )

def validate_production_energy_history(df: pd.DataFrame) -> DatasetCheckResult:
    errors = []
    warnings = []
    metrics = {}

    # Formula check: energy_consumed_kwh = solar_energy_used_kwh + grid_energy_used_kwh
    diff_energy = np.abs(df["energy_consumed_kwh"] - (df["solar_energy_used_kwh"] + df["grid_energy_used_kwh"]))
    bad_energy = (diff_energy > 0.5).sum()
    if bad_energy > 0:
        errors.append(f"Historical energy formula mismatch (energy != solar + grid) in {bad_energy} rows.")

    # Formula check: total_operating_cost_rs = labour_cost_rs + electricity_cost_rs
    diff_cost = np.abs(df["total_operating_cost_rs"] - (df["labour_cost_rs"] + df["electricity_cost_rs"]))
    bad_cost = (diff_cost > 1.0).sum()
    if bad_cost > 0:
        errors.append(f"Historical cost formula mismatch (total != labour + elec) in {bad_cost} rows.")

    metrics["total_history_records"] = len(df)
    metrics["total_historical_energy_kwh"] = float(df["energy_consumed_kwh"].sum())
    metrics["total_historical_cost_rs"] = float(df["total_operating_cost_rs"].sum())

    return DatasetCheckResult(
        dataset_name="PRODUCTION ENERGY HISTORY",
        row_count=len(df),
        col_count=len(df.columns),
        is_valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
        metrics=metrics
    )

def run_full_system_validation(datasets: Dict[str, pd.DataFrame]) -> SystemValidationReport:
    """Executes full validation across all 7 datasets and relationships."""
    f_df = datasets["factories"]
    m_df = datasets["machines"]
    j_df = datasets["jobs"]
    w_df = datasets["workforce"]
    s_df = datasets["solar_weather"]
    t_df = datasets["tariffs"]
    h_df = datasets["history"]

    results = {
        "factories": validate_factories(f_df, m_df, w_df),
        "machines": validate_machines(m_df, f_df),
        "workforce": validate_workforce(w_df, f_df),
        "jobs": validate_production_jobs(j_df, f_df, m_df),
        "solar_weather": validate_solar_weather(s_df),
        "tariffs": validate_electricity_tariffs(t_df),
        "history": validate_production_energy_history(h_df)
    }

    all_valid = all(res.is_valid for res in results.values())
    summary_errs = []
    for k, res in results.items():
        summary_errs.extend(res.errors)

    logger.info(f"System Validation Complete. Overall Healthy: {all_valid}")
    return SystemValidationReport(
        is_healthy=all_valid,
        results=results,
        summary_errors=summary_errs
    )
