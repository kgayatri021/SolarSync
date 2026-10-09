import os
import sys
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any, Optional

if os.path.exists(r'D:\python_packages') and r'D:\python_packages' not in sys.path:
    sys.path.insert(0, r'D:\python_packages')

from src.utils import parse_time_str
from src.logger import logger

class WorkforceOptimizer:
    def __init__(self, workforce_df: pd.DataFrame, machines_df: pd.DataFrame):
        self.workforce_df = workforce_df.copy()
        self.machines_df = machines_df.copy()
        self.machine_map = self.machines_df.set_index("machine_id").to_dict(orient="index")

    def get_workers_for_factory(self, factory_id: str) -> pd.DataFrame:
        """Returns workforce available for a specific factory."""
        return self.workforce_df[self.workforce_df["factory_id"] == factory_id].copy()

    def get_hourly_worker_capacity(self, factory_id: str) -> Dict[str, np.ndarray]:
        """
        Calculates hourly worker supply for a factory across 24 hours (0..23).
        Returns dict with:
        - total_workers_available: 24-len array
        - total_hourly_regular_cost: 24-len array
        - skill_capacity: dict of skill_level -> 24-len array
        """
        workers = self.get_workers_for_factory(factory_id)
        supply = np.zeros(24, dtype=int)
        hourly_cost = np.zeros(24, dtype=float)
        skill_supply = {}

        if workers.empty:
            # Fallback uniform supply if factory workforce data empty
            return {
                "total_workers_available": np.full(24, 10),
                "total_hourly_regular_cost": np.full(24, 1500.0),
                "skill_capacity": {"Level 1": np.full(24, 10), "Level 2": np.full(24, 10), "Level 3": np.full(24, 10)}
            }

        for _, w in workers.iterrows():
            st_hour = int(parse_time_str(str(w.get("shift_start", "08:00"))))
            end_hour = int(parse_time_str(str(w.get("shift_end", "16:00"))))
            cost = float(w.get("hourly_labour_cost", 150.0))
            skill = str(w.get("skill_level", "Level 1"))

            if skill not in skill_supply:
                skill_supply[skill] = np.zeros(24, dtype=int)

            if end_hour > st_hour:
                hours_range = range(st_hour, end_hour)
            else:
                # Night shift crossing midnight
                hours_range = list(range(st_hour, 24)) + list(range(0, max(1, end_hour)))

            for h in hours_range:
                if 0 <= h < 24:
                    supply[h] += 1
                    hourly_cost[h] += cost
                    skill_supply[skill][h] += 1

        return {
            "total_workers_available": supply,
            "total_hourly_regular_cost": hourly_cost,
            "skill_capacity": skill_supply
        }

    def evaluate_schedule_staffing(
        self, 
        factory_id: str, 
        hourly_jobs_running: List[List[Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """
        Evaluates staffing feasibility for a scheduled 24-hour job plan.
        `hourly_jobs_running` is a list of 24 lists containing running jobs at each hour.
        """
        capacity = self.get_hourly_worker_capacity(factory_id)
        supply = capacity["total_workers_available"]
        
        hourly_workers_needed = np.zeros(24, dtype=int)
        hourly_labour_cost = np.zeros(24, dtype=float)
        hourly_overtime_cost = np.zeros(24, dtype=float)
        shortages = []

        workers_df = self.get_workers_for_factory(factory_id)
        avg_rate = workers_df["hourly_labour_cost"].mean() if not workers_df.empty else 150.0
        avg_ot_rate = workers_df["overtime_cost_per_hour"].mean() if not workers_df.empty and "overtime_cost_per_hour" in workers_df.columns else avg_rate * 1.5

        for h in range(24):
            jobs = hourly_jobs_running[h]
            needed = sum(int(j.get("workers_required", 1)) for j in jobs)
            hourly_workers_needed[h] = needed

            avail = supply[h]
            if needed <= avail:
                hourly_labour_cost[h] = needed * avg_rate
            else:
                # Overtime or extra staffing required
                regular_workers = avail
                overtime_workers = needed - avail
                hourly_labour_cost[h] = regular_workers * avg_rate
                hourly_overtime_cost[h] = overtime_workers * avg_ot_rate
                shortages.append({"hour": h, "needed": needed, "available": avail, "shortage": overtime_workers})

        is_feasible = len(shortages) == 0
        return {
            "is_feasible": is_feasible,
            "hourly_workers_needed": hourly_workers_needed,
            "hourly_workers_available": supply,
            "total_labour_cost": float(np.sum(hourly_labour_cost)),
            "total_overtime_cost": float(np.sum(hourly_overtime_cost)),
            "shortages": shortages
        }
