import os
import sys
import textwrap
import streamlit as st

# Ensure D:\python_packages is in sys.path
if os.path.exists(r'D:\python_packages') and r'D:\python_packages' not in sys.path:
    sys.path.insert(0, r'D:\python_packages')

# Page Configuration - Wide desktop layout (Section 10 & 11)
st.set_page_config(
    page_title="SOLAR SYNC | Industrial Demand Shifting Platform",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Light Enterprise SaaS Theme CSS - Standardized Font Stack & Cross-Browser Styling
css_code = """<style>
/* Base Font Family & Smoothing */
html, body, [class*="css"], .stApp {
    font-family: Inter, 'Segoe UI', Roboto, Arial, sans-serif !important;
}

/* Hide default Streamlit top header bar completely */
header[data-testid="stHeader"] {
    display: none !important;
}
.stAppHeader {
    display: none !important;
}
.block-container {
    padding-top: 1rem !important;
    padding-bottom: 2rem !important;
    max-width: 1400px !important;
}

/* Page Background: Off-white / Light Neutral Gray */
.stApp {
    background-color: #F8FAFC !important;
    color: #0F172A !important;
}

/* Dark Navy Sidebar */
[data-testid="stSidebar"] {
    background-color: #0F172A !important;
    border-right: 1px solid #1E293B !important;
}

/* Sidebar Typography (avoid wildcards with !important to protect input fields) */
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] h4,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] .stMarkdown {
    color: #F8FAFC !important;
}

/* Sidebar Selectbox Styling */
[data-testid="stSidebar"] div[data-baseweb="select"] > div {
    background-color: #FFFFFF !important;
    border: 1px solid #CBD5E1 !important;
    border-radius: 6px !important;
}
[data-testid="stSidebar"] div[data-baseweb="select"] span,
[data-testid="stSidebar"] div[data-baseweb="select"] div {
    color: #0F172A !important;
    font-weight: 600 !important;
}
[data-testid="stSidebar"] div[data-baseweb="select"] svg {
    fill: #2563EB !important;
}

/* Sidebar Input & Date Control Styling (Dark Text on White Background for Chrome & Edge) */
[data-testid="stSidebar"] div[data-baseweb="input"] {
    background-color: #FFFFFF !important;
    border-radius: 6px !important;
    border: 1px solid #CBD5E1 !important;
}
[data-testid="stSidebar"] div[data-baseweb="input"] input,
[data-testid="stSidebar"] div[data-baseweb="input"] div,
[data-testid="stSidebar"] div[data-baseweb="input"] span {
    color: #0F172A !important;
    background-color: #FFFFFF !important;
    font-weight: 600 !important;
}

/* Streamlit Main Container Inputs & Controls */
.main div[data-baseweb="select"] > div,
.main div[data-baseweb="input"] > div,
.main div[data-testid="stDateInput"] input,
div[data-testid="stDateInput"] input,
input[type="date"] {
    background-color: #FFFFFF !important;
    border: 1px solid #CBD5E1 !important;
    color: #0F172A !important;
    border-radius: 6px !important;
    font-weight: 600 !important;
}

/* Datepicker Calendar Popovers (Ensure visibility across Edge, Chrome, Antigravity) */
div[data-baseweb="popover"],
div[data-baseweb="calendar"],
div[role="tooltip"] {
    background-color: #FFFFFF !important;
    color: #0F172A !important;
    border-radius: 8px !important;
    box-shadow: 0 4px 20px rgba(0,0,0,0.15) !important;
}
div[data-baseweb="popover"] *,
div[data-baseweb="calendar"] * {
    color: #0F172A !important;
}
div[data-baseweb="calendar"] [aria-selected="true"] {
    background-color: #2563EB !important;
    color: #FFFFFF !important;
}

/* Buttons */
.stButton>button {
    border-radius: 6px;
    font-weight: 700;
    letter-spacing: 0.3px;
    transition: all 0.2s ease-in-out;
}

/* Primary Action Buttons */
button[kind="primary"] {
    background-color: #2563EB !important;
    color: #FFFFFF !important;
    border: none !important;
}
button[kind="primary"]:hover {
    background-color: #1D4ED8 !important;
}

/* Eliminate Accidental Pink/Magenta Focus Borders */
*:focus, div[data-baseweb="select"]:focus, input:focus {
    outline: none !important;
    border-color: #2563EB !important;
    box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.2) !important;
}

/* Typography */
h1, h2, h3, h4 {
    color: #0F172A !important;
    font-family: Inter, 'Segoe UI', Roboto, Arial, sans-serif !important;
}

/* Table styling */
.dataframe {
    border: 1px solid #E2E8F0 !important;
    border-radius: 6px !important;
}
</style>"""

st.markdown(textwrap.dedent(css_code).strip(), unsafe_allow_html=True)

# Imports from SolarSync src and components
from src.data_loader import load_all_datasets
from src.solar_engine import SolarEngine
from src.demand_engine import DemandEngine
from src.cost_engine import CostEngine
from src.workforce_optimizer import WorkforceOptimizer
from src.scheduler import SolarSyncScheduler
from src.recommender import RecommendationEngine
from src.scenario_engine import ScenarioEngine

from components.dashboard import render_executive_dashboard
from components.factory_view import render_factory_view
from components.scheduler_view import render_scheduler_view
from components.scenario_view import render_scenario_view
from components.energy_workforce_view import render_energy_workforce_view
from components.history_health_view import render_history_health_view
from components.about_view import render_about_view

def main():
    # Sidebar Header (Clean Professional Enterprise Header - Section 27)
    sidebar_header = """<div style="text-align: left; padding: 10px 0 20px 0; border-bottom: 1px solid #1E293B; margin-bottom: 20px;">
<h1 style="color: #F59E0B !important; margin: 0; font-size: 1.7rem; font-weight: 800; letter-spacing: 0.8px;">SOLAR SYNC</h1>
<div style="color: #38BDF8 !important; font-size: 0.8rem; font-weight: 700; margin-top: 4px;">Solar-Aware Demand Shifting & Scheduling Platform</div>
<div style="color: #94A3B8 !important; font-size: 0.72rem; margin-top: 2px;">DRE Enterprise Hackathon '26 (PS07)</div>
</div>"""

    st.sidebar.markdown(textwrap.dedent(sidebar_header).strip(), unsafe_allow_html=True)

    # Load datasets & initialize engines once
    try:
        datasets = load_all_datasets()
        solar_engine = SolarEngine(datasets["solar_weather"], datasets["factories"])
        demand_engine = DemandEngine(datasets["jobs"], datasets["machines"], datasets["tariffs"], datasets["workforce"])
        cost_engine = CostEngine(datasets["tariffs"])
        workforce_optimizer = WorkforceOptimizer(datasets["workforce"], datasets["machines"])
        scheduler = SolarSyncScheduler(solar_engine, cost_engine, workforce_optimizer, datasets["machines"], datasets["factories"])
        recommender = RecommendationEngine()
        scenario_engine = ScenarioEngine(scheduler, demand_engine)
    except Exception as e:
        st.error(f"Error loading system datasets: {str(e)}")
        st.stop()

    # Categorized Navigation Menu (Section 26 & 41)
    pages = [
        "Executive Dashboard",
        "Factory Intelligence",
        "Smart Scheduler",
        "Scenario Simulator",
        "Energy & Workforce",
        "History & System Health",
        "About SOLAR SYNC"
    ]

    selected_page = st.sidebar.radio("Navigation Menu:", pages, index=0, key="main_nav_menu")

    # Global Application State Management (Section 4 & 5)
    fac_options = datasets["factories"]["factory_id"].tolist()
    if "selected_factory_id" not in st.session_state or st.session_state["selected_factory_id"] not in fac_options:
        st.session_state["selected_factory_id"] = "FAC_016" if "FAC_016" in fac_options else fac_options[0]
    if "selected_date" not in st.session_state:
        import datetime
        st.session_state["selected_date"] = datetime.date(2026, 8, 10)

    st.sidebar.markdown("---")
    st.sidebar.markdown("### Global Facility & Date Context")

    curr_fac = st.session_state["selected_factory_id"]
    curr_fac_idx = fac_options.index(curr_fac) if curr_fac in fac_options else 0

    selected_fac = st.sidebar.selectbox(
        "Active Industrial Facility:",
        options=fac_options,
        index=curr_fac_idx,
        format_func=lambda fid: f"{fid} - {datasets['factories'][datasets['factories']['factory_id']==fid]['factory_name'].values[0]}",
        key="global_fac_select"
    )
    if selected_fac != st.session_state["selected_factory_id"]:
        st.session_state["selected_factory_id"] = selected_fac

    selected_dt = st.sidebar.date_input(
        "Target Analysis Date:",
        value=st.session_state["selected_date"],
        key="global_date_select"
    )
    if selected_dt != st.session_state["selected_date"]:
        st.session_state["selected_date"] = selected_dt

    st.sidebar.markdown("---")
    
    geo_html = """<div style="padding: 10px 12px; background: #1E293B; border-radius: 8px; border: 1px solid #334155; font-size: 0.78rem; color: #CBD5E1;">
<b style="color: #F59E0B;">North Coastal Andhra Pradesh</b><br>
Visakhapatnam • Anakapalli • Vizianagaram • Srikakulam
</div>"""
    st.sidebar.markdown(textwrap.dedent(geo_html).strip(), unsafe_allow_html=True)

    # Unified Header Banner (Section 10 & 27)
    header_banner = """<div style="background-color: #FFFFFF; border-bottom: 1px solid #E2E8F0; padding: 12px 20px; margin-bottom: 20px; border-radius: 8px; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 1px 3px rgba(0,0,0,0.04);">
<div>
<span style="font-weight: 800; font-size: 1.2rem; color: #0F172A; letter-spacing: 0.5px;">SOLAR SYNC</span>
<span style="color: #64748B; margin-left: 10px; font-size: 0.9rem;">Solar-Aware Industrial Demand Shifting & Scheduling Platform</span>
</div>
<div style="color: #0284C7; font-weight: 700; font-size: 0.85rem;">
DRE Enterprise Hackathon '26 • PS07
</div>
</div>"""
    st.markdown(textwrap.dedent(header_banner).strip(), unsafe_allow_html=True)

    # Page Routing (Section 17)
    if selected_page == "Executive Dashboard":
        render_executive_dashboard(datasets)
    elif selected_page == "Factory Intelligence":
        render_factory_view(datasets, solar_engine, demand_engine)
    elif selected_page == "Smart Scheduler":
        render_scheduler_view(datasets, scheduler, demand_engine, recommender)
    elif selected_page == "Scenario Simulator":
        render_scenario_view(datasets, scenario_engine)
    elif selected_page == "Energy & Workforce":
        render_energy_workforce_view(datasets, workforce_optimizer)
    elif selected_page == "History & System Health":
        render_history_health_view(datasets)
    elif selected_page == "About SOLAR SYNC":
        render_about_view()

if __name__ == "__main__":
    main()
