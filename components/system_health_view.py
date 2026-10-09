import os
import sys
import streamlit as st
import pandas as pd

if os.path.exists(r'D:\python_packages') and r'D:\python_packages' not in sys.path:
    sys.path.insert(0, r'D:\python_packages')

from components.cards import render_kpi_card, render_section_header, render_badge
from src.validation import run_full_system_validation

def render_system_health_view(datasets: dict):
    render_section_header("Data Quality & System Health", "System Integrity, Data Schema Verification & Audit Engine")

    report = run_full_system_validation(datasets)

    status_text = "OVERALL SYSTEM STATUS: HEALTHY" if report.is_healthy else "OVERALL SYSTEM STATUS: ISSUES DETECTED"
    bg_color = "#ECFDF5" if report.is_healthy else "#FEF2F2"
    border_color = "#059669" if report.is_healthy else "#DC2626"
    text_color = "#065F46" if report.is_healthy else "#991B1B"

    st.markdown(f"""
    <div style="background-color: {bg_color}; padding: 18px 24px; border-radius: 10px; margin-bottom: 25px; border-left: 6px solid {border_color}; shadow: 0 1px 3px rgba(0,0,0,0.05);">
        <h3 style="color: {text_color}; margin: 0; font-weight: 800; font-size: 1.15rem;">{status_text}</h3>
        <p style="color: #475569; margin-top: 6px; margin-bottom: 0; font-size: 0.95rem;">
            Automated audit engine dynamically verified all 7 core datasets (Schema, Data Types, FK Integrity, Range Checks, Maintenance, Physics & History Formulas).
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### Core Dataset Validation Status Matrix")

    # Grid of status cards for all 7 CSVs
    cols = st.columns(4)
    for idx, (name, res) in enumerate(report.results.items()):
        col_target = cols[idx % 4]
        with col_target:
            badge_html = render_badge(res.dataset_name, "pass" if res.is_valid else "fail")
            st.markdown(f"""
            <div style="background: #FFFFFF; border-radius: 10px; padding: 16px; margin-bottom: 15px; border: 1px solid #E2E8F0; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
                <div style="margin-bottom: 10px;">{badge_html}</div>
                <div style="color: #0F172A; font-weight: 700; font-size: 1.05rem;">{res.dataset_name}</div>
                <div style="color: #64748B; font-size: 0.85rem; margin-top: 4px;">Rows: <b>{res.row_count:,}</b> | Cols: <b>{res.col_count}</b></div>
                <div style="color: #059669; font-size: 0.8rem; margin-top: 6px; font-weight: 600;">Errors: {len(res.errors)} | Warnings: {len(res.warnings)}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    st.markdown("### Dataset Schema & Metric Audit Summary")
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
