import os
import sys
import pandas as pd
import numpy as np
from typing import Dict, List, Any
from dataclasses import dataclass

if os.path.exists(r'D:\python_packages') and r'D:\python_packages' not in sys.path:
    sys.path.insert(0, r'D:\python_packages')

from src.scheduler import SolarShiftScheduler, ScheduleResult
from src.demand_engine import DemandEngine
from src.logger import logger

@dataclass
class ScenarioParams:
    scenario_name: str
    factory_id: str
    target_date: str
    cloud_factor: float = 1.0 # 1.0 normal, 0.5 heavy cloud
    solar_capacity_multiplier: float = 1.0 # 1.0 current, 1.5 expansion
    demand_multiplier: float = 1.0 # 1.0 normal, 1.3 high demand
    workforce_availability_factor: float = 1.0 # 1.0 full, 0.8 limited
    tariff_peak_multiplier: float = 1.0 # 1.0 standard, 1.2 rate hike

@dataclass
class ScenarioResult:
    params: ScenarioParams
    baseline_result: ScheduleResult
    scenario_result: ScheduleResult
    impact_summary: Dict[str, Any]

class ScenarioEngine:
    def __init__(self, scheduler: SolarShiftScheduler, demand_engine: DemandEngine):
        self.scheduler = scheduler
        self.demand_engine = demand_engine

    def run_scenario(self, params: ScenarioParams) -> ScenarioResult:
        """Executes full schedule recalculation under simulated scenario conditions."""
        logger.info(f"Running Scenario '{params.scenario_name}' for Factory {params.factory_id} on {params.target_date}")
        
        # 1. Fetch jobs
        jobs = self.demand_engine.get_jobs_for_factory_and_date(params.factory_id, params.target_date)
        
        # Apply demand multiplier if > 1.0
        if params.demand_multiplier != 1.0:
            jobs = jobs.copy()
            jobs["estimated_duration_hours"] = jobs["estimated_duration_hours"] * params.demand_multiplier

        # 2. Run Baseline (Normal condition) schedule run
        base_run = self.scheduler.optimize_schedule(
            factory_id=params.factory_id,
            target_date=params.target_date,
            jobs_df=jobs,
            cloud_factor=1.0,
            solar_multiplier=1.0
        )

        # 3. Run Scenario schedule run
        scenario_run = self.scheduler.optimize_schedule(
            factory_id=params.factory_id,
            target_date=params.target_date,
            jobs_df=jobs,
            cloud_factor=params.cloud_factor,
            solar_multiplier=params.solar_capacity_multiplier
        )

        # 4. Compare baseline vs scenario impact
        diff_grid_kwh = scenario_run.optimized_metrics.grid_energy_used_kwh - base_run.optimized_metrics.grid_energy_used_kwh
        diff_solar_kwh = scenario_run.optimized_metrics.solar_energy_used_kwh - base_run.optimized_metrics.solar_energy_used_kwh
        diff_cost_rs = scenario_run.optimized_metrics.total_operating_cost_rs - base_run.optimized_metrics.total_operating_cost_rs

        impact = {
            "scenario_name": params.scenario_name,
            "grid_energy_change_kwh": round(diff_grid_kwh, 2),
            "solar_energy_change_kwh": round(diff_solar_kwh, 2),
            "cost_change_rs": round(diff_cost_rs, 2),
            "scenario_savings_rs": scenario_run.comparison.total_cost_savings_rs,
            "scenario_solar_utilization": scenario_run.optimized_metrics.solar_utilization_percent
        }

        return ScenarioResult(
            params=params,
            baseline_result=base_run,
            scenario_result=scenario_run,
            impact_summary=impact
        )
