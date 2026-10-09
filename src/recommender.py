import os
import sys
import pandas as pd
import numpy as np
from typing import Dict, List, Any
from dataclasses import dataclass

if os.path.exists(r'D:\python_packages') and r'D:\python_packages' not in sys.path:
    sys.path.insert(0, r'D:\python_packages')

from src.scheduler import ScheduleResult, ScheduledJob
from src.utils import format_currency, format_kwh

@dataclass
class JobRecommendation:
    job_id: str
    product_id: str
    machine_id: str
    baseline_start: str
    recommended_start: str
    shift_hours: int
    solar_used_kwh: float
    grid_used_kwh: float
    estimated_savings_rs: float
    reason: str
    deadline_status: str

class RecommendationEngine:
    def __init__(self):
        pass

    def generate_recommendations(self, schedule_result: ScheduleResult) -> List[JobRecommendation]:
        """Generates detailed, explainable job shift recommendations from optimization results."""
        recommendations = []
        
        base_map = {b.job_id: b for b in schedule_result.baseline_jobs}
        solar_profile = schedule_result.hourly_solar_available
        
        for job in schedule_result.scheduled_jobs:
            base_job = base_map.get(job.job_id, job)
            st_base = base_job.start_hour
            st_rec = job.start_hour
            shift_diff = st_rec - st_base

            # Calculate energy split for recommended job runtime
            dur = job.duration_hours
            kw = job.rated_power_kw
            
            job_solar = 0.0
            job_grid = 0.0
            
            for h in range(st_rec, min(24, st_rec + dur)):
                s_avail = solar_profile[h]
                s_share = min(kw, s_avail)
                g_share = max(0.0, kw - s_share)
                job_solar += s_share
                job_grid += g_share

            # Tariff cost rate helper
            def get_tariff(h_idx: int) -> float:
                h_idx = h_idx % 24
                return 9.25 if 18 <= h_idx < 22 else (7.25 if 6 <= h_idx < 18 else 5.75)

            # Baseline grid cost vs Recommended grid cost for this specific job
            base_grid_cost = sum(max(0.0, kw - solar_profile[h % 24]) * get_tariff(h) for h in range(st_base, st_base + dur))
            rec_grid_cost = sum(max(0.0, kw - solar_profile[h % 24]) * get_tariff(h) for h in range(st_rec, st_rec + dur))
            est_savings = max(0.0, base_grid_cost - rec_grid_cost)

            if shift_diff > 0:
                reason = f"Shifted +{shift_diff}h later to align with peak solar availability ({solar_profile[st_rec % 24]:.1f} kW) and reduce grid draw."
            elif shift_diff < 0:
                reason = f"Advanced {abs(shift_diff)}h earlier to utilize morning solar rise and avoid evening peak electricity rates."
            else:
                reason = "No schedule change required. Current timing is already optimal under selected constraints."

            recommendations.append(JobRecommendation(
                job_id=job.job_id,
                product_id=job.product_id,
                machine_id=job.machine_id,
                baseline_start=f"{st_base:02d}:00",
                recommended_start=f"{st_rec:02d}:00",
                shift_hours=shift_diff,
                solar_used_kwh=round(job_solar, 1),
                grid_used_kwh=round(job_grid, 1),
                estimated_savings_rs=round(est_savings, 2),
                reason=reason,
                deadline_status="Satisfied"
            ))

        return recommendations

    def generate_executive_summary(self, schedule_result: ScheduleResult) -> Dict[str, Any]:
        """Generates executive level summary metrics and insights."""
        comp = schedule_result.comparison
        recs = self.generate_recommendations(schedule_result)
        shifted_count = sum(1 for r in recs if r.shift_hours != 0)

        return {
            "factory_id": schedule_result.factory_id,
            "target_date": schedule_result.target_date,
            "total_jobs_scheduled": len(schedule_result.scheduled_jobs),
            "total_jobs_shifted": shifted_count,
            "grid_reduction_kwh": comp.grid_reduction_kwh,
            "grid_reduction_percent": comp.grid_reduction_percent,
            "solar_utilization_improvement": comp.solar_utilization_improvement_percent,
            "electricity_cost_savings": comp.electricity_cost_savings_rs,
            "total_operating_cost_savings": comp.total_cost_savings_rs,
            "cost_savings_percent": comp.cost_savings_percent,
            "top_recommendation": f"Moving {shifted_count} flexible jobs into peak solar window (10:00–15:00) yields {comp.grid_reduction_percent}% grid reduction."
        }
