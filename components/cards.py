import os
import sys
import textwrap
import streamlit as st

if os.path.exists(r'D:\python_packages') and r'D:\python_packages' not in sys.path:
    sys.path.insert(0, r'D:\python_packages')

def render_kpi_card(
    title: str, 
    value: str, 
    delta: str = None, 
    icon: str = "", 
    color_theme: str = "gold",
    tooltip_text: str = None
):
    """
    Renders a custom styled KPI card in Streamlit (Light Enterprise SaaS Theme).
    Strictly uses textwrap.dedent to eliminate any markdown-induced raw HTML code block leakage.
    """
    theme_borders = {
        "gold": "#D97706",
        "blue": "#2563EB",
        "cyan": "#0284C7",
        "green": "#059669",
        "orange": "#EA580C",
        "red": "#DC2626"
    }
    border_color = theme_borders.get(color_theme, "#D97706")

    delta_html = ""
    if delta:
        if "↓" in delta or "Reduction" in delta or "Saved" in delta or "Satisfied" in delta:
            delta_color = "#059669"
        elif "+" in delta or "↑" in delta or "Improvement" in delta:
            delta_color = "#0284C7"
        else:
            delta_color = "#475569"
            
        delta_html = f'<div style="font-size: 0.85rem; color: {delta_color}; margin-top: 6px; font-weight: 600;">{delta}</div>'

    tooltip_html = ""
    if tooltip_text:
        tooltip_html = f'<span title="{tooltip_text}" style="cursor: help; color: #64748B; font-size: 0.85rem; margin-left: 4px;">ⓘ</span>'

    icon_html = f'<span style="font-size: 1.1rem;">{icon}</span>' if icon else ""

    raw_html = f"""<div style="background-color: #FFFFFF; border-radius: 10px; border: 1px solid #E2E8F0; border-left: 5px solid {border_color}; padding: 18px 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); margin-bottom: 15px;">
<div style="display: flex; justify-content: space-between; align-items: center;">
<span style="color: #64748B; font-size: 0.8rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">{title} {tooltip_html}</span>
{icon_html}
</div>
<div style="font-size: 1.75rem; font-weight: 800; color: #0F172A; margin-top: 6px;">{value}</div>
{delta_html}
</div>"""

    st.markdown(textwrap.dedent(raw_html).strip(), unsafe_allow_html=True)

def render_section_header(title: str, subtitle: str = None, icon: str = ""):
    """Renders a clean formatted section header (Light Enterprise SaaS Theme)."""
    sub_html = f'<div style="color: #64748B; font-size: 0.95rem; margin-top: 4px;">{subtitle}</div>' if subtitle else ""
    icon_span = f'<span style="margin-right: 8px;">{icon}</span>' if icon else ""
    raw_html = f"""<div style="margin-bottom: 24px; padding-bottom: 12px; border-bottom: 1px solid #E2E8F0;">
<h2 style="color: #0F172A; font-weight: 800; margin: 0; font-size: 1.5rem; display: flex; align-items: center;">{icon_span}<span>{title}</span></h2>
{sub_html}
</div>"""
    st.markdown(textwrap.dedent(raw_html).strip(), unsafe_allow_html=True)

def render_badge(label: str, status: str = "pass"):
    """Renders a status badge pill."""
    bg_color = "#DCFCE7" if status == "pass" else "#FEE2E2"
    text_color = "#15803D" if status == "pass" else "#B91C1C"
    symbol = "✓ PASS" if status == "pass" else "✕ FAIL"
    
    return f'<span style="background-color: {bg_color}; color: {text_color}; padding: 4px 10px; border-radius: 20px; font-weight: 700; font-size: 0.8rem;">{label}: {symbol}</span>'
