import os
import sys
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from typing import List, Dict, Any

if os.path.exists(r'D:\python_packages') and r'D:\python_packages' not in sys.path:
    sys.path.insert(0, r'D:\python_packages')

LIGHT_LAYOUT_CONFIG = {
    "paper_bgcolor": "rgba(255, 255, 255, 0.0)",
    "plot_bgcolor": "#FFFFFF",
    "font": {"color": "#0F172A", "family": "Inter, 'Segoe UI', Roboto, Arial, sans-serif"},
    "xaxis": {
        "showgrid": True, 
        "gridcolor": "#F1F5F9", 
        "zerolinecolor": "#CBD5E1",
        "title_font": {"size": 13, "color": "#334155", "family": "Inter, sans-serif"},
        "tickfont": {"size": 11, "color": "#475569"}
    },
    "yaxis": {
        "showgrid": True, 
        "gridcolor": "#F1F5F9", 
        "zerolinecolor": "#CBD5E1",
        "title_font": {"size": 13, "color": "#334155", "family": "Inter, sans-serif"},
        "tickfont": {"size": 11, "color": "#475569"}
    },
    "legend": {
        "bgcolor": "rgba(255, 255, 255, 0.95)", 
        "bordercolor": "#E2E8F0", 
        "borderwidth": 1,
        "font": {"color": "#1E293B", "size": 11}
    },
    "margin": {"l": 50, "r": 40, "t": 55, "b": 45}
}

DARK_LAYOUT_CONFIG = LIGHT_LAYOUT_CONFIG

def plot_solar_vs_demand_curve(
    hourly_solar: np.ndarray, 
    hourly_baseline_demand: np.ndarray, 
    hourly_optimized_demand: np.ndarray = None,
    title: str = "SOLAR AVAILABILITY VS DEMAND"
) -> go.Figure:
    """
    Renders the primary SOLAR SYNC hero chart overlaying available solar generation against baseline & optimized production demand.
    Highlights the peak solar window (10:00–14:00).
    """
    hours = list(range(24))
    fig = go.Figure()

    # Highlighted Solar-Rich Production Window (Shaded Green Region)
    fig.add_vrect(
        x0=10, x1=14,
        fillcolor="rgba(16, 185, 129, 0.12)",
        layer="below",
        line_width=1,
        line_color="rgba(16, 185, 129, 0.3)",
        annotation_text="Peak Solar Window (10:00–14:00)",
        annotation_position="top left",
        annotation_font=dict(size=11, color="#059669", family="Inter, sans-serif")
    )

    # Solar Available Area Curve (Warm Amber)
    fig.add_trace(go.Scatter(
        x=hours,
        y=hourly_solar,
        name="Available Solar Power (kW)",
        mode="lines",
        fill="tozeroy",
        line=dict(color="#D97706", width=3),
        fillcolor="rgba(245, 158, 11, 0.20)"
    ))

    # Baseline Demand Curve (Crimson Red Dashed)
    fig.add_trace(go.Scatter(
        x=hours,
        y=hourly_baseline_demand,
        name="Baseline Production Demand (kW)",
        mode="lines+markers",
        line=dict(color="#DC2626", width=2.5, dash="dash"),
        marker=dict(size=6, symbol="circle")
    ))

    # Optimized Demand Curve (Emerald Green Solid)
    if hourly_optimized_demand is not None:
        fig.add_trace(go.Scatter(
            x=hours,
            y=hourly_optimized_demand,
            name="SOLAR SYNC Optimized Demand (kW)",
            mode="lines+markers",
            line=dict(color="#059669", width=3.5),
            marker=dict(size=7, symbol="diamond")
        ))

    fig.update_layout(
        title={"text": f"<b>{title}</b>", "x": 0.0, "font": {"size": 15, "color": "#0F172A"}},
        xaxis_title="Hour of Day (00:00 - 23:00)",
        yaxis_title="Power Demand / Generation (kW)",
        hovermode="x unified",
        height=460,
        **LIGHT_LAYOUT_CONFIG
    )
    return fig

def plot_baseline_vs_optimized_comparison(
    baseline_grid_kwh: float,
    optimized_grid_kwh: float,
    baseline_solar_kwh: float,
    optimized_solar_kwh: float,
    baseline_cost_rs: float,
    optimized_cost_rs: float
) -> go.Figure:
    """
    Renders 3 distinct side-by-side subplot comparisons for Grid Energy (kWh), Solar Energy (kWh),
    and Total Electricity Cost (₹) with concise SOLAR SYNC titles.
    """
    fig = make_subplots(
        rows=1, cols=3,
        subplot_titles=(
            "GRID ENERGY",
            "SOLAR ENERGY",
            "ELECTRICITY COST"
        ),
        horizontal_spacing=0.08
    )

    x_labels = ["Baseline", "SOLAR SYNC"]

    # Chart 1: Grid Energy (kWh)
    fig.add_trace(
        go.Bar(
            x=x_labels,
            y=[baseline_grid_kwh, optimized_grid_kwh],
            marker_color=["#94A3B8", "#059669"],
            text=[f"{baseline_grid_kwh:,.1f} kWh", f"{optimized_grid_kwh:,.1f} kWh"],
            textposition="auto",
            name="Grid Energy (kWh)",
            showlegend=False
        ),
        row=1, col=1
    )

    # Chart 2: Solar Energy Used (kWh)
    fig.add_trace(
        go.Bar(
            x=x_labels,
            y=[baseline_solar_kwh, optimized_solar_kwh],
            marker_color=["#94A3B8", "#D97706"],
            text=[f"{baseline_solar_kwh:,.1f} kWh", f"{optimized_solar_kwh:,.1f} kWh"],
            textposition="auto",
            name="Solar Energy (kWh)",
            showlegend=False
        ),
        row=1, col=2
    )

    # Chart 3: Electricity Cost (₹)
    fig.add_trace(
        go.Bar(
            x=x_labels,
            y=[baseline_cost_rs, optimized_cost_rs],
            marker_color=["#94A3B8", "#2563EB"],
            text=[f"₹{baseline_cost_rs:,.0f}", f"₹{optimized_cost_rs:,.0f}"],
            textposition="auto",
            name="Electricity Cost (₹)",
            showlegend=False
        ),
        row=1, col=3
    )

    fig.update_yaxes(title_text="Grid Energy (kWh)", row=1, col=1, showgrid=True, gridcolor="#F1F5F9")
    fig.update_yaxes(title_text="Solar Energy (kWh)", row=1, col=2, showgrid=True, gridcolor="#F1F5F9")
    fig.update_yaxes(title_text="Electricity Cost (₹)", row=1, col=3, showgrid=True, gridcolor="#F1F5F9")

    fig.update_layout(
        title={"text": "<b>BASELINE VS SOLAR SYNC</b>", "x": 0.0, "font": {"size": 15, "color": "#0F172A"}},
        height=440,
        paper_bgcolor="rgba(255, 255, 255, 0.0)",
        plot_bgcolor="#FFFFFF",
        font={"color": "#0F172A", "family": "Inter, 'Segoe UI', Roboto, Arial, sans-serif"},
        margin={"l": 40, "r": 40, "t": 60, "b": 40}
    )
    return fig

def plot_hourly_tariff_structure() -> go.Figure:
    """Renders 24-hour electricity tariff rate structure (Peak vs Normal vs Offpeak)."""
    hours = list(range(24))
    rates = [9.25 if 18 <= h < 22 else (7.25 if 6 <= h < 18 else 5.75) for h in hours]
    colors = ["#DC2626" if 18 <= h < 22 else ("#D97706" if 6 <= h < 18 else "#059669") for h in hours]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=hours,
        y=rates,
        marker_color=colors,
        text=[f"₹{r}" for r in rates],
        textposition="auto",
        textfont=dict(size=10, color="#FFFFFF")
    ))

    fig.update_layout(
        title={"text": "<b>ELECTRICITY TARIFF STRUCTURE</b>", "x": 0.0, "font": {"size": 16, "color": "#0F172A"}},
        xaxis_title="Hour of Day",
        yaxis_title="Tariff Rate (₹/kWh)",
        height=440,
        **LIGHT_LAYOUT_CONFIG
    )
    return fig

def plot_historical_energy_trends(history_df: pd.DataFrame) -> go.Figure:
    """Plots historical daily energy consumption trends (Solar vs Grid)."""
    daily = history_df.groupby("date")[["solar_energy_used_kwh", "grid_energy_used_kwh"]].sum().reset_index()

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=daily["date"],
        y=daily["solar_energy_used_kwh"],
        name="Solar Energy Used (kWh)",
        stackgroup="one",
        fillcolor="rgba(245, 158, 11, 0.45)",
        line=dict(color="#D97706", width=2)
    ))
    fig.add_trace(go.Scatter(
        x=daily["date"],
        y=daily["grid_energy_used_kwh"],
        name="Grid Energy Used (kWh)",
        stackgroup="one",
        fillcolor="rgba(37, 99, 235, 0.45)",
        line=dict(color="#2563EB", width=2)
    ))

    fig.update_layout(
        title={"text": "<b>HISTORICAL ENERGY MIX (SOLAR VS GRID)</b>", "x": 0.0, "font": {"size": 16, "color": "#0F172A"}},
        xaxis_title="Date",
        yaxis_title="Total Daily Energy (kWh)",
        height=460,
        **LIGHT_LAYOUT_CONFIG
    )
    return fig
