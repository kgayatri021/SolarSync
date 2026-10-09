import os
import sys
from dataclasses import dataclass
from typing import Dict, Any, List

if os.path.exists(r'D:\python_packages') and r'D:\python_packages' not in sys.path:
    sys.path.insert(0, r'D:\python_packages')

from src.utils import format_currency, format_kwh

@dataclass
class ResultState:
    code: str  # "IMPROVED", "NO_CHANGE", "NO_BENEFIT", "INFEASIBLE"
    title: str
    subtitle: str
    banner_bg: str
    border_color: str
    text_color: str
    grid_delta_text: str
    solar_delta_text: str
    cost_delta_text: str
    reasons: List[str]
    is_feasible: bool

def evaluate_result_state(
    solver_status: str,
    shifted_count: int,
    baseline_grid_kwh: float,
    optimized_grid_kwh: float,
    baseline_solar_kwh: float,
    optimized_solar_kwh: float,
    baseline_cost_rs: float,
    optimized_cost_rs: float,
    limiting_constraint: str = None
) -> ResultState:
    """
    Unified Result State Engine enforcing strict mathematical consistency
    and non-contradictory messaging across SOLAR SYNC.
    """
    grid_diff = optimized_grid_kwh - baseline_grid_kwh  # negative means reduction
    solar_diff = optimized_solar_kwh - baseline_solar_kwh # positive means increase
    cost_diff = optimized_cost_rs - baseline_cost_rs    # negative means savings

    # 1. INFEASIBLE STATE
    if solver_status in ("INFEASIBLE", "MODEL_INVALID", "UNKNOWN"):
        reason_msg = limiting_constraint or "No production schedule satisfies all selected machine, workforce, maintenance, and deadline constraints."
        return ResultState(
            code="INFEASIBLE",
            title="NO FEASIBLE SCHEDULE",
            subtitle=f"No production schedule satisfies all selected constraints. ({reason_msg})",
            banner_bg="#FEE2E2",
            border_color="#DC2626",
            text_color="#991B1B",
            grid_delta_text="Grid Draw: N/A",
            solar_delta_text="Solar Used: N/A",
            cost_delta_text="Electricity Cost: N/A",
            reasons=[
                f"Limiting Constraint: {reason_msg}",
                "Optimized schedule is disabled because solver could not satisfy all operational bounds.",
                "Review machine maintenance, job release times, and worker shift availability."
            ],
            is_feasible=False
        )

    # 2. NO BENEFIT STATE (Cost increased or grid draw increased without benefit)
    if cost_diff > 0.01:
        return ResultState(
            code="NO_BENEFIT",
            title="NO BENEFIT IDENTIFIED",
            subtitle=f"The selected parameters increase modeled electricity cost by {format_currency(cost_diff)}. No schedule change is recommended.",
            banner_bg="#FFEDD5",
            border_color="#EA580C",
            text_color="#9A3412",
            grid_delta_text=f"Grid Draw: +{grid_diff:.1f} kWh" if grid_diff > 0 else f"Grid Draw: {grid_diff:.1f} kWh",
            solar_delta_text=f"Solar Used: {solar_diff:+.1f} kWh",
            cost_delta_text=f"Cost Increase: +{format_currency(cost_diff)}",
            reasons=[
                f"Modeled electricity cost increases by {format_currency(cost_diff)} under this scenario.",
                "Shifting jobs under these constraints would increase grid peak charges.",
                "The default baseline schedule is retained to prevent financial loss."
            ],
            is_feasible=True
        )

    # 3. NO CHANGE STATE (Optimal schedule matches baseline / 0 jobs shifted)
    if shifted_count == 0 or (abs(cost_diff) <= 0.01 and abs(grid_diff) <= 0.01):
        return ResultState(
            code="NO_CHANGE",
            title="NO SCHEDULE CHANGE REQUIRED",
            subtitle="The existing schedule is already optimal under the selected constraints.",
            banner_bg="#FEF3C7",
            border_color="#D97706",
            text_color="#92400E",
            grid_delta_text="Grid Draw: No Change (0.0 kWh)",
            solar_delta_text="Solar Used: No Change (0.0 kWh)",
            cost_delta_text="Electricity Cost: No Change (₹0.00)",
            reasons=[
                "The current job release timing already aligns with peak solar generation hours.",
                "Flexible jobs are tightly bounded by strict deadline windows or machine availability.",
                "No additional job shift yields further cost reduction or grid reduction."
            ],
            is_feasible=True
        )

    # 4. IMPROVED STATE
    grid_red_kwh = abs(grid_diff)
    cost_sav_rs = abs(cost_diff)
    grid_pct = (grid_red_kwh / baseline_grid_kwh * 100) if baseline_grid_kwh > 0 else 0.0
    cost_pct = (cost_sav_rs / baseline_cost_rs * 100) if baseline_cost_rs > 0 else 0.0

    return ResultState(
        code="IMPROVED",
        title="SOLAR SYNC RECOMMENDS A SCHEDULE CHANGE",
        subtitle=f"Recommended shifting {shifted_count} flexible job{'s' if shifted_count!=1 else ''} into peak solar window — Reduces grid draw by {grid_red_kwh:.1f} kWh ({grid_pct:.1f}%) and saves {format_currency(cost_sav_rs)} ({cost_pct:.1f}%).",
        banner_bg="#ECFDF5",
        border_color="#059669",
        text_color="#065F46",
        grid_delta_text=f"Grid Reduced: -{grid_red_kwh:.1f} kWh (↓{grid_pct:.1f}%)",
        solar_delta_text=f"Solar Increased: +{solar_diff:.1f} kWh",
        cost_delta_text=f"Cost Saved: {format_currency(cost_sav_rs)} (↓{cost_pct:.1f}%)",
        reasons=[
            f"Shifted {shifted_count} flexible jobs into the 10:00–14:00 peak solar generation window.",
            f"Avoided HT1 Peak tariff rates (18:00–22:00 @ ₹9.25/kWh) by shifting production to zero-marginal-cost solar hours.",
            "Respects machine non-overlap, maintenance schedules, workforce shift capacity, and product deadlines."
        ],
        is_feasible=True
    )
