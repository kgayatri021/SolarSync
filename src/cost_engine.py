import os
import sys
import pandas as pd
import numpy as np
from typing import Dict, List, Any
from dataclasses import dataclass

if os.path.exists(r'D:\python_packages') and r'D:\python_packages' not in sys.path:
    sys.path.insert(0, r'D:\python_packages')

from src.logger import logger

@dataclass
class ScheduleMetrics:
    total_energy_kwh: float
    solar_energy_used_kwh: float
    grid_energy_used_kwh: float
    solar_utilization_percent: float
    grid_dependency_percent: float
    electricity_cost_rs: float
    labour_cost_rs: float
    overtime_cost_rs: float
    total_operating_cost_rs: float

@dataclass
class CostComparison:
    baseline: ScheduleMetrics
    optimized: ScheduleMetrics
    grid_reduction_kwh: float
    grid_reduction_percent: float
    solar_increase_kwh: float
    solar_increase_percent: float
    solar_utilization_improvement_percent: float
    electricity_cost_savings_rs: float
    total_cost_savings_rs: float
    cost_savings_percent: float

class CostEngine:
    def __init__(self, tariffs_df: pd.DataFrame):
        self.tariffs_df = tariffs_df.copy()
        
        # Build 24-hour tariff rates (default HT1 11kV tariff structure)
        self.hourly_tariff_rates = np.zeros(24)
        for h in range(24):
            if 18 <= h < 22: # Peak: 18:00 to 22:00
                self.hourly_tariff_rates[h] = 9.25
            elif 6 <= h < 18: # Normal: 06:00 to 18:00
                self.hourly_tariff_rates[h] = 7.25
            else: # Off-peak: 22:00 to 06:00
                self.hourly_tariff_rates[h] = 5.75

    def get_hourly_tariff_rate(self, hour: int, tariff_category: str = "HT1") -> float:
        """Returns tariff rate in Rs/kWh for a given hour index (0..23)."""
        h = int(hour) % 24
        if "LT3" in tariff_category:
            return 6.75
        return self.hourly_tariff_rates[h]

    def calculate_schedule_metrics(
        self, 
        hourly_demand_kw: np.ndarray, 
        hourly_solar_available_kw: np.ndarray,
        hourly_labour_cost_rs: np.ndarray = None,
        hourly_overtime_cost_rs: np.ndarray = None,
        tariff_category: str = "HT1"
    ) -> ScheduleMetrics:
        """
        Calculates exact energy, grid, solar, electricity cost, labour cost, and total operating cost metrics for a 24-hour profile.
        """
        hours = len(hourly_demand_kw)
        solar_used = np.zeros(hours)
        grid_used = np.zeros(hours)
        elec_cost = 0.0

        for h in range(hours):
            demand = max(0.0, float(hourly_demand_kw[h]))
            solar_avail = max(0.0, float(hourly_solar_available_kw[h]))
            
            s_used = min(demand, solar_avail)
            g_used = max(0.0, demand - s_used)
            
            solar_used[h] = s_used
            grid_used[h] = g_used
            
            rate = self.get_hourly_tariff_rate(h, tariff_category)
            elec_cost += g_used * rate

        tot_energy = float(np.sum(hourly_demand_kw))
        tot_solar_used = float(np.sum(solar_used))
        tot_grid_used = float(np.sum(grid_used))
        
        tot_solar_available = float(np.sum(hourly_solar_available_kw))
        solar_util = (tot_solar_used / tot_solar_available * 100.0) if tot_solar_available > 0 else 0.0
        grid_dep = (tot_grid_used / tot_energy * 100.0) if tot_energy > 0 else 0.0

        labour_cost = float(np.sum(hourly_labour_cost_rs)) if hourly_labour_cost_rs is not None else 0.0
        overtime_cost = float(np.sum(hourly_overtime_cost_rs)) if hourly_overtime_cost_rs is not None else 0.0
        tot_cost = elec_cost + labour_cost + overtime_cost

        return ScheduleMetrics(
            total_energy_kwh=tot_energy,
            solar_energy_used_kwh=tot_solar_used,
            grid_energy_used_kwh=tot_grid_used,
            solar_utilization_percent=round(solar_util, 2),
            grid_dependency_percent=round(grid_dep, 2),
            electricity_cost_rs=round(elec_cost, 2),
            labour_cost_rs=round(labour_cost, 2),
            overtime_cost_rs=round(overtime_cost, 2),
            total_operating_cost_rs=round(tot_cost, 2)
        )

    def compare_schedules(self, baseline: ScheduleMetrics, optimized: ScheduleMetrics) -> CostComparison:
        """Compares baseline vs optimized schedule metrics."""
        grid_reduction = baseline.grid_energy_used_kwh - optimized.grid_energy_used_kwh
        grid_red_pct = (grid_reduction / baseline.grid_energy_used_kwh * 100.0) if baseline.grid_energy_used_kwh > 0 else 0.0
        
        solar_increase = optimized.solar_energy_used_kwh - baseline.solar_energy_used_kwh
        solar_increase_pct = (solar_increase / baseline.solar_energy_used_kwh * 100.0) if baseline.solar_energy_used_kwh > 0 else 0.0
        solar_util_imp = optimized.solar_utilization_percent - baseline.solar_utilization_percent

        elec_savings = baseline.electricity_cost_rs - optimized.electricity_cost_rs
        total_savings = baseline.total_operating_cost_rs - optimized.total_operating_cost_rs
        savings_pct = (total_savings / baseline.total_operating_cost_rs * 100.0) if baseline.total_operating_cost_rs > 0 else 0.0

        return CostComparison(
            baseline=baseline,
            optimized=optimized,
            grid_reduction_kwh=round(grid_reduction, 2),
            grid_reduction_percent=round(grid_red_pct, 2),
            solar_increase_kwh=round(solar_increase, 2),
            solar_increase_percent=round(solar_increase_pct, 2),
            solar_utilization_improvement_percent=round(solar_util_imp, 2),
            electricity_cost_savings_rs=round(elec_savings, 2),
            total_cost_savings_rs=round(total_savings, 2),
            cost_savings_percent=round(savings_pct, 2)
        )
