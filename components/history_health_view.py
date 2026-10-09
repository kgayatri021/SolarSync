import os
import sys
import textwrap
import streamlit as st
import pandas as pd
import numpy as np

if os.path.exists(r'D:\python_packages') and r'D:\python_packages' not in sys.path:
    sys.path.insert(0, r'D:\python_packages')

from components.cards import render_kpi_card, render_section_header, render_badge
from components.charts import plot_historical_energy_trends, plot_hourly_tariff_structure
from src.validation import run_full_system_validation
from src.utils import format_currency, format_kwh

def render_history_health_view(datasets: dict):
    render_section_header("History & System Health", "Historical Industrial Energy Trends & Data Quality Integrity Verification")

    tab1, tab2 = st.tabs(["Historical Energy Analytics", "Data Quality & System Health Verification"])

    # -------------------------------------------------------------
    # Tab 1: Historical Energy Analytics
    # -------------------------------------------------------------
    with tab1:
        history = datasets["history"]

        tot_records = len(history)
        tot_energy = history["energy_consumed_kwh"].sum()
        tot_solar = history["solar_energy_used_kwh"].sum()
        tot_grid = history["grid_energy_used_kwh"].sum()
        tot_cost = history["total_operating_cost_rs"].sum()
        solar_pct = (tot_solar / tot_energy * 100.0) if tot_energy > 0 else 0.0

        min_date_str = pd.to_datetime(history["date"].min()).strftime("%b %Y")
        max_date_str = pd.to_datetime(history["date"].max()).strftime("%b %Y")
        date_range_str = f"{min_date_str} - {max_date_str}"

        h1, h2, h3, h4 = st.columns(4)
        with h1:
            render_kpi_card("Historical Records", f"{tot_records:,}", date_range_str, color_theme="gold")
        with h2:
            render_kpi_card("Historical Energy Consumed", format_kwh(tot_energy), f"{solar_pct:.1f}% Solar Share", color_theme="cyan")
        with h3:
            render_kpi_card("Historical Solar Used", format_kwh(tot_solar), f"Grid Draw: {format_kwh(tot_grid)}", color_theme="green")
        with h4:
            render_kpi_card("Total Operating Cost", format_currency(tot_cost), "Labour + Electricity", color_theme="orange")

        st.markdown("---")

        st.markdown("### Historical Daily Solar vs Grid Energy Share")
        fig_trend = plot_historical_energy_trends(history)
        st.plotly_chart(fig_trend, use_container_width=True)

        st.markdown("---")

        st.markdown("### Andhra Pradesh Electricity Tariff Rate Reference Structure")
        fig_tariff = plot_hourly_tariff_structure()
        st.plotly_chart(fig_tariff, use_container_width=True)

        with st.expander("View Historical Data Log Sample (HISTORICAL DATA)", expanded=False):
            st.dataframe(history.tail(500), use_container_width=True)

    # -------------------------------------------------------------
    # Tab 2: Data Quality & System Health Verification (Section 39)
    # -------------------------------------------------------------
    with tab2:
        report = run_full_system_validation(datasets)

        status_text = "OVERALL SYSTEM STATUS: HEALTHY" if report.is_healthy else "OVERALL SYSTEM STATUS: ISSUES DETECTED"
        bg_color = "#ECFDF5" if report.is_healthy else "#FEF2F2"
        border_color = "#059669" if report.is_healthy else "#DC2626"
        text_color = "#065F46" if report.is_healthy else "#991B1B"

        callout_html = f"""<div style="background-color: {bg_color}; padding: 18px 24px; border-radius: 10px; margin-bottom: 25px; border-left: 6px solid {border_color}; shadow: 0 1px 3px rgba(0,0,0,0.05);">
<h3 style="color: {text_color}; margin: 0; font-weight: 800; font-size: 1.15rem;">{status_text}</h3>
<p style="color: #475569; margin-top: 6px; margin-bottom: 0; font-size: 0.95rem;">
Automated audit engine dynamically verified all 7 core datasets (Schema, Data Types, FK Integrity, Range Checks, Maintenance, Physics & History Formulas).
</p>
</div>"""
        st.markdown(textwrap.dedent(callout_html).strip(), unsafe_allow_html=True)

        st.markdown("### Core Dataset Validation Matrix")
        cols = st.columns(4)
        for idx, (name, res) in enumerate(report.results.items()):
            col_target = cols[idx % 4]
            with col_target:
                badge_html = render_badge(res.dataset_name, "pass" if res.is_valid else "fail")
                card_html = f"""<div style="background: #FFFFFF; border-radius: 10px; padding: 16px; margin-bottom: 15px; border: 1px solid #E2E8F0; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
<div style="margin-bottom: 10px;">{badge_html}</div>
<div style="color: #0F172A; font-weight: 700; font-size: 1.05rem;">{res.dataset_name}</div>
<div style="color: #64748B; font-size: 0.85rem; margin-top: 4px;">Rows: <b>{res.row_count:,}</b> | Cols: <b>{res.col_count}</b></div>
<div style="color: #059669; font-size: 0.8rem; margin-top: 6px; font-weight: 600;">Errors: {len(res.errors)} | Warnings: {len(res.warnings)}</div>
</div>"""
                st.markdown(textwrap.dedent(card_html).strip(), unsafe_allow_html=True)

        with st.expander("Dataset Schema & Metric Audit Summary", expanded=False):
            audit_data = []
            for k, res in report.results.items():
                audit_data.append({
                    "Dataset": res.dataset_name,
                    "Row Count": f"{res.row_count:,}",
                    "Col Count": res.col_count,
                    "Validation Status": "PASSED" if res.is_valid else "FAILED",
                    "Error Count": len(res.errors),
                    "Key Metrics": str(res.metrics)
                })
            st.dataframe(pd.DataFrame(audit_data), use_container_width=True)
