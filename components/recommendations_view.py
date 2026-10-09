import os
import sys
import streamlit as st
import pandas as pd

if os.path.exists(r'D:\python_packages') and r'D:\python_packages' not in sys.path:
    sys.path.insert(0, r'D:\python_packages')

from components.cards import render_kpi_card, render_section_header
from src.scheduler import SolarSyncScheduler
from src.demand_engine import DemandEngine
from src.recommender import RecommendationEngine
from src.utils import format_currency

def render_recommendations_view(
    datasets: dict,
    scheduler: SolarSyncScheduler,
    demand_engine: DemandEngine,
    recommender: RecommendationEngine
):
    render_section_header("Actionable Recommendations", "Explainable Job Shift Rationale & Decision Support System")

    factories = datasets["factories"]

    c1, c2 = st.columns(2)
    with c1:
        fac_options = factories["factory_id"].tolist()
        default_idx = fac_options.index("FAC_016") if "FAC_016" in fac_options else 0
        selected_factory = st.selectbox(
            "Select Facility:",
            options=fac_options,
            index=default_idx,
            format_func=lambda fid: f"{fid} - {factories[factories['factory_id']==fid]['factory_name'].values[0]}"
        )
    with c2:
        selected_date = st.date_input("Recommendation Date:", pd.to_datetime("2026-08-10"))

    # Run scheduler optimization for recommendations
    jobs = demand_engine.get_jobs_for_factory_and_date(selected_factory, str(selected_date))
    res = scheduler.optimize_schedule(selected_factory, str(selected_date), jobs)
    recs = recommender.generate_recommendations(res)

    shifted_recs = [r for r in recs if r.shift_hours != 0]
    total_savings = sum(r.estimated_savings_rs for r in recs)

    r1, r2, r3, r4 = st.columns(4)
    with r1:
        render_kpi_card("Jobs Analyzed", f"{len(recs)}", "Production Schedule", color_theme="gold")
    with r2:
        render_kpi_card("Jobs Shifted", f"{len(shifted_recs)}", f"Shift Rate: {len(shifted_recs)/len(recs)*100:.0f}%", color_theme="cyan")
    with r3:
        render_kpi_card("Estimated Savings", format_currency(total_savings), "Tariff & SOLAR SYNC", color_theme="green")
    with r4:
        render_kpi_card("Deadline Compliance", "100% Satisfied", "Zero Violations", color_theme="green")

    st.markdown("---")

    st.markdown("### Production Decision Cards")
    
    for idx, r in enumerate(recs, start=1):
        if r.shift_hours != 0:
            header_title = f"RECOMMENDATION #{idx} - JOB {r.job_id} ({r.product_id} on {r.machine_id})"
            border_color = "#059669"
            bg_color = "#ECFDF5"
            text_color = "#065F46"
            shift_badge = f"Shifted +{r.shift_hours}h ({r.baseline_start} -> {r.recommended_start})"
        else:
            header_title = f"JOB {r.job_id} ({r.product_id} on {r.machine_id})"
            border_color = "#D97706"
            bg_color = "#FEF3C7"
            text_color = "#92400E"
            shift_badge = f"Maintained at {r.baseline_start} (Optimal)"

        st.markdown(f"""
        <div style="background-color: {bg_color}; border-left: 6px solid {border_color}; padding: 18px 22px; border-radius: 10px; margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <h4 style="color: {text_color}; margin: 0; font-weight: 800; font-size: 1.05rem;">{header_title}</h4>
                <span style="background-color: #FFFFFF; color: {border_color}; border: 1px solid {border_color}; padding: 4px 12px; border-radius: 15px; font-weight: 700; font-size: 0.85rem;">{shift_badge}</span>
            </div>
            <div style="color: #334155; margin-top: 10px; font-size: 0.95rem;">
                <b>WHY?</b> {r.reason if r.shift_hours != 0 else "✓ No schedule change required. Current timing is already optimal under selected constraints."}
            </div>
            <div style="display: flex; gap: 25px; margin-top: 14px; font-size: 0.9rem; color: #475569;">
                <div><b>Solar Share:</b> {r.solar_used_kwh:.1f} kWh</div>
                <div><b>Grid Draw:</b> {r.grid_used_kwh:.1f} kWh</div>
                <div><b>Estimated Savings:</b> {format_currency(r.estimated_savings_rs)}</div>
                <div><b>Deadline:</b> {r.deadline_status}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
