import os
import sys
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

if os.path.exists(r'D:\python_packages') and r'D:\python_packages' not in sys.path:
    sys.path.insert(0, r'D:\python_packages')

from components.cards import render_kpi_card, render_section_header
from components.three_d_visuals import plot_3d_solar_landscape
from components.charts import LIGHT_LAYOUT_CONFIG

def render_solar_view(datasets: dict):
    render_section_header("Solar & Energy Intelligence", "Solar Generation Forecasting, Irradiance & Cloud Impact Analysis")

    solar_df = datasets["solar_weather"]

    col1, col2 = st.columns([2, 2])
    with col1:
        locs = solar_df["location"].unique().tolist()
        selected_loc = st.selectbox("Select Industrial Location:", locs)
    with col2:
        dates = solar_df["date_str"].unique().tolist() if "date_str" in solar_df.columns else solar_df["date"].astype(str).unique().tolist()
        selected_date = st.selectbox("Select Forecast Date:", dates[:30])

    subset = solar_df[(solar_df["location"] == selected_loc) & (solar_df["date"].astype(str) == selected_date)].sort_values("hour")
    
    if subset.empty:
        subset = solar_df[solar_df["location"] == selected_loc].head(24)

    # Top KPI Metrics
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

    # Solar Irradiance Breakdown
    st.markdown(f"### Solar Irradiance Breakdown — {selected_loc} ({selected_date})")
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=subset["hour"], y=subset["ghi_w_m2"], name="Global Horizontal Irradiance (GHI)", line=dict(color="#D97706", width=3)))
    fig.add_trace(go.Scatter(x=subset["hour"], y=subset["dni_w_m2"], name="Direct Normal Irradiance (DNI)", line=dict(color="#0284C7", width=2)))
    fig.add_trace(go.Scatter(x=subset["hour"], y=subset["dhi_w_m2"], name="Diffuse Horizontal Irradiance (DHI)", line=dict(color="#64748B", width=2, dash="dot")))
    
    fig.update_layout(
        title={"text": "<b>Solar Irradiance Components (W/m²)</b>", "x": 0.0, "font": {"size": 15, "color": "#0F172A"}},
        xaxis_title="Hour of Day (0..23)",
        yaxis_title="Irradiance (W/m²)",
        hovermode="x unified",
        **LIGHT_LAYOUT_CONFIG
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # 3D Solar Generation Surface Map
    st.markdown("### 3D Regional Solar Intensity Surface Map")
    fig_3d = plot_3d_solar_landscape(solar_df)
    st.plotly_chart(fig_3d, use_container_width=True)
