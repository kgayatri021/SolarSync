import os
import sys
import streamlit as st
import pandas as pd
import numpy as np

if os.path.exists(r'D:\python_packages') and r'D:\python_packages' not in sys.path:
    sys.path.insert(0, r'D:\python_packages')

from components.cards import render_kpi_card, render_section_header
from components.charts import plot_solar_vs_demand_curve, plot_baseline_vs_optimized_comparison
from src.result_engine import evaluate_result_state
from src.scenario_engine import ScenarioEngine, ScenarioParams, ScenarioResult
from src.utils import format_currency

def render_scenario_view(datasets: dict, scenario_engine: ScenarioEngine):
    render_section_header("Scenario Simulator", "What-If Policy, Solar Expansion & Tariff Stress-Testing Platform")

    factories = datasets["factories"]

    st.markdown("##### Scenario Simulation Parameters")
    sc_col1, sc_col2, sc_col3 = st.columns(3)
    
    selected_factory = st.session_state.get("selected_factory_id", "FAC_016")
    selected_date = st.session_state.get("selected_date", pd.to_datetime("2026-08-10").date())
    fac_name = factories[factories['factory_id']==selected_factory]['factory_name'].values[0]

    with sc_col1:
        scenario_name = st.text_input("Scenario Label:", "Cloudy Day & Solar Expansion Test")
        st.caption(f"Target Facility: **{selected_factory} ({fac_name})**")
        st.caption(f"Simulation Date: **{selected_date}**")

    with sc_col2:
        solar_avail_pct = st.slider(
            "Solar Availability (% of normal):", 
            min_value=10, max_value=150, value=70, step=5, 
            format="%d%%",
            help="70% of normal solar generation due to cloud cover"
        )
        solar_cap_pct = st.slider(
            "Solar Capacity (% of current):", 
            min_value=50, max_value=200, value=140, step=10, 
            format="%d%%",
            help="140% of current installed solar capacity"
        )

    with sc_col3:
        demand_pct = st.slider(
            "Production Demand (% of normal):", 
            min_value=50, max_value=150, value=100, step=5, 
            format="%d%%",
            help="100% = Normal Production Demand"
        )
        tariff_pct = st.slider(
            "Peak Electricity Price (% of current):", 
            min_value=50, max_value=200, value=120, step=10, 
            format="%d%%",
            help="120% of current Peak Electricity Tariff Rate"
        )

        cloud_factor = solar_avail_pct / 100.0
        solar_capacity_mult = solar_cap_pct / 100.0
        demand_mult = demand_pct / 100.0
        tariff_mult = tariff_pct / 100.0

    run_btn = st.button("RUN SCENARIO SIMULATION", type="primary", use_container_width=True)

    st.markdown("---")

    sc_key = f"sc_{selected_factory}_{selected_date}_{cloud_factor}_{solar_capacity_mult}_{demand_mult}_{tariff_mult}"
    
    if run_btn or sc_key in st.session_state:
        if run_btn:
            with st.spinner("Recalculating OR-Tools CP-SAT optimization under scenario parameters..."):
                params = ScenarioParams(
                    scenario_name=scenario_name,
                    factory_id=selected_factory,
                    target_date=str(selected_date),
                    cloud_factor=cloud_factor,
                    solar_capacity_multiplier=solar_capacity_mult,
                    demand_multiplier=demand_mult,
                    tariff_peak_multiplier=tariff_mult
                )
                sc_res = scenario_engine.run_scenario(params)
                st.session_state[sc_key] = sc_res

        sc_result: ScenarioResult = st.session_state[sc_key]
        base_run = sc_result.baseline_result
        sc_run = sc_result.scenario_result
        opt_metrics = sc_run.optimized_metrics
        comp = sc_run.comparison

        shifted_count = sum(1 for b, s in zip(sc_run.baseline_jobs, sc_run.scheduled_jobs) if b.start_hour != s.start_hour)

        state = evaluate_result_state(
            solver_status=sc_run.solver_status,
            shifted_count=shifted_count,
            baseline_grid_kwh=sc_run.baseline_metrics.grid_energy_used_kwh,
            optimized_grid_kwh=sc_run.optimized_metrics.grid_energy_used_kwh,
            baseline_solar_kwh=sc_run.baseline_metrics.solar_energy_used_kwh,
            optimized_solar_kwh=sc_run.optimized_metrics.solar_energy_used_kwh,
            baseline_cost_rs=sc_run.baseline_metrics.electricity_cost_rs,
            optimized_cost_rs=sc_run.optimized_metrics.electricity_cost_rs
        )

        grid_diff = opt_metrics.grid_energy_used_kwh - sc_run.baseline_metrics.grid_energy_used_kwh
        cost_diff = opt_metrics.electricity_cost_rs - sc_run.baseline_metrics.electricity_cost_rs

        # WHAT CHANGED?
        st.markdown(f"### WHAT CHANGED? — Scenario: {scenario_name}")
        w1, w2, w3 = st.columns(3)
        with w1:
            st.markdown(f"""
            <div style="background: #FFFFFF; border: 1px solid #E2E8F0; padding: 16px; border-radius: 8px;">
                <b style="color: #0F172A;">Solar Availability:</b> <span style="color: #D97706;">{cloud_factor*100:.0f}% of normal</span><br>
                <b style="color: #0F172A;">Solar Capacity:</b> <span style="color: #0284C7;">{solar_capacity_mult*100:.0f}% of current</span>
            </div>
            """, unsafe_allow_html=True)
        with w2:
            st.markdown(f"""
            <div style="background: #FFFFFF; border: 1px solid #E2E8F0; padding: 16px; border-radius: 8px;">
                <b style="color: #0F172A;">Peak Tariff:</b> <span style="color: #DC2626;">{tariff_mult*100:.0f}% of current</span><br>
                <b style="color: #0F172A;">Production Demand:</b> <span style="color: #0F172A;">{demand_mult*100:.0f}% of normal</span>
            </div>
            """, unsafe_allow_html=True)
        with w3:
            grid_change_str = f"+{grid_diff:.1f} kWh" if grid_diff > 0 else f"{grid_diff:.1f} kWh"
            cost_change_str = f"+{format_currency(cost_diff)}" if cost_diff > 0 else f"-{format_currency(abs(cost_diff))}"
            cost_color = "#059669" if cost_diff <= 0 else "#DC2626"
            st.markdown(f"""
            <div style="background: #FFFFFF; border: 1px solid #E2E8F0; padding: 16px; border-radius: 8px;">
                <b style="color: #0F172A;">Grid Draw Change:</b> <span style="color: #0284C7;">{grid_change_str}</span><br>
                <b style="color: #0F172A;">Cost Impact:</b> <span style="color: {cost_color};">{cost_change_str}</span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        # RESULT & DECISION
        st.markdown("### SCENARIO RESULT & RECOMMENDED DECISION")
        
        st.markdown(f"""
        <div style="background-color: {state.banner_bg}; padding: 20px 24px; border-radius: 10px; border-left: 6px solid {state.border_color}; margin-bottom: 25px;">
            <h4 style="color: {state.text_color}; margin: 0; font-weight: 800;">
                {state.title} — {state.subtitle}
            </h4>
            <p style="color: #475569; margin-top: 6px; margin-bottom: 0;">
                Grid draw: <b>{sc_run.baseline_metrics.grid_energy_used_kwh:.1f} kWh → {opt_metrics.grid_energy_used_kwh:.1f} kWh</b> | 
                Cost: <b>{format_currency(sc_run.baseline_metrics.electricity_cost_rs)} → {format_currency(opt_metrics.electricity_cost_rs)}</b>
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("### Solar Availability vs Demand (Scenario)")
        fig_curve = plot_solar_vs_demand_curve(
            sc_run.hourly_solar_available,
            sc_run.hourly_baseline_demand,
            sc_run.hourly_optimized_demand,
            f"SOLAR AVAILABILITY VS DEMAND ({selected_factory})"
        )
        st.plotly_chart(fig_curve, use_container_width=True)

        st.markdown("### Baseline vs SOLAR SYNC Impact (Scenario)")
        fig_comp = plot_baseline_vs_optimized_comparison(
            sc_run.baseline_metrics.grid_energy_used_kwh,
            opt_metrics.grid_energy_used_kwh,
            sc_run.baseline_metrics.solar_energy_used_kwh,
            opt_metrics.solar_energy_used_kwh,
            sc_run.baseline_metrics.electricity_cost_rs,
            opt_metrics.electricity_cost_rs
        )
        st.plotly_chart(fig_comp, use_container_width=True)
