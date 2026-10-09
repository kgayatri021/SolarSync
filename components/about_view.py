import os
import sys
import streamlit as st

if os.path.exists(r'D:\python_packages') and r'D:\python_packages' not in sys.path:
    sys.path.insert(0, r'D:\python_packages')

from components.cards import render_section_header

def render_about_view():
    render_section_header("About SOLAR SYNC", "PS07 - Solar-Aware Demand Shifting Scheduler | DRE Enterprise Hackathon '26")

    st.markdown("""
    ### Executive Overview
    **SOLAR SYNC** is an intelligent industrial decision-support and production scheduling platform engineered for manufacturing clusters in **North Coastal Andhra Pradesh** (Visakhapatnam, Anakapalli, Vizianagaram, Srikakulam).

    ### The Core Problem
    Industrial manufacturing facilities operate energy-intensive machinery while solar PV generation peaks during midday hours (10:00 - 15:00). 
    Uncoordinated production scheduling often runs heavy flexible jobs during evening peak tariff hours (18:00 - 22:00), resulting in high electricity bills, unnecessary grid power dependency, and wasted solar generation potential.

    ---

    ### The SOLAR SYNC Solution
    SOLAR SYNC integrates multi-modal industrial datasets:
    1. **Factory Specifications** (Grid capacity, contracted demand, installed solar capacity, battery storage)
    2. **Machine Constraints** (Rated power, standby power, production rates, scheduled maintenance windows)
    3. **Production Jobs** (Release time, deadline, duration, machine eligibility, shiftability flag)
    4. **Workforce Availability** (Skills, shift windows, maximum daily hours, overtime rules)
    5. **Solar & Weather Forecasts** (GHI, DNI, DHI, cloud cover, capacity factors)
    6. **Electricity Tariffs** (AP Industrial HT1 / LT3 peak, normal, and off-peak tariffs)

    ---

    ### Optimization Architecture (OR-Tools CP-SAT)
    SOLAR SYNC formulates demand shifting as a **Constraint Programming (CP-SAT)** integer optimization problem:
    - **Objective:** $\\text{Minimize Total Cost} = \\sum_{h=0}^{23} \\text{GridEnergy}_h \\times \\text{Tariff}_h + \\text{LabourCost}_h + \\text{OvertimeCost}_h$
    - **Constraints:**
      - Job Release Time & Deadline Windows: $r_j \\le \\text{Start}_j \\le dl_j - d_j$
      - Non-Shiftable Job Protection: $\\text{can\\_shift} = \\text{False} \\implies \\text{Start}_j = r_j$
      - Machine Maintenance Windows: Zero job execution during scheduled maintenance.
      - Machine Single-Job Execution: No overlap between jobs on the same machine.
      - Grid Connection Capacity: Total active power $\\le C_{\\text{grid}}$ at any hour.
      - Workforce Skill Supply: Active job worker requirements satisfied by shift roster.

    ---

    ### Product Principles & Governance
    - **Decision Support System:** SOLAR SYNC recommends optimal production timing for factory managers; it does **NOT** claim direct control over the government electricity grid.
    - **Zero Fake Data:** All displayed metrics originate from verified calculations over the 7 source CSV datasets.
    - **Explainable Rationale:** Every job shift recommendation is accompanied by an explicit quantitative explanation.
    """)
