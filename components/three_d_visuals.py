import os
import sys
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

if os.path.exists(r'D:\python_packages') and r'D:\python_packages' not in sys.path:
    sys.path.insert(0, r'D:\python_packages')

from components.charts import LIGHT_LAYOUT_CONFIG

def plot_3d_factory_cluster(factories_df: pd.DataFrame) -> go.Figure:
    """
    Renders an interactive 3D Geographic Industrial Cluster elevation map for North Coastal AP factories.
    X = Longitude, Y = Latitude, Z = Installed Solar Capacity (kW), Marker Size = Grid Capacity (kW).
    Uses mode='markers' to avoid text overlap clutter, showing rich detail on hover.
    """
    district_coords = {
        "Visakhapatnam": (17.6868, 83.2185),
        "Anakapalli": (17.6913, 83.0039),
        "Vizianagaram": (18.1124, 83.3976),
        "Srikakulam": (18.2949, 83.8938)
    }

    df = factories_df.copy()
    lats = []
    lons = []
    np.random.seed(42)
    for _, row in df.iterrows():
        dist = str(row.get("district", "Visakhapatnam"))
        base_lat, base_lon = district_coords.get(dist, (17.6868, 83.2185))
        lats.append(base_lat + np.random.uniform(-0.06, 0.06))
        lons.append(base_lon + np.random.uniform(-0.06, 0.06))

    df["lat"] = lats
    df["lon"] = lons

    # Clean hover text array
    hover_texts = [
        f"<b>{row['factory_name']} ({row['factory_id']})</b><br>" +
        f"District: {row.get('district', 'N/A')}<br>" +
        f"Solar Capacity: {row['installed_solar_capacity_kw']:.0f} kW<br>" +
        f"Grid Connection: {row['grid_connection_capacity_kw']:.0f} kW<br>" +
        f"Baseline Daily Energy: {row['baseline_daily_energy_kwh']:,.0f} kWh"
        for _, row in df.iterrows()
    ]

    fig = go.Figure(data=[go.Scatter3d(
        x=df["lon"],
        y=df["lat"],
        z=df["installed_solar_capacity_kw"],
        mode="markers",
        hoverinfo="text",
        hovertext=hover_texts,
        marker=dict(
            size=np.clip(df["grid_connection_capacity_kw"] / 35.0, 6, 22),
            color=df["baseline_daily_energy_kwh"],
            colorscale="Viridis",
            colorbar=dict(title="Baseline Energy (kWh)", title_font=dict(color="#0F172A", size=11)),
            opacity=0.9
        )
    )])

    fig.update_layout(
        title={"text": "<b>3D Industrial Cluster Elevation Map (North Coastal AP)</b>", "x": 0.0, "font": {"size": 15, "color": "#0F172A"}},
        scene=dict(
            xaxis_title="Longitude (°E)",
            yaxis_title="Latitude (°N)",
            zaxis_title="Solar Capacity (kW)",
            xaxis=dict(gridcolor="#E2E8F0", backgroundcolor="#F8FAFC"),
            yaxis=dict(gridcolor="#E2E8F0", backgroundcolor="#F8FAFC"),
            zaxis=dict(gridcolor="#E2E8F0", backgroundcolor="#F8FAFC")
        ),
        height=480,
        **LIGHT_LAYOUT_CONFIG
    )
    return fig

def plot_2d_factory_cluster_map(factories_df: pd.DataFrame) -> go.Figure:
    """
    Renders a clean 2D Geographic Map of factories across North Coastal AP districts (Section 32).
    """
    district_coords = {
        "Visakhapatnam": (17.6868, 83.2185),
        "Anakapalli": (17.6913, 83.0039),
        "Vizianagaram": (18.1124, 83.3976),
        "Srikakulam": (18.2949, 83.8938)
    }

    df = factories_df.copy()
    lats = []
    lons = []
    np.random.seed(42)
    for _, row in df.iterrows():
        dist = str(row.get("district", "Visakhapatnam"))
        base_lat, base_lon = district_coords.get(dist, (17.6868, 83.2185))
        lats.append(base_lat + np.random.uniform(-0.06, 0.06))
        lons.append(base_lon + np.random.uniform(-0.06, 0.06))

    df["lat"] = lats
    df["lon"] = lons

    fig = px.scatter(
        df,
        x="lon",
        y="lat",
        size="installed_solar_capacity_kw",
        color="district",
        hover_name="factory_name",
        hover_data={
            "factory_id": True,
            "installed_solar_capacity_kw": ":.0f",
            "grid_connection_capacity_kw": ":.0f",
            "baseline_daily_energy_kwh": ":,.0f",
            "lat": False,
            "lon": False
        },
        title="2D Regional Industrial Cluster Geographic Layout"
    )

    fig.update_layout(
        title={"text": "<b>2D Regional Industrial Cluster Map (North Coastal AP)</b>", "x": 0.0, "font": {"size": 15, "color": "#0F172A"}},
        xaxis_title="Longitude (°E)",
        yaxis_title="Latitude (°N)",
        height=480,
        **LIGHT_LAYOUT_CONFIG
    )
    return fig

def plot_3d_solar_landscape(solar_df: pd.DataFrame) -> go.Figure:
    """
    Renders a 3D Surface map of Solar Generation across Hours of Day (0..23) and Locations.
    """
    pivot = solar_df.pivot_table(
        index="hour", 
        columns="location", 
        values="solar_capacity_factor", 
        aggfunc="mean"
    ).fillna(0.0)

    z_matrix = pivot.to_numpy()
    x_locs = list(pivot.columns)
    y_hours = list(pivot.index)

    fig = go.Figure(data=[go.Surface(
        z=z_matrix,
        x=x_locs,
        y=y_hours,
        colorscale="YlOrRd",
        colorbar=dict(title="Solar Factor", title_font=dict(color="#0F172A"))
    )])

    fig.update_layout(
        title={"text": "<b>3D Regional Solar Intensity Surface Map</b>", "x": 0.0, "font": {"size": 15, "color": "#0F172A"}},
        scene=dict(
            xaxis_title="Cluster Location",
            yaxis_title="Hour of Day (0..23)",
            zaxis_title="Solar Capacity Factor",
            xaxis=dict(gridcolor="#E2E8F0", backgroundcolor="#F8FAFC"),
            yaxis=dict(gridcolor="#E2E8F0", backgroundcolor="#F8FAFC"),
            zaxis=dict(gridcolor="#E2E8F0", backgroundcolor="#F8FAFC")
        ),
        height=480,
        **LIGHT_LAYOUT_CONFIG
    )
    return fig
