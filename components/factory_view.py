import os
import sys
import streamlit as st
import pandas as pd
import numpy as np

if os.path.exists(r'D:\python_packages') and r'D:\python_packages' not in sys.path:
    sys.path.insert(0, r'D:\python_packages')

from components.cards import render_kpi_card, render_section_header
from components.charts import plot_solar_vs_demand_curve
from src.solar_engine import SolarEngine
from src.demand_engine import DemandEngine

def render_factory_view(datasets: dict, solar_engine: SolarEngine, demand_engine: DemandEngine):
    render_section_header("Factory Intelligence", "Detailed Facility Infrastructure, Machines, Workforce & Energy Flow")

    factories = datasets["factories"]
    machines = datasets["machines"]
    workforce = datasets["workforce"]

    selected_factory_id = st.session_state.get("selected_factory_id", "FAC_016")
    selected_date = st.session_state.get("selected_date", pd.to_datetime("2026-08-10").date())
    fac_name = factories[factories['factory_id']==selected_factory_id]['factory_name'].values[0]

    st.markdown(f"""
    <div style="background-color: #FFFFFF; border: 1px solid #CBD5E1; border-radius: 8px; padding: 12px 18px; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center;">
        <div>
            <span style="font-size: 0.8rem; font-weight: 700; color: #64748B; text-transform: uppercase;">Active Facility Context</span>
            <div style="font-size: 1.1rem; font-weight: 800; color: #0F172A;">{selected_factory_id} — {fac_name}</div>
        </div>
        <div style="text-align: right;">
            <span style="font-size: 0.8rem; font-weight: 700; color: #64748B; text-transform: uppercase;">Target Analysis Date</span>
            <div style="font-size: 1.1rem; font-weight: 800; color: #2563EB;">{selected_date}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    fac_row = factories[factories["factory_id"] == selected_factory_id].iloc[0]
    fac_name = fac_row["factory_name"]
    industry = fac_row["industry_type"]
    solar_cap = fac_row["installed_solar_capacity_kw"]
    grid_cap = fac_row["grid_connection_capacity_kw"]
    n_mach = fac_row["number_of_machines"]
    n_work = fac_row["number_of_workers"]

    # Dynamic Factory Status Banner (Section 26)
    st.markdown("""
    <div style="background-color: #ECFDF5; border-left: 6px solid #059669; padding: 14px 20px; border-radius: 8px; margin-bottom: 20px;">
        <span style="color: #065F46; font-weight: 800; font-size: 0.95rem;">CURRENT FACTORY STATUS: Production Feasible & Solar-Aware</span>
    </div>
    """, unsafe_allow_html=True)

    # Specs KPI Row
    f1, f2, f3, f4 = st.columns(4)
    with f1:
        render_kpi_card("Industry Type", industry, f"District: {fac_row.get('district', '')}", color_theme="gold")
    with f2:
        render_kpi_card("Solar Capacity", f"{solar_cap:.0f} kW", f"Battery: {fac_row['battery_capacity_kwh']} kWh", color_theme="green")
    with f3:
        render_kpi_card("Grid Connection", f"{grid_cap:.0f} kW", f"Contracted: {fac_row['contracted_demand_kw']} kW", color_theme="cyan")
    with f4:
        render_kpi_card("Facility Assets", f"{n_mach} Machines", f"{n_work} Assigned Workers", color_theme="orange")

    st.markdown("---")

    # Solar & Demand Profile for selected factory
    solar_profile = solar_engine.get_solar_profile_for_factory(selected_factory_id, str(selected_date))
    jobs = demand_engine.get_jobs_for_factory_and_date(selected_factory_id, str(selected_date))

    st.markdown(f"### Hourly Energy Profile — {fac_name} ({selected_date})")
    solar_array = solar_profile["solar_available_kw"].to_numpy()
    
    mach_subset = machines[machines["factory_id"] == selected_factory_id]
    tot_mach_power = mach_subset["rated_power_kw"].sum()
    base_demand = np.array([0.2, 0.2, 0.2, 0.2, 0.3, 0.6, 0.8, 0.9, 0.95, 0.9, 0.85, 0.8, 0.75, 0.8, 0.85, 0.9, 0.95, 0.9, 0.7, 0.5, 0.3, 0.2, 0.2, 0.2]) * tot_mach_power * 0.4

    fig = plot_solar_vs_demand_curve(solar_array, base_demand, None, f"{fac_name} - Available Solar vs Facility Power Demand")
    st.plotly_chart(fig, use_container_width=True)

    # Tables: Machines & Workforce
    tab1, tab2 = st.tabs(["Machine Inventory & Maintenance Status", "Workforce Skill Matrix"])
    with tab1:
        st.dataframe(
            mach_subset[["machine_id", "machine_name", "machine_type", "rated_power_kw", "standby_power_kw", "production_rate_units_per_hour", "maintenance_status", "workers_required"]],
            use_container_width=True
        )

    with tab2:
        work_subset = workforce[workforce["factory_id"] == selected_factory_id]
        st.dataframe(
            work_subset[["worker_id", "worker_name", "worker_role", "skill_level", "primary_machine_skill", "shift_start", "shift_end", "hourly_labour_cost", "overtime_allowed"]],
            use_container_width=True
        )
