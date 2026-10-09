import os
import sys
import textwrap
import streamlit as st
import pandas as pd
import numpy as np

if os.path.exists(r'D:\python_packages') and r'D:\python_packages' not in sys.path:
    sys.path.insert(0, r'D:\python_packages')

from components.cards import render_kpi_card, render_section_header
from components.charts import plot_solar_vs_demand_curve, plot_baseline_vs_optimized_comparison
from components.three_d_visuals import plot_3d_factory_cluster, plot_2d_factory_cluster_map
from src.result_engine import evaluate_result_state
from src.solar_engine import SolarEngine
from src.demand_engine import DemandEngine
from src.cost_engine import CostEngine
from src.workforce_optimizer import WorkforceOptimizer
from src.scheduler import SolarShiftScheduler
from src.report_generator import generate_excel_decision_report
from src.pdf_generator import generate_pdf_decision_report
from src.utils import format_currency, format_kwh

def render_executive_dashboard(datasets: dict):
    # Hero Visual Header & Flow Illustration (Section 20 & 21)
    hero_html = """<div style="background: linear-gradient(135deg, #FFFFFF 0%, #F1F5F9 100%); border: 1px solid #E2E8F0; border-radius: 12px; padding: 24px 28px; margin-bottom: 24px; box-shadow: 0 2px 5px rgba(0,0,0,0.05);">
<div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 15px;">
<div>
<span style="background-color: #FEF3C7; color: #92400E; font-size: 0.75rem; font-weight: 800; padding: 4px 10px; border-radius: 12px; letter-spacing: 0.5px;">DRE ENTERPRISE HACKATHON '26 • PS07</span>
<h1 style="color: #0F172A; font-size: 2.1rem; font-weight: 800; margin: 8px 0 4px 0;">SOLAR SYNC</h1>
<div style="color: #334155; font-size: 1.05rem; font-weight: 600;">Solar-Aware Industrial Demand Shifting & Scheduling Platform</div>
<div style="color: #64748B; font-size: 0.9rem; margin-top: 4px;">North Coastal Andhra Pradesh Industrial Cluster (Visakhapatnam, Anakapalli, Vizianagaram, Srikakulam)</div>
</div>
<div style="background-color: #FFFFFF; border: 1px solid #CBD5E1; border-radius: 10px; padding: 12px 18px; text-align: center;">
<div style="font-size: 0.78rem; font-weight: 700; color: #64748B; text-transform: uppercase;">Solver Engine</div>
<div style="font-size: 1.25rem; font-weight: 800; color: #059669; margin-top: 2px;">Google OR-Tools</div>
<div style="font-size: 0.75rem; color: #0284C7; font-weight: 600;">CP-SAT Integer Solver</div>
</div>
</div>
<div style="margin-top: 20px; padding-top: 16px; border-top: 1px solid #E2E8F0;">
<div style="font-size: 0.8rem; font-weight: 700; color: #475569; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px;">Industrial Energy Flow Topology</div>
<div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 8px; font-size: 0.88rem; font-weight: 700;">
<span style="background: #FFFBEB; border: 1px solid #FCD34D; color: #B45309; padding: 6px 12px; border-radius: 6px;">1. Solar Generation</span>
<span style="color: #94A3B8;">➔</span>
<span style="background: #F0F9FF; border: 1px solid #7DD3FC; color: #0369A1; padding: 6px 12px; border-radius: 6px;">2. Factory Demand</span>
<span style="color: #94A3B8;">➔</span>
<span style="background: #F5F3FF; border: 1px solid #C4B5FD; color: #6D28D9; padding: 6px 12px; border-radius: 6px;">3. Flexible Jobs</span>
<span style="color: #94A3B8;">➔</span>
<span style="background: #ECFDF5; border: 1px solid #6EE7B7; color: #047857; padding: 6px 12px; border-radius: 6px;">4. CP-SAT Optimizer</span>
<span style="color: #94A3B8;">➔</span>
<span style="background: #EFF6FF; border: 1px solid #93C5FD; color: #1D4ED8; padding: 6px 12px; border-radius: 6px;">5. Grid Reduction & Savings</span>
</div>
</div>
</div>"""

    st.markdown(textwrap.dedent(hero_html).strip(), unsafe_allow_html=True)

    factories = datasets["factories"]
    machines = datasets["machines"]
    jobs = datasets["jobs"]
    workforce = datasets["workforce"]
    solar = datasets["solar_weather"]
    tariffs = datasets["tariffs"]

    # Top Cluster Infrastructure Metrics
    tot_factories = len(factories)
    tot_machines = len(machines)
    tot_solar_kw = float(factories["installed_solar_capacity_kw"].sum())
    tot_grid_kw = float(factories["grid_connection_capacity_kw"].sum())

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_kpi_card("Industrial Factories", f"{tot_factories}", "North Coastal AP Cluster", color_theme="gold")
    with c2:
        render_kpi_card("Active Machines", f"{tot_machines}", "26 Scheduled Maintenance", color_theme="cyan")
    with c3:
        render_kpi_card("Installed Solar", f"{tot_solar_kw:,.0f} kW", "Cluster Infrastructure", color_theme="green")
    with c4:
        render_kpi_card("Grid Connection", f"{tot_grid_kw:,.0f} kW", "Contracted Demand Limit", color_theme="orange")

    st.markdown("---")

    # Facility & Date Context from Sidebar
    selected_fac_id = st.session_state.get("selected_factory_id", "FAC_016")
    selected_date = st.session_state.get("selected_date", pd.to_datetime("2026-08-10").date())
    fac_name = factories[factories['factory_id']==selected_fac_id]['factory_name'].values[0]

    st.markdown(f"""
    <div style="background-color: #FFFFFF; border: 1px solid #CBD5E1; border-radius: 8px; padding: 12px 18px; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center;">
        <div>
            <span style="font-size: 0.8rem; font-weight: 700; color: #64748B; text-transform: uppercase;">Active Facility Context</span>
            <div style="font-size: 1.1rem; font-weight: 800; color: #0F172A;">{selected_fac_id} — {fac_name}</div>
        </div>
        <div style="text-align: right;">
            <span style="font-size: 0.8rem; font-weight: 700; color: #64748B; text-transform: uppercase;">Target Analysis Date</span>
            <div style="font-size: 1.1rem; font-weight: 800; color: #2563EB;">{selected_date}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Optional Today's Operating Inputs (Section 12 & 13)
    with st.expander("⚙️ Today's Operating Conditions & Real-World Overrides", expanded=False):
        input_mode = st.radio(
            "Operating Input Mode:",
            ["USE DATASET VALUES", "TODAY'S OPERATING CONDITIONS"],
            index=0,
            horizontal=True,
            help="Switch to input today's actual plant production requirements and workforce roster.",
            key="operating_input_mode"
        )

        cloud_factor_val = 1.0
        if input_mode == "TODAY'S OPERATING CONDITIONS":
            st.info("⚡ USER OVERRIDE ACTIVE — Optimization solver will incorporate live plant operational conditions.")
            o_col1, o_col2 = st.columns(2)
            with o_col1:
                prod_req_pct = st.slider("Today's Production Demand Target:", 50, 150, 100, 5, format="%d%% of normal")
            with o_col2:
                solar_avail_override = st.slider("Today's Expected Solar Generation:", 20, 150, 100, 5, format="%d%% of normal")
            cloud_factor_val = solar_avail_override / 100.0
        else:
            st.caption("Status: USING DATASET VALUES (Baseline Operational Schedule)")

    # Compute optimization for selected facility & date
    solar_eng = SolarEngine(solar, factories)
    demand_eng = DemandEngine(jobs, machines, tariffs, workforce)
    cost_eng = CostEngine(tariffs)
    work_opt = WorkforceOptimizer(workforce, machines)
    scheduler = SolarShiftScheduler(solar_eng, cost_eng, work_opt, machines, factories)

    fac_jobs = demand_eng.get_jobs_for_factory_and_date(selected_fac_id, str(selected_date))
    opt_res = scheduler.optimize_schedule(
        selected_fac_id, 
        str(selected_date), 
        fac_jobs, 
        cloud_factor=cloud_factor_val,
        time_limit_seconds=5
    )
    comp = opt_res.comparison
    base_st = [b.start_hour for b in opt_res.baseline_jobs]
    opt_st = [s.start_hour for s in opt_res.scheduled_jobs]
    shifted_count = sum(1 for i in range(len(base_st)) if base_st[i] != opt_st[i])

    state = evaluate_result_state(
        solver_status=opt_res.solver_status,
        shifted_count=shifted_count,
        baseline_grid_kwh=opt_res.baseline_metrics.grid_energy_used_kwh,
        optimized_grid_kwh=opt_res.optimized_metrics.grid_energy_used_kwh,
        baseline_solar_kwh=opt_res.baseline_metrics.solar_energy_used_kwh,
        optimized_solar_kwh=opt_res.optimized_metrics.solar_energy_used_kwh,
        baseline_cost_rs=opt_res.baseline_metrics.electricity_cost_rs,
        optimized_cost_rs=opt_res.optimized_metrics.electricity_cost_rs
    )

    # HERO SECTION: TODAY'S SOLAR SYNC DECISION (Section 3 & 4)
    st.markdown("### TODAY'S SOLAR SYNC DECISION")

    decision_html = f"""<div style="background-color: {state.banner_bg}; padding: 20px 24px; border-radius: 10px; border-left: 6px solid {state.border_color}; margin-bottom: 22px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
<h3 style="color: {state.text_color}; margin: 0; font-weight: 800; font-size: 1.25rem;">{state.title} — {state.subtitle}</h3>
<p style="color: #475569; margin-top: 6px; margin-bottom: 0; font-size: 0.95rem;">
Optimization status: <b>{opt_res.solver_status}</b> via Google OR-Tools CP-SAT Integer Programming Solver.
</p>
</div>"""
    st.markdown(textwrap.dedent(decision_html).strip(), unsafe_allow_html=True)

    # Priority 1: Today's Operating Metrics (Section 3 & 12)
    solar_avail_kwh = float(opt_res.hourly_solar_available.sum())
    demand_kwh = float(opt_res.hourly_baseline_demand.sum())

    m1, m2, m3, m4, m5 = st.columns(5)
    with m1:
        render_kpi_card(
            "Solar Available", 
            f"{solar_avail_kwh:,.1f} kWh", 
            "Peak Window (10:00–14:00)", 
            color_theme="gold",
            tooltip_text="Total available solar generation for today."
        )
    with m2:
        render_kpi_card(
            "Production Demand", 
            f"{demand_kwh:,.1f} kWh", 
            f"{len(fac_jobs)} Jobs Scheduled", 
            color_theme="cyan",
            tooltip_text="Total electrical demand of production jobs scheduled today."
        )
    with m3:
        render_kpi_card(
            "Jobs Shifted", 
            f"{shifted_count} Flexible Jobs", 
            "Shifted to Peak Solar" if shifted_count > 0 else "Optimal Schedule", 
            color_theme="green" if shifted_count > 0 else "gold",
            tooltip_text="Number of production jobs shifted into solar peak window."
        )
    with m4:
        grid_val = f"{opt_res.optimized_metrics.grid_energy_used_kwh:.1f} kWh" if state.is_feasible else "N/A"
        render_kpi_card(
            "Grid Energy Draw", 
            grid_val, 
            state.grid_delta_text, 
            color_theme="green" if state.code == "IMPROVED" else "gold",
            tooltip_text="Optimized grid energy consumption today."
        )
    with m5:
        cost_val = format_currency(opt_res.optimized_metrics.electricity_cost_rs) if state.is_feasible else "N/A"
        render_kpi_card(
            "Cost Impact", 
            cost_val, 
            state.cost_delta_text, 
            color_theme="green" if state.code == "IMPROVED" else ("red" if state.code == "NO_BENEFIT" else "gold"),
            tooltip_text="Net electricity cost after SolarSync optimization."
        )

    # Detailed Operating Cost Breakdown Card
    with st.expander("💰 View Detailed Operating Cost Breakdown", expanded=False):
        c_b1, c_b2, c_b3 = st.columns(3)
        with c_b1:
            st.markdown(f"""
            <div style="background: #FFFFFF; border: 1px solid #E2E8F0; padding: 14px; border-radius: 8px;">
                <div style="color: #64748B; font-size: 0.8rem; font-weight: 700; text-transform: uppercase;">Electricity Cost (HT1 Tariff)</div>
                <div style="font-size: 1.2rem; font-weight: 800; color: #2563EB; margin-top: 4px;">{format_currency(opt_res.optimized_metrics.electricity_cost_rs) if state.is_feasible else 'N/A'}</div>
                <div style="font-size: 0.78rem; color: #64748B; margin-top: 2px;">Baseline: {format_currency(opt_res.baseline_metrics.electricity_cost_rs)}</div>
            </div>
            """, unsafe_allow_html=True)
        with c_b2:
            st.markdown(f"""
            <div style="background: #FFFFFF; border: 1px solid #E2E8F0; padding: 14px; border-radius: 8px;">
                <div style="color: #64748B; font-size: 0.8rem; font-weight: 700; text-transform: uppercase;">Net Operating Savings</div>
                <div style="font-size: 1.2rem; font-weight: 800; color: {'#059669' if comp.electricity_cost_savings_rs >= 0 else '#DC2626'}; margin-top: 4px;">{format_currency(abs(comp.electricity_cost_savings_rs))} {'Saved' if comp.electricity_cost_savings_rs >= 0 else 'Increase'}</div>
                <div style="font-size: 0.78rem; color: #64748B; margin-top: 2px;">{state.cost_delta_text}</div>
            </div>
            """, unsafe_allow_html=True)
        with c_b3:
            st.markdown(f"""
            <div style="background: #FFFFFF; border: 1px solid #E2E8F0; padding: 14px; border-radius: 8px;">
                <div style="color: #64748B; font-size: 0.8rem; font-weight: 700; text-transform: uppercase;">Solar Energy Contribution</div>
                <div style="font-size: 1.2rem; font-weight: 800; color: #D97706; margin-top: 4px;">{opt_res.optimized_metrics.solar_energy_used_kwh:.1f} kWh</div>
                <div style="font-size: 0.78rem; color: #D97706; margin-top: 2px;">Grid Offset: +{comp.solar_increase_percent:.1f}% Solar</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown(f"##### Why did SOLAR SYNC make this decision?")
    for r_item in state.reasons:
        st.markdown(f"- {r_item}")

    st.markdown("---")

    # Secondary Cluster Infrastructure Overview (Section 3 & 12)
    with st.expander("🏢 View Industrial Cluster Infrastructure Overview", expanded=False):
        tot_factories = len(factories)
        tot_machines = len(machines)
        tot_solar_kw = float(factories["installed_solar_capacity_kw"].sum())
        tot_grid_kw = float(factories["grid_connection_capacity_kw"].sum())

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            render_kpi_card("Industrial Factories", f"{tot_factories}", "North Coastal AP Cluster", color_theme="gold")
        with c2:
            render_kpi_card("Active Machines", f"{tot_machines}", "26 Scheduled Maintenance", color_theme="cyan")
        with c3:
            render_kpi_card("Installed Solar", f"{tot_solar_kw:,.0f} kW", "Cluster Infrastructure", color_theme="green")
        with c4:
            render_kpi_card("Grid Connection", f"{tot_grid_kw:,.0f} kW", "Contracted Demand Limit", color_theme="orange")

    st.markdown("---")

    # Full-Width Solar vs Demand Hero Chart
    st.markdown("### Solar Availability vs Production Demand")
    fig = plot_solar_vs_demand_curve(
        opt_res.hourly_solar_available, 
        opt_res.hourly_baseline_demand, 
        opt_res.hourly_optimized_demand, 
        f"SOLAR AVAILABILITY VS DEMAND ({selected_fac_id})"
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Geographic Visualizations: 3D Elevation Map & 2D Regional Map (Section 19)
    st.markdown("### Industrial Cluster Geographic Visualizations")
    st.caption("Shows relative solar intensity across the selected industrial region and factory locations.")
    map_tab1, map_tab2 = st.tabs(["3D Industrial Elevation Cluster", "2D Regional Map View"])
    with map_tab1:
        fig_3d = plot_3d_factory_cluster(factories)
        st.plotly_chart(fig_3d, use_container_width=True)
    with map_tab2:
        fig_2d = plot_2d_factory_cluster_map(factories)
        st.plotly_chart(fig_2d, use_container_width=True)

    st.markdown("---")

    # Comparative Impact Bar Chart
    st.markdown("### Baseline vs SOLAR SYNC Impact Comparison")
    fig_comp = plot_baseline_vs_optimized_comparison(
        opt_res.baseline_metrics.grid_energy_used_kwh,
        opt_res.optimized_metrics.grid_energy_used_kwh,
        opt_res.baseline_metrics.solar_energy_used_kwh,
        opt_res.optimized_metrics.solar_energy_used_kwh,
        opt_res.baseline_metrics.electricity_cost_rs,
        opt_res.optimized_metrics.electricity_cost_rs
    )
    st.plotly_chart(fig_comp, use_container_width=True)

    # Decision Report & Data Export Hub (Section 28, 31, 33)
    st.markdown("### Export Decision Reports & Operational Data")
    exp_col1, exp_col2 = st.columns(2)
    with exp_col1:
        pdf_bytes = generate_pdf_decision_report(opt_res, factory_info={"factory_name": factories[factories['factory_id']==selected_fac_id]['factory_name'].values[0]})
        st.download_button(
            label="📥 Download Decision Report (PDF)",
            data=pdf_bytes,
            file_name=f"SolarSync_Decision_Report_{selected_fac_id}_{selected_date}.pdf",
            mime="application/pdf",
            use_container_width=True,
            type="primary"
        )
    with exp_col2:
        excel_bytes = generate_excel_decision_report(opt_res)
        st.download_button(
            label="📥 Download Detailed Data (Excel)",
            data=excel_bytes,
            file_name=f"SolarSync_Detailed_Data_{selected_fac_id}_{selected_date}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

    with st.expander("🛠️ Advanced Technical Data Export (CSV)", expanded=False):
        csv_bytes = fac_jobs.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Technical Export (CSV)",
            data=csv_bytes,
            file_name=f"SolarSync_Jobs_{selected_fac_id}_{selected_date}.csv",
            mime="text/csv",
            use_container_width=True
        )
