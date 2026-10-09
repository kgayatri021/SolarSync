import os
import sys
import streamlit as st
import pandas as pd
import numpy as np

if os.path.exists(r'D:\python_packages') and r'D:\python_packages' not in sys.path:
    sys.path.insert(0, r'D:\python_packages')

from components.cards import render_kpi_card, render_section_header
from components.charts import plot_historical_energy_trends, plot_hourly_tariff_structure
from src.utils import format_currency, format_kwh

def render_history_view(datasets: dict):
    render_section_header("Historical Analytics", "Analysis of Historical Industrial Production & Energy History")

    history = datasets["history"]

    tot_records = len(history)
    tot_energy = history["energy_consumed_kwh"].sum()
    tot_solar = history["solar_energy_used_kwh"].sum()
    tot_grid = history["grid_energy_used_kwh"].sum()
    tot_cost = history["total_operating_cost_rs"].sum()
    solar_pct = (tot_solar / tot_energy * 100.0) if tot_energy > 0 else 0.0

    h1, h2, h3, h4 = st.columns(4)
    with h1:
        render_kpi_card("Historical Records", f"{tot_records:,}", "May 2026 - Oct 2026", color_theme="gold")
    with h2:
        render_kpi_card("Historical Energy Consumed", format_kwh(tot_energy), f"{solar_pct:.1f}% Solar Share", color_theme="cyan")
    with h3:
        render_kpi_card("Historical Solar Used", format_kwh(tot_solar), f"Grid Draw: {format_kwh(tot_grid)}", color_theme="green")
    with h4:
        render_kpi_card("Total Operating Cost", format_currency(tot_cost), "Labour + Electricity", color_theme="orange")

    st.markdown("---")

    # Historical Daily Energy Trend Chart
    st.markdown("### Historical Daily Solar vs Grid Energy Share")
    fig_trend = plot_historical_energy_trends(history)
    st.plotly_chart(fig_trend, use_container_width=True)

    st.markdown("---")

    # Tariff Structure Reference Chart
    st.markdown("### Andhra Pradesh Electricity Tariff Rate Reference")
    fig_tariff = plot_hourly_tariff_structure()
    st.plotly_chart(fig_tariff, use_container_width=True)

    st.markdown("---")

    st.markdown("### Historical Energy Data Log (HISTORICAL DATA)")
    st.dataframe(history.tail(500), use_container_width=True)
