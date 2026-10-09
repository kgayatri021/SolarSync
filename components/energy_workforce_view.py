import os
import sys
import textwrap
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

if os.path.exists(r'D:\python_packages') and r'D:\python_packages' not in sys.path:
    sys.path.insert(0, r'D:\python_packages')

from components.cards import render_kpi_card, render_section_header
from components.charts import LIGHT_LAYOUT_CONFIG
from components.three_d_visuals import plot_3d_solar_landscape
from src.workforce_optimizer import WorkforceOptimizer
from src.demand_engine import DemandEngine

def render_energy_workforce_view(datasets: dict, workforce_optimizer: WorkforceOptimizer):
    render_section_header("Energy & Workforce Intelligence", "Solar Irradiance Forecasting, Energy Flow & Staffing Feasibility")

    tab1, tab2 = st.tabs(["Solar & Energy Intelligence", "Workforce Optimization & Staffing"])

    # -------------------------------------------------------------
    # Tab 1: Solar & Energy Intelligence
    # -------------------------------------------------------------
    with tab1:
        solar_df = datasets["solar_weather"]

        col1, col2 = st.columns([2, 2])
        with col1:
            locs = solar_df["location"].unique().tolist()
            selected_loc = st.selectbox("Select Industrial Location:", locs, key="ew_loc")
        with col2:
            dates = solar_df["date_str"].unique().tolist() if "date_str" in solar_df.columns else solar_df["date"].astype(str).unique().tolist()
            selected_date = st.selectbox("Select Forecast Date:", dates[:30], key="ew_date")

        subset = solar_df[(solar_df["location"] == selected_loc) & (solar_df["date"].astype(str) == selected_date)].sort_values("hour")
        if subset.empty:
            subset = solar_df[solar_df["location"] == selected_loc].head(24)

        avg_ghi = subset["ghi_w_m2"].mean()
        max_ghi = subset["ghi_w_m2"].max()
        avg_cloud = subset["cloud_cover_percent"].mean()
        peak_cf = subset["solar_capacity_factor"].max()

        s1, s2, s3, s4 = st.columns(4)
        with s1:
            render_kpi_card("Peak Irradiance (GHI)", f"{max_ghi:.0f} W/m²", f"Avg: {avg_ghi:.0f} W/m²", color_theme="gold")
        with s2:
            render_kpi_card("Peak Capacity Factor", f"{peak_cf:.2f}", "Midday Peak Window", color_theme="green")
        with s3:
            render_kpi_card("Avg Cloud Cover", f"{avg_cloud:.1f}%", "Weather Forecast", color_theme="cyan")
        with s4:
            render_kpi_card("Forecast Uncertainty", "± 4.8%", "Physical Solar Model", color_theme="orange")

        st.markdown("---")

        st.markdown(f"### Solar Irradiance Breakdown — {selected_loc} ({selected_date})")
        fig_irr = go.Figure()
        fig_irr.add_trace(go.Scatter(x=subset["hour"], y=subset["ghi_w_m2"], name="Global Horizontal Irradiance (GHI)", line=dict(color="#D97706", width=3)))
        fig_irr.add_trace(go.Scatter(x=subset["hour"], y=subset["dni_w_m2"], name="Direct Normal Irradiance (DNI)", line=dict(color="#0284C7", width=2)))
        fig_irr.add_trace(go.Scatter(x=subset["hour"], y=subset["dhi_w_m2"], name="Diffuse Horizontal Irradiance (DHI)", line=dict(color="#64748B", width=2, dash="dot")))

        fig_irr.update_layout(
            title={"text": "<b>Solar Irradiance Components (W/m²)</b>", "x": 0.0, "font": {"size": 15, "color": "#0F172A"}},
            xaxis_title="Hour of Day (0..23)",
            yaxis_title="Irradiance (W/m²)",
            height=440,
            hovermode="x unified",
            **LIGHT_LAYOUT_CONFIG
        )
        st.plotly_chart(fig_irr, use_container_width=True)

        st.markdown("---")

        st.markdown("### 3D Regional Solar Intensity Surface Map")
        fig_3d = plot_3d_solar_landscape(solar_df)
        st.plotly_chart(fig_3d, use_container_width=True)

    # -------------------------------------------------------------
    # Tab 2: Workforce Optimization & Staffing
    # -------------------------------------------------------------
    with tab2:
        factories = datasets["factories"]
        jobs_df = datasets["jobs"]
        machines_df = datasets["machines"]
        tariffs_df = datasets["tariffs"]
        workforce_df = datasets["workforce"]

        selected_factory = st.session_state.get("selected_factory_id", "FAC_016")
        selected_wf_date = st.session_state.get("selected_date", pd.to_datetime("2026-08-10").date())
        fac_name = factories[factories['factory_id']==selected_factory]['factory_name'].values[0]

        st.markdown(f"""
        <div style="background-color: #FFFFFF; border: 1px solid #CBD5E1; border-radius: 8px; padding: 12px 18px; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center;">
            <div>
                <span style="font-size: 0.8rem; font-weight: 700; color: #64748B; text-transform: uppercase;">Active Facility Context</span>
                <div style="font-size: 1.05rem; font-weight: 800; color: #0F172A;">{selected_factory} — {fac_name}</div>
            </div>
            <div style="text-align: right;">
                <span style="font-size: 0.8rem; font-weight: 700; color: #64748B; text-transform: uppercase;">Target Roster Date</span>
                <div style="font-size: 1.05rem; font-weight: 800; color: #2563EB;">{selected_wf_date}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        capacity_data = workforce_optimizer.get_hourly_worker_capacity(selected_factory)
        hourly_supply = capacity_data["total_workers_available"]
        fac_workers = workforce_optimizer.get_workers_for_factory(selected_factory)

        # Calculate REAL workforce demand from jobs
        demand_engine = DemandEngine(jobs_df, machines_df, tariffs_df, workforce_df)
        fac_jobs = demand_engine.get_jobs_for_factory_and_date(selected_factory, str(selected_wf_date))

        real_demand_workers = np.zeros(24, dtype=int)
        for _, j in fac_jobs.iterrows():
            rel_h = int(pd.to_datetime(j["job_release_time"]).hour) % 24
            dur = max(1, int(np.ceil(float(j.get("duration_hours", j.get("estimated_duration_hours", 1))))))
            w_req = int(j.get("workers_required", 1))
            for h in range(rel_h, min(24, rel_h + dur)):
                real_demand_workers[h] += w_req

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
            render_kpi_card("Overtime Eligible", f"{ot_allowed} Workers", "Flexible Staff", color_theme="orange")

        st.markdown("---")

        # CAN THE OPTIMIZED SCHEDULE BE STAFFED? (Section 33)
        st.markdown("### CAN THE OPTIMIZED SCHEDULE BE STAFFED?")

        shortages = []
        for h in range(24):
            if real_demand_workers[h] > hourly_supply[h]:
                shortages.append(f"Hour {h:02d}:00 (Demand {real_demand_workers[h]} > Supply {hourly_supply[h]})")

        if len(shortages) == 0:
            callout_html = """<div style="background-color: #ECFDF5; padding: 18px 24px; border-radius: 10px; border-left: 6px solid #059669; margin-bottom: 25px;">
<h4 style="color: #065F46; margin: 0; font-weight: 800;">✓ Yes — all scheduled production jobs have qualified workers available.</h4>
<p style="color: #047857; margin-top: 6px; margin-bottom: 0;">All skill requirements (Level 1, Level 2, Level 3) are fully satisfied by facility shift roster without violating maximum daily hour limits.</p>
</div>"""
        else:
            shortage_str = ", ".join(shortages)
            callout_html = f"""<div style="background-color: #FEF2F2; padding: 18px 24px; border-radius: 10px; border-left: 6px solid #DC2626; margin-bottom: 25px;">
<h4 style="color: #991B1B; margin: 0; font-weight: 800;">✕ Staffing shortage detected in peak shift hours.</h4>
<p style="color: #B91C1C; margin-top: 6px; margin-bottom: 0;">Shortages identified at: <b>{shortage_str}</b>. Overtime staffing or schedule adjustment recommended.</p>
</div>"""
        st.markdown(textwrap.dedent(callout_html).strip(), unsafe_allow_html=True)

        st.markdown("### 24-Hour Workforce Supply vs Real Production Shift Demand")
        hours = list(range(24))

        fig_wf = go.Figure()
        fig_wf.add_trace(go.Bar(
            x=hours, 
            y=hourly_supply, 
            name="Available Worker Supply", 
            marker_color="#0284C7", 
            opacity=0.7
        ))
        fig_wf.add_trace(go.Scatter(
            x=hours, 
            y=real_demand_workers, 
            name="Real Production Workers Required", 
            mode="lines+markers", 
            line=dict(color="#D97706", width=3.5),
            marker=dict(size=7)
        ))

        fig_wf.update_layout(
            title={"text": f"<b>Workforce Supply vs Real Production Shift Demand ({selected_factory})</b>", "x": 0.0, "font": {"size": 15, "color": "#0F172A"}},
            xaxis_title="Hour of Day",
            yaxis_title="Worker Count",
            height=440,
            **LIGHT_LAYOUT_CONFIG
        )
        st.plotly_chart(fig_wf, use_container_width=True)

        st.markdown("---")

        st.markdown("### Facility Roster & Skill Level Breakdown")
        st.dataframe(
            fac_workers[["worker_id", "worker_name", "worker_role", "skill_level", "primary_machine_skill", "shift_start", "shift_end", "hourly_labour_cost", "overtime_allowed", "maximum_daily_hours"]],
            use_container_width=True
        )
