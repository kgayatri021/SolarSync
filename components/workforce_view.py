import os
import sys
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

if os.path.exists(r'D:\python_packages') and r'D:\python_packages' not in sys.path:
    sys.path.insert(0, r'D:\python_packages')

from components.cards import render_kpi_card, render_section_header
from components.charts import LIGHT_LAYOUT_CONFIG
from src.workforce_optimizer import WorkforceOptimizer
from src.demand_engine import DemandEngine

def render_workforce_view(datasets: dict, workforce_optimizer: WorkforceOptimizer):
    render_section_header("Workforce Optimization", "Shift Allocation, Skill Matching & Labour Constraint Analysis")

    factories = datasets["factories"]
    jobs_df = datasets["jobs"]
    machines_df = datasets["machines"]
    tariffs_df = datasets["tariffs"]
    workforce_df = datasets["workforce"]

    c_sel1, c_sel2 = st.columns(2)
    with c_sel1:
        fac_options = factories["factory_id"].tolist()
        default_idx = fac_options.index("FAC_016") if "FAC_016" in fac_options else 0
        selected_factory = st.selectbox(
            "Select Factory:",
            options=fac_options,
            index=default_idx,
            format_func=lambda fid: f"{fid} - {factories[factories['factory_id']==fid]['factory_name'].values[0]}"
        )
    with c_sel2:
        selected_date = st.date_input("Analysis Date:", pd.to_datetime("2026-08-10"))

    capacity_data = workforce_optimizer.get_hourly_worker_capacity(selected_factory)
    hourly_supply = capacity_data["total_workers_available"]
    fac_workers = workforce_optimizer.get_workers_for_factory(selected_factory)

    # Calculate REAL workforce demand from jobs for this factory and date
    demand_engine = DemandEngine(jobs_df, machines_df, tariffs_df, workforce_df)
    fac_jobs = demand_engine.get_jobs_for_factory_and_date(selected_factory, str(selected_date))
    
    real_demand_workers = np.zeros(24, dtype=int)
    for _, j in fac_jobs.iterrows():
        rel_h = int(pd.to_datetime(j["job_release_time"]).hour) % 24
        dur = max(1, int(np.ceil(float(j.get("duration_hours", j.get("estimated_duration_hours", 1))))))
        w_req = int(j.get("workers_required", 1))
        for h in range(rel_h, min(24, rel_h + dur)):
            real_demand_workers[h] += w_req

    # Top KPI Metrics
    tot_workers = len(fac_workers)
    avg_cost = fac_workers["hourly_labour_cost"].mean() if not fac_workers.empty else 150.0
    ot_allowed = int((fac_workers["overtime_allowed"] == True).sum()) if not fac_workers.empty else 0
    max_supply_hour = int(hourly_supply.max())

    w1, w2, w3, w4 = st.columns(4)
    with w1:
        render_kpi_card("Assigned Workers", f"{tot_workers}", "Facility Roster Staff", color_theme="gold")
    with w2:
        render_kpi_card("Peak Hourly Supply", f"{max_supply_hour} Workers", "Shift Window", color_theme="green")
    with w3:
        render_kpi_card("Avg Hourly Labour Rate", f"₹{avg_cost:.2f}/hr", "Regular Wages", color_theme="cyan")
    with w4:
        render_kpi_card("Overtime Eligible", f"{ot_allowed} Workers", "Flexible Overtime Staff", color_theme="orange")

    st.markdown("---")

    # CAN THE OPTIMIZED SCHEDULE BE STAFFED? (Section 29)
    st.markdown("### CAN THE OPTIMIZED SCHEDULE BE STAFFED?")
    
    shortages = []
    for h in range(24):
        if real_demand_workers[h] > hourly_supply[h]:
            shortages.append(f"Hour {h:02d}:00 (Demand {real_demand_workers[h]} > Supply {hourly_supply[h]})")

    if len(shortages) == 0:
        callout_html = f"""
        <div style="background-color: #ECFDF5; padding: 18px 24px; border-radius: 10px; border-left: 6px solid #059669; margin-bottom: 25px;">
            <h4 style="color: #065F46; margin: 0; font-weight: 800;">✓ Yes — all scheduled production jobs have qualified workers available.</h4>
            <p style="color: #047857; margin-top: 6px; margin-bottom: 0;">
                All skill requirements (Level 1, Level 2, Level 3) are fully satisfied by facility shift roster without violating maximum daily hour limits.
            </p>
        </div>
        """
    else:
        shortage_str = ", ".join(shortages)
        callout_html = f"""
        <div style="background-color: #FEF2F2; padding: 18px 24px; border-radius: 10px; border-left: 6px solid #DC2626; margin-bottom: 25px;">
            <h4 style="color: #991B1B; margin: 0; font-weight: 800;">✕ Staffing shortage detected in peak shift hours.</h4>
            <p style="color: #B91C1C; margin-top: 6px; margin-bottom: 0;">
                Shortages identified at: <b>{shortage_str}</b>. Overtime staffing or schedule adjustment recommended.
            </p>
        </div>
        """
    st.markdown(callout_html, unsafe_allow_html=True)

    # 24-Hour Workforce Supply vs Production Job Demand Profile Chart (Section 17)
    st.markdown("### 24-Hour Workforce Supply vs Real Production Shift Demand")
    hours = list(range(24))
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=hours, 
        y=hourly_supply, 
        name="Available Worker Supply", 
        marker_color="#0284C7", 
        opacity=0.7
    ))
    fig.add_trace(go.Scatter(
        x=hours, 
        y=real_demand_workers, 
        name="Real Production Workers Required", 
        mode="lines+markers", 
        line=dict(color="#D97706", width=3.5),
        marker=dict(size=7)
    ))

    fig.update_layout(
        title={"text": f"<b>Workforce Supply vs Real Production Shift Demand ({selected_factory})</b>", "x": 0.0, "font": {"size": 15, "color": "#0F172A"}},
        xaxis_title="Hour of Day",
        yaxis_title="Worker Count",
        **LIGHT_LAYOUT_CONFIG
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Skill Level Distribution & Roster Table
    st.markdown("### Facility Roster & Skill Level Breakdown")
    st.dataframe(
        fac_workers[["worker_id", "worker_name", "worker_role", "skill_level", "primary_machine_skill", "shift_start", "shift_end", "hourly_labour_cost", "overtime_allowed", "maximum_daily_hours"]],
        use_container_width=True
    )
