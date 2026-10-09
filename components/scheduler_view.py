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
from src.result_engine import evaluate_result_state
from src.scheduler import SolarSyncScheduler, ScheduleResult
from src.demand_engine import DemandEngine
from src.recommender import RecommendationEngine
from src.report_generator import generate_excel_decision_report
from src.pdf_generator import generate_pdf_decision_report
from src.utils import format_currency, format_kwh

def render_scheduler_view(
    datasets: dict, 
    scheduler: SolarSyncScheduler, 
    demand_engine: DemandEngine,
    recommender: RecommendationEngine
):
    render_section_header("Smart Scheduler", "Google OR-Tools CP-SAT Powered Solar-Aware Job Demand Shifting Engine")

    factories = datasets["factories"]

    # Production Scheduler Parameters
    selected_factory = st.session_state.get("selected_factory_id", "FAC_016")
    selected_date = st.session_state.get("selected_date", pd.to_datetime("2026-08-10").date())
    fac_name = factories[factories['factory_id']==selected_factory]['factory_name'].values[0]

    with st.container():
        st.markdown(f"""
        <div style="background-color: #FFFFFF; border: 1px solid #CBD5E1; border-radius: 8px; padding: 12px 18px; margin-bottom: 15px; display: flex; justify-content: space-between; align-items: center;">
            <div>
                <span style="font-size: 0.78rem; font-weight: 700; color: #64748B; text-transform: uppercase;">Active Facility Context</span>
                <div style="font-size: 1.05rem; font-weight: 800; color: #0F172A;">{selected_factory} — {fac_name}</div>
            </div>
            <div style="text-align: right;">
                <span style="font-size: 0.78rem; font-weight: 700; color: #64748B; text-transform: uppercase;">Target Schedule Date</span>
                <div style="font-size: 1.05rem; font-weight: 800; color: #2563EB;">{selected_date}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        opt_objective = st.selectbox(
            "Optimization Objective:",
            ["Minimize Electricity Cost", "Maximize Solar Utilization", "Balance Cost + Solar + Workforce"],
            key="sched_obj_select"
        )

        # Advanced technical controls hidden in expander
        with st.expander("Advanced Settings & Solver Parameters", expanded=False):
            sc_a, sc_b = st.columns(2)
            with sc_a:
                cloud_factor = st.slider("Solar Weather Adjustment Factor:", 0.2, 1.0, 1.0, 0.1, help="1.0 = Normal Solar, 0.5 = Cloud Cover")
            with sc_b:
                solver_time_limit = st.selectbox("Solver Time Limit (s):", [5, 10, 15, 30], index=1)

        opt_btn = st.button("OPTIMIZE SCHEDULE", use_container_width=True, type="primary")

    st.markdown("---")

    session_key = f"opt_{selected_factory}_{selected_date}_{cloud_factor}_{opt_objective}"
    
    if opt_btn or session_key in st.session_state:
        if opt_btn:
            with st.spinner("Solving integer programming model via Google OR-Tools CP-SAT..."):
                jobs = demand_engine.get_jobs_for_factory_and_date(selected_factory, str(selected_date))
                if jobs.empty:
                    st.error("No valid production jobs found for the selected facility and date.")
                    return

                res = scheduler.optimize_schedule(
                    factory_id=selected_factory,
                    target_date=str(selected_date),
                    jobs_df=jobs,
                    cloud_factor=cloud_factor,
                    time_limit_seconds=solver_time_limit
                )
                st.session_state[session_key] = res
        
        result: ScheduleResult = st.session_state[session_key]
        comp = result.comparison

        base_st = [b.start_hour for b in result.baseline_jobs]
        opt_st = [s.start_hour for s in result.scheduled_jobs]
        shifted_count = sum(1 for i in range(len(base_st)) if base_st[i] != opt_st[i])

        state = evaluate_result_state(
            solver_status=result.solver_status,
            shifted_count=shifted_count,
            baseline_grid_kwh=result.baseline_metrics.grid_energy_used_kwh,
            optimized_grid_kwh=result.optimized_metrics.grid_energy_used_kwh,
            baseline_solar_kwh=result.baseline_metrics.solar_energy_used_kwh,
            optimized_solar_kwh=result.optimized_metrics.solar_energy_used_kwh,
            baseline_cost_rs=result.baseline_metrics.electricity_cost_rs,
            optimized_cost_rs=result.optimized_metrics.electricity_cost_rs
        )

        # Decision State Banner
        decision_html = f"""<div style="background-color: {state.banner_bg}; padding: 18px 22px; border-radius: 10px; border-left: 6px solid {state.border_color}; margin-bottom: 20px;">
<h3 style="color: {state.text_color}; margin: 0; font-weight: 800; font-size: 1.2rem;">{state.title} — {state.subtitle}</h3>
</div>"""
        st.markdown(textwrap.dedent(decision_html).strip(), unsafe_allow_html=True)

        # Top Results KPI Cards
        st.markdown("### Optimization Summary & Business Impact")
        k1, k2, k3, k4 = st.columns(4)
        with k1:
            render_kpi_card(
                "Solver Status", 
                f"{result.solver_status}", 
                "Google OR-Tools CP-SAT", 
                color_theme="green" if state.is_feasible else "red"
            )
        with k2:
            render_kpi_card(
                "Grid Energy Draw", 
                f"{result.optimized_metrics.grid_energy_used_kwh:.1f} kWh" if state.is_feasible else "N/A", 
                state.grid_delta_text, 
                color_theme="green" if state.code == "IMPROVED" else "gold",
                tooltip_text="Baseline grid energy minus optimized grid energy."
            )
        with k3:
            render_kpi_card(
                "Electricity Cost", 
                format_currency(result.optimized_metrics.electricity_cost_rs) if state.is_feasible else "N/A", 
                state.cost_delta_text, 
                color_theme="green" if state.code == "IMPROVED" else ("red" if state.code == "NO_BENEFIT" else "gold"),
                tooltip_text="Baseline electricity cost minus optimized electricity cost."
            )
        with k4:
            render_kpi_card(
                "Solar Energy Used", 
                f"{result.optimized_metrics.solar_energy_used_kwh:.1f} kWh" if state.is_feasible else "N/A", 
                state.solar_delta_text, 
                color_theme="cyan",
                tooltip_text="Solar energy utilized by production schedule."
            )

        st.markdown("---")

        # Hero Charts (Full Width for Maximum Readability - Section 10)
        st.markdown("### Solar Availability vs Demand")
        fig_curve = plot_solar_vs_demand_curve(
            result.hourly_solar_available,
            result.hourly_baseline_demand,
            result.hourly_optimized_demand,
            f"SOLAR AVAILABILITY VS DEMAND ({selected_factory})"
        )
        st.plotly_chart(fig_curve, use_container_width=True)

        st.markdown("### Baseline vs SOLAR SYNC Impact")
        fig_comp = plot_baseline_vs_optimized_comparison(
            result.baseline_metrics.grid_energy_used_kwh,
            result.optimized_metrics.grid_energy_used_kwh,
            result.baseline_metrics.solar_energy_used_kwh,
            result.optimized_metrics.solar_energy_used_kwh,
            result.baseline_metrics.electricity_cost_rs,
            result.optimized_metrics.electricity_cost_rs
        )
        st.plotly_chart(fig_comp, use_container_width=True)

        st.markdown("---")

        # Detailed Recommended Schedule Table
        st.markdown("### SolarSync Recommended Production Schedule")
        recs = recommender.generate_recommendations(result)
        
        table_data = []
        for r in recs:
            if r.shift_hours == 0:
                reason_str = f"✓ No schedule change required. Current timing ({r.baseline_start}) is already optimal."
                shift_str = "0h (Optimal)"
            else:
                reason_str = r.reason
                shift_str = f"+{r.shift_hours}h" if r.shift_hours > 0 else f"{r.shift_hours}h"

            table_data.append({
                "Job ID": r.job_id,
                "Product": r.product_id,
                "Machine": r.machine_id,
                "Baseline Start": r.baseline_start,
                "Recommended Start": r.recommended_start,
                "Shift Window": shift_str,
                "Solar kWh": f"{r.solar_used_kwh:.1f}",
                "Grid kWh": f"{r.grid_used_kwh:.1f}",
                "Est. Savings": format_currency(r.estimated_savings_rs),
                "Deadline Status": r.deadline_status,
                "Decision Rationale": reason_str
            })
        
        df_recs = pd.DataFrame(table_data)
        # Display main clean table without Decision Rationale column crowding
        df_main_view = df_recs[["Job ID", "Product", "Machine", "Baseline Start", "Recommended Start", "Shift Window", "Solar kWh", "Grid kWh", "Est. Savings", "Deadline Status"]]
        st.dataframe(df_main_view, use_container_width=True, hide_index=True)

        # Full Decision Rationale Detail Callout Section (Section 27 & 28)
        with st.expander("📋 View Detailed Business Rationale & Solver Constraints per Job", expanded=True):
            for r in recs:
                if r.shift_hours != 0:
                    badge_color = "#059669"
                    bg_color = "#ECFDF5"
                    border_c = "#6EE7B7"
                    title_text = f"SHIFT RECOMMENDED: {r.job_id} ({r.product_id}) on Machine {r.machine_id}"
                else:
                    badge_color = "#D97706"
                    bg_color = "#FFFBEB"
                    border_c = "#FCD34D"
                    title_text = f"KEEP CURRENT TIMING: {r.job_id} ({r.product_id}) on Machine {r.machine_id}"

                rat_html = f"""<div style="background-color: {bg_color}; border: 1px solid {border_c}; border-left: 5px solid {badge_color}; border-radius: 8px; padding: 14px 18px; margin-bottom: 12px;">
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
<b style="color: #0F172A; font-size: 0.95rem;">{title_text}</b>
<span style="background: {badge_color}; color: #FFFFFF; font-size: 0.75rem; font-weight: 700; padding: 3px 8px; border-radius: 4px;">Baseline {r.baseline_start} ➔ Rec {r.recommended_start}</span>
</div>
<div style="color: #334155; font-size: 0.88rem; line-height: 1.4;">
<b>Solver Rationale:</b> {r.reason}<br>
<span style="color: #64748B; font-size: 0.82rem;">Solar kWh: <b>{r.solar_used_kwh:.1f}</b> | Grid kWh: <b>{r.grid_used_kwh:.1f}</b> | Est. Savings: <b style="color: #059669;">{format_currency(r.estimated_savings_rs)}</b> | Deadline: <b>{r.deadline_status}</b></span>
</div>
</div>"""
                st.markdown(textwrap.dedent(rat_html).strip(), unsafe_allow_html=True)

        # Decision Report & Data Export Hub (Section 28, 31, 33)
        st.markdown("### Export Decision Reports & Operational Data")
        exp_c1, exp_c2 = st.columns(2)
        with exp_c1:
            pdf_bytes = generate_pdf_decision_report(result, factory_info={"factory_name": factories[factories['factory_id']==selected_factory]['factory_name'].values[0]})
            st.download_button(
                label="📥 Download Decision Report (PDF)",
                data=pdf_bytes,
                file_name=f"SolarSync_Decision_Report_{selected_factory}_{selected_date}.pdf",
                mime="application/pdf",
                use_container_width=True,
                type="primary"
            )
        with exp_c2:
            excel_bytes = generate_excel_decision_report(result)
            st.download_button(
                label="📥 Download Detailed Data (Excel)",
                data=excel_bytes,
                file_name=f"SolarSync_Detailed_Data_{selected_factory}_{selected_date}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

        with st.expander("🛠️ Advanced Technical Data Export (CSV)", expanded=False):
            csv_bytes = df_recs.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Technical Export (CSV)",
                data=csv_bytes,
                file_name=f"SolarSync_Schedule_{selected_factory}_{selected_date}.csv",
                mime="text/csv",
                use_container_width=True
            )
