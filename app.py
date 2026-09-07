"""
app.py
Streamlit entry point and SaaS Dashboard for the AI-Powered Water Grievance Analyzer.
"""

import pandas as pd
import streamlit as st

from config.settings import credentials_configured
from core.database import get_all_complaints, init_db
from core.ui_icons import get_icon_svg
from core.ui_theme import LOGO_PATH, apply_custom_theme

# Page configuration
st.set_page_config(
    page_title="Dashboard - Water Grievance Analyzer",
    page_icon=LOGO_PATH,
    layout="wide",
)

# Apply global UI design theme
apply_custom_theme()

# Init database
init_db()

icon_accent = "#38bdf8"
text_muted = "#94a3b8"

# ── Hero Banner ───────────────────────────────────────────────────────────────
st.markdown(
    f"""
    <div class="hero-banner">
        <span class="sdg-tag">{get_icon_svg("water", color="#ffffff", size=14)} UN SDG 6: Clean Water & Sanitation</span>
        <h1>AI-Powered Water Grievance Analyzer</h1>
        <p>AI-assisted analysis and prioritization of citizen water complaints. Designed for municipal decision support leveraging IBM Granite on watsonx.ai.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Credentials Status Notice ──────────────────────────────────────────────────
if not credentials_configured():
    st.error(
        "IBM watsonx.ai credentials are not configured. "
        "Set WATSONX_API_KEY, WATSONX_PROJECT_ID, and WATSONX_URL in .env.",
    )
else:
    status_bg = "rgba(16, 185, 129, 0.12)"
    status_border = "rgba(16, 185, 129, 0.3)"
    status_text = "#34d399"
    st.markdown(
        f"<div style='font-size: 0.85rem; background: {status_bg}; border: 1px solid {status_border}; color: {status_text}; padding: 0.5rem 0.9rem; border-radius: 8px; margin-bottom: 1.5rem; display: flex; align-items: center; gap: 8px;'>"
        f"{get_icon_svg('check-circle', color=status_text, size=16)} "
        f"<strong>System Status:</strong> IBM watsonx.ai API & SQLite Database Connected</div>",
        unsafe_allow_html=True,
    )

# ── Dashboard Overview Metrics ─────────────────────────────────────────────────
complaints = get_all_complaints()
total_count = len(complaints)
high_sev_count = sum(1 for c in complaints if c.get("severity") == "High")
urgent_pri_count = sum(1 for c in complaints if c.get("priority") == "Urgent")

if total_count > 0:
    df_temp = pd.DataFrame(complaints)
    most_common_cat = df_temp["category"].value_counts().idxmax()
else:
    most_common_cat = "None Yet"

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(
        f"""
        <div class="saas-metric-card">
            <div class="saas-metric-title">{get_icon_svg("file-text", color=text_muted, size=14)} Total Complaints</div>
            <div class="saas-metric-value">{total_count}</div>
            <div class="saas-metric-sub">Logged in database</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with col2:
    sev_color = "#fb923c"
    st.markdown(
        f"""
        <div class="saas-metric-card">
            <div class="saas-metric-title">{get_icon_svg("alert-triangle", color=sev_color, size=14)} High Severity</div>
            <div class="saas-metric-value" style="color: {sev_color} !important;">{high_sev_count}</div>
            <div class="saas-metric-sub">Critical infrastructure issues</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with col3:
    urg_color = "#f87171"
    st.markdown(
        f"""
        <div class="saas-metric-card">
            <div class="saas-metric-title">{get_icon_svg("shield-check", color=urg_color, size=14)} Urgent Priority</div>
            <div class="saas-metric-value" style="color: {urg_color} !important;">{urgent_pri_count}</div>
            <div class="saas-metric-sub">Requires immediate triage</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with col4:
    st.markdown(
        f"""
        <div class="saas-metric-card">
            <div class="saas-metric-title">{get_icon_svg("target", color=icon_accent, size=14)} Primary Issue Type</div>
            <div class="saas-metric-value" style="font-size: 1.15rem; font-weight: 600;">{most_common_cat}</div>
            <div class="saas-metric-sub">Most frequent category</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)

# ── Call-To-Action Banner & Quick Navigation ───────────────────────────────────
cta_col1, cta_col2 = st.columns([3, 1])
with cta_col1:
    st.markdown(
        f"### {get_icon_svg('search', color=icon_accent, size=20)} Analyze a Water Grievance",
        unsafe_allow_html=True,
    )
    st.markdown(
        "Submit unstructured citizen feedback for instant AI classification, "
        "severity assessment, location extraction, and priority recommendation."
    )
with cta_col2:
    st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
    if st.button("Analyze Complaint", type="primary", use_container_width=True):
        st.switch_page("pages/1_Analyze_Complaint.py")

st.divider()

# ── How It Works Section ───────────────────────────────────────────────────────
st.markdown(
    f"### {get_icon_svg('cpu', color=icon_accent, size=20)} How It Works",
    unsafe_allow_html=True,
)

st.markdown(
    f"""
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 1rem; margin-bottom: 1.5rem;">
        <div class="content-card">
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 0.5rem;">
                <div class="card-icon-box">{get_icon_svg("file-text", color=icon_accent, size=16)}</div>
                <h4 style="margin: 0; font-size: 0.95rem;">1. Submit Complaint</h4>
            </div>
            <p style="font-size: 0.85rem; color: var(--text-secondary); margin: 0;">Citizens submit unstructured water grievances in natural language.</p>
        </div>
        <div class="content-card">
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 0.5rem;">
                <div class="card-icon-box">{get_icon_svg("sparkles", color=icon_accent, size=16)}</div>
                <h4 style="margin: 0; font-size: 0.95rem;">2. AI Analysis</h4>
            </div>
            <p style="font-size: 0.85rem; color: var(--text-secondary); margin: 0;">IBM Granite model categorizes, extracts details, and evaluates severity.</p>
        </div>
        <div class="content-card">
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 0.5rem;">
                <div class="card-icon-box">{get_icon_svg("target", color=icon_accent, size=16)}</div>
                <h4 style="margin: 0; font-size: 0.95rem;">3. Structured Results</h4>
            </div>
            <p style="font-size: 0.85rem; color: var(--text-secondary); margin: 0;">Instant structured dashboard display of location, duration, and priority.</p>
        </div>
        <div class="content-card">
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 0.5rem;">
                <div class="card-icon-box">{get_icon_svg("shield-check", color=icon_accent, size=16)}</div>
                <h4 style="margin: 0; font-size: 0.95rem;">4. Human Review</h4>
            </div>
            <p style="font-size: 0.85rem; color: var(--text-secondary); margin: 0;">Municipal officers review advisory AI recommendations for dispatch.</p>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Responsible AI Statement Banner ───────────────────────────────────────────
st.markdown(
    f"""
    <div class="disclaimer-box">
        {get_icon_svg("shield-check", color=icon_accent, size=16)}
        <span><strong>Responsible AI Notice:</strong> AI recommendations support human review and do not replace municipal decisions.</span>
    </div>
    """,
    unsafe_allow_html=True,
)

st.divider()

# ── Recent Complaints Overview ─────────────────────────────────────────────────
st.markdown(
    f"### {get_icon_svg('clock', color=icon_accent, size=20)} Recent Complaint Activity",
    unsafe_allow_html=True,
)

if not complaints:
    st.info(
        "No complaints logged yet. Click **Analyze Complaint** above to process your first grievance."
    )
else:
    recent_df = pd.DataFrame(complaints[:5])
    recent_df["summary_short"] = recent_df["summary"].str.slice(0, 85) + recent_df["summary"].str[85:].apply(
        lambda s: "…" if s else ""
    )

    display_recent = recent_df[["id", "submitted_at", "category", "severity", "priority", "summary_short"]].rename(
        columns={
            "id": "ID",
            "submitted_at": "Submitted (UTC)",
            "category": "Category",
            "severity": "Severity",
            "priority": "Priority",
            "summary_short": "Summary",
        }
    )

    st.dataframe(
        display_recent,
        use_container_width=True,
        hide_index=True,
        column_config={
            "ID": st.column_config.NumberColumn(width="small"),
            "Submitted (UTC)": st.column_config.TextColumn(width="medium"),
            "Category": st.column_config.TextColumn(width="medium"),
            "Severity": st.column_config.TextColumn(width="small"),
            "Priority": st.column_config.TextColumn(width="small"),
            "Summary": st.column_config.TextColumn(width="large"),
        },
    )

    if st.button("View Full Review History", use_container_width=False):
        st.switch_page("pages/2_Review_History.py")
