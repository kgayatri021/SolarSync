import os
import sys
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass

if os.path.exists(r'D:\python_packages') and r'D:\python_packages' not in sys.path:
    sys.path.insert(0, r'D:\python_packages')

from ortools.sat.python import cp_model
from src.utils import parse_time_str
from src.solar_engine import SolarEngine
from src.cost_engine import CostEngine, ScheduleMetrics, CostComparison
from src.workforce_optimizer import WorkforceOptimizer
from src.logger import logger

@dataclass
class ScheduledJob:
    job_id: str
    product_id: str
    product_type: str
    machine_id: str
    start_hour: int
    end_hour: int
    duration_hours: int
    rated_power_kw: float
    energy_required_kwh: float
    workers_required: int
    priority: str
    can_shift: bool
    reason: str = ""

@dataclass
class ScheduleResult:
    factory_id: str
    target_date: str
    solver_status: str
    baseline_metrics: ScheduleMetrics
    optimized_metrics: ScheduleMetrics
    comparison: CostComparison
    scheduled_jobs: List[ScheduledJob]
    baseline_jobs: List[ScheduledJob]
    hourly_solar_available: np.ndarray
    hourly_baseline_demand: np.ndarray
    hourly_optimized_demand: np.ndarray

class SolarSyncScheduler:
    def __init__(
        self, 
        solar_engine: SolarEngine, 
        cost_engine: CostEngine,
        workforce_optimizer: WorkforceOptimizer,
        machines_df: pd.DataFrame,
        factories_df: pd.DataFrame
    ):
        self.solar_engine = solar_engine
        self.cost_engine = cost_engine
        self.workforce_optimizer = workforce_optimizer
        self.machines_df = machines_df.copy()
        self.factories_df = factories_df.copy()

        self.machine_map = self.machines_df.set_index("machine_id").to_dict(orient="index")
        self.factory_map = self.factories_df.set_index("factory_id").to_dict(orient="index")

    def create_baseline_schedule(self, jobs_df: pd.DataFrame) -> List[ScheduledJob]:
        """Creates baseline schedule running each job at its release time."""
        baseline_jobs = []
        for _, j in jobs_df.iterrows():
            jid = j["job_id"]
            mid = j["eligible_machine_id"]
            mach = self.machine_map.get(mid, {})
            rated_kw = float(mach.get("rated_power_kw", 10.0))

            duration = int(np.ceil(float(j.get("duration_hours", j.get("estimated_duration_hours", 1)))))
            duration = max(1, duration)

            rel_time = pd.to_datetime(j["job_release_time"])
            start_hour = int(rel_time.hour) % 24
            end_hour = min(24, start_hour + duration)

            baseline_jobs.append(ScheduledJob(
                job_id=jid,
                product_id=str(j.get("product_id", "")),
                product_type=str(j.get("product_type", "")),
                machine_id=mid,
                start_hour=start_hour,
                end_hour=end_hour,
                duration_hours=duration,
                rated_power_kw=rated_kw,
                energy_required_kwh=rated_kw * duration,
                workers_required=int(j.get("workers_required", 1)),
                priority=str(j.get("priority", "Medium")),
                can_shift=bool(j.get("can_shift", True)),
                reason="Baseline start at release time"
            ))
        return baseline_jobs

    def _jobs_to_hourly_demand(self, scheduled_jobs: List[ScheduledJob]) -> np.ndarray:
        """Converts scheduled jobs into 24-hour power demand vector."""
        demand = np.zeros(24, dtype=float)
        for job in scheduled_jobs:
            st = job.start_hour
            et = min(24, job.end_hour)
            for h in range(st, et):
                demand[h] += job.rated_power_kw
        return demand

    def optimize_schedule(
        self, 
        factory_id: str, 
        target_date: str, 
        jobs_df: pd.DataFrame,
        cloud_factor: float = 1.0,
        solar_multiplier: float = 1.0,
        priority_weight: float = 1.0,
        time_limit_seconds: int = 10
    ) -> ScheduleResult:
        """
        Runs OR-Tools CP-SAT optimizer to shift flexible production jobs to peak solar hours.
        """
        logger.info(f"Starting OR-Tools CP-SAT optimization for Factory {factory_id} on {target_date}")
        
        # 1. Get solar profile
        solar_avail = self.solar_engine.get_hourly_solar_array(factory_id, target_date, cloud_factor, solar_multiplier)
        
        # 2. Get baseline schedule
        baseline_jobs = self.create_baseline_schedule(jobs_df)
        baseline_demand = self._jobs_to_hourly_demand(baseline_jobs)
        
        # 3. CP-SAT Optimization Model Setup
        model = cp_model.CpModel()

        # Build OR-Tools variables per job
        job_vars = {}
        machine_intervals = {} # machine_id -> list of interval vars
        
        # Scale factor for precision in integer solver
        SCALE = 10 

        for _, j in jobs_df.iterrows():
            jid = j["job_id"]
            mid = j["eligible_machine_id"]
            mach = self.machine_map.get(mid, {})
            rated_kw = float(mach.get("rated_power_kw", 10.0))

            duration = int(np.ceil(float(j.get("duration_hours", j.get("estimated_duration_hours", 1)))))
            duration = max(1, duration)

            rel_time = pd.to_datetime(j["job_release_time"])
            dl_time = pd.to_datetime(j["deadline"])
            
            # Start bounds
            rel_hour = int(rel_time.hour) % 24
            dl_hour = int(dl_time.hour) if dl_time.date() == rel_time.date() else 24
            dl_hour = min(24, max(rel_hour + duration, dl_hour))

            can_shift = bool(j.get("can_shift", True))

            if not can_shift:
                min_start = rel_hour
                max_start = rel_hour
            else:
                min_start = rel_hour
                max_start = max(rel_hour, dl_hour - duration)

            start_var = model.NewIntVar(min_start, max_start, f"start_{jid}")
            end_var = model.NewIntVar(min_start + duration, max_start + duration, f"end_{jid}")
            interval_var = model.NewIntervalVar(start_var, duration, end_var, f"interval_{jid}")

            job_vars[jid] = {
                "start_var": start_var,
                "end_var": end_var,
                "interval_var": interval_var,
                "duration": duration,
                "rated_kw": rated_kw,
                "machine_id": mid,
                "workers_required": int(j.get("workers_required", 1)),
                "priority": str(j.get("priority", "Medium")),
                "can_shift": can_shift,
                "product_id": str(j.get("product_id", "")),
                "product_type": str(j.get("product_type", ""))
            }

            if mid not in machine_intervals:
                machine_intervals[mid] = []
            machine_intervals[mid].append(interval_var)

        # Constraint 1: Machine No-Overlap (Single job on a machine at a time)
        for mid, intervals in machine_intervals.items():
            if len(intervals) > 1:
                model.AddNoOverlap(intervals)

        # Constraint 2: Maintenance window constraint
        target_dt_obj = pd.to_datetime(target_date).date()
        for mid, mach_info in self.machine_map.items():
            m_status = str(mach_info.get("maintenance_status", "None"))
            if m_status == "Scheduled" and mid in machine_intervals:
                m_st_str = mach_info.get("maintenance_start_time")
                m_end_str = mach_info.get("maintenance_end_time")
                if pd.notna(m_st_str) and pd.notna(m_end_str):
                    try:
                        st_dt = pd.to_datetime(m_st_str)
                        end_dt = pd.to_datetime(m_end_str)
                        if st_dt.date() <= target_dt_obj <= end_dt.date():
                            m_st = st_dt.hour if st_dt.date() == target_dt_obj else 0
                            m_et = end_dt.hour if end_dt.date() == target_dt_obj else 24
                            if m_et > m_st:
                                for interval in machine_intervals[mid]:
                                    jid_key = interval.Name().replace("interval_", "")
                                    if jid_key in job_vars:
                                        s_v = job_vars[jid_key]["start_var"]
                                        e_v = job_vars[jid_key]["end_var"]
                                        b1 = model.NewBoolVar(f"before_maint_{jid_key}")
                                        b2 = model.NewBoolVar(f"after_maint_{jid_key}")
                                        model.Add(e_v <= m_st).OnlyEnforceIf(b1)
                                        model.Add(s_v >= m_et).OnlyEnforceIf(b2)
                                        model.AddOr([b1, b2])
                    except Exception as ex:
                        logger.warning(f"Could not parse maintenance window for machine {mid}: {ex}")

        # Hourly Demand & Objective Formulation
        hourly_demand_vars = []
        cost_vars = []
        
        # Grid connection capacity constraint
        fac_info = self.factory_map.get(factory_id, {})
        grid_cap_kw = float(fac_info.get("grid_connection_capacity_kw", 1000.0))
        grid_cap_scaled = int(grid_cap_kw * SCALE)

        for h in range(24):
            # Active boolean for each job at hour h
            active_bools = []
            power_terms = []

            for jid, info in job_vars.items():
                s_v = info["start_var"]
                e_v = info["end_var"]
                active_h = model.NewBoolVar(f"active_{jid}_{h}")
                
                # active_h is true iff s_v <= h and e_v > h
                b_start = model.NewBoolVar(f"b_start_{jid}_{h}")
                b_end = model.NewBoolVar(f"b_end_{jid}_{h}")
                model.Add(s_v <= h).OnlyEnforceIf(b_start)
                model.Add(s_v > h).OnlyEnforceIf(b_start.Not())
                model.Add(e_v > h).OnlyEnforceIf(b_end)
                model.Add(e_v <= h).OnlyEnforceIf(b_end.Not())
                
                model.AddBoolAnd([b_start, b_end]).OnlyEnforceIf(active_h)
                model.AddBoolOr([b_start.Not(), b_end.Not()]).OnlyEnforceIf(active_h.Not())

                active_bools.append(active_h)
                p_scaled = int(info["rated_kw"] * SCALE)
                power_terms.append((active_h, p_scaled))

            # Total hourly demand variable
            demand_h_var = model.NewIntVar(0, grid_cap_scaled * 2, f"demand_{h}")
            model.Add(demand_h_var == sum(b * p for b, p in power_terms))
            model.Add(demand_h_var <= grid_cap_scaled) # Enforce grid capacity limit

            hourly_demand_vars.append(demand_h_var)

            # Grid Energy Used = max(0, demand_h - solar_h)
            solar_scaled = int(solar_avail[h] * SCALE)
            grid_h_var = model.NewIntVar(0, grid_cap_scaled * 2, f"grid_{h}")
            model.Add(grid_h_var >= demand_h_var - solar_scaled)
            model.Add(grid_h_var >= 0)

            # Tariff cost at hour h
            tariff_rate = self.cost_engine.get_hourly_tariff_rate(h)
            rate_int = int(round(tariff_rate * 100)) # Scale tariff rate
            
            cost_h_var = model.NewIntVar(0, 10000000, f"cost_{h}")
            model.Add(cost_h_var == grid_h_var * rate_int)
            cost_vars.append(cost_h_var)

        # Minimize Total Electricity Cost
        model.Minimize(sum(cost_vars))

        # 4. Solve Model
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = float(time_limit_seconds)
        solver.parameters.num_workers = 4
        status = solver.Solve(model)

        status_name = solver.StatusName(status)
        logger.info(f"OR-Tools Solver Status: {status_name}")

        scheduled_jobs = []
        if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            for jid, info in job_vars.items():
                st_val = int(solver.Value(info["start_var"]))
                dur = info["duration"]
                et_val = st_val + dur

                # Determine recommendation rationale
                baseline_job = next((b for b in baseline_jobs if b.job_id == jid), None)
                base_st = baseline_job.start_hour if baseline_job else st_val
                
                st_idx = min(23, max(0, st_val))
                if st_val != base_st:
                    reason = f"Shifted from {base_st:02d}:00 to {st_val:02d}:00 to align with solar peak ({solar_avail[st_idx]:.1f} kW) and lower grid tariff."
                else:
                    reason = f"Kept at {st_val:02d}:00 due to deadline or tight availability window."

                scheduled_jobs.append(ScheduledJob(
                    job_id=jid,
                    product_id=info["product_id"],
                    product_type=info["product_type"],
                    machine_id=info["machine_id"],
                    start_hour=st_val,
                    end_hour=et_val,
                    duration_hours=dur,
                    rated_power_kw=info["rated_kw"],
                    energy_required_kwh=info["rated_kw"] * dur,
                    workers_required=info["workers_required"],
                    priority=info["priority"],
                    can_shift=info["can_shift"],
                    reason=reason
                ))
        else:
            logger.warning("CP-SAT solver infeasible or timed out. Falling back to baseline schedule.")
            scheduled_jobs = baseline_jobs

        optimized_demand = self._jobs_to_hourly_demand(scheduled_jobs)

        # 5. Compute baseline vs optimized metrics
        base_metrics = self.cost_engine.calculate_schedule_metrics(baseline_demand, solar_avail)
        opt_metrics = self.cost_engine.calculate_schedule_metrics(optimized_demand, solar_avail)
        comparison = self.cost_engine.compare_schedules(base_metrics, opt_metrics)

        return ScheduleResult(
            factory_id=factory_id,
            target_date=target_date,
            solver_status=status_name,
            baseline_metrics=base_metrics,
            optimized_metrics=opt_metrics,
            comparison=comparison,
            scheduled_jobs=scheduled_jobs,
            baseline_jobs=baseline_jobs,
            hourly_solar_available=solar_avail,
            hourly_baseline_demand=baseline_demand,
            hourly_optimized_demand=optimized_demand
        )

SolarShiftScheduler = SolarSyncScheduler
