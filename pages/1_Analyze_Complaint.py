"""
pages/1_Analyze_Complaint.py
Submit a citizen water complaint for AI-powered analysis using IBM Granite.
"""

import json
from datetime import datetime

import streamlit as st

from config.settings import credentials_configured
from core.database import insert_complaint
from core.granite_client import analyze_complaint
from core.response_parser import parse_response
from core.ui_icons import get_icon_svg
from core.ui_theme import LOGO_PATH, apply_custom_theme, get_status_badge_html

st.set_page_config(
    page_title="Analyze Complaint - Water Grievance Analyzer",
    page_icon=LOGO_PATH,
    layout="wide",
)

apply_custom_theme()

icon_accent = "#38bdf8"

# ── Page Header ───────────────────────────────────────────────────────────────
st.markdown(
    f"## {get_icon_svg('search', color=icon_accent, size=24)} Analyze Water Grievance",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='font-size: 1rem; color: var(--text-secondary); margin-bottom: 1.5rem;'>"
    "AI-assisted analysis for faster review and prioritization of citizen water complaints."
    "</p>",
    unsafe_allow_html=True,
)

# ── Credential check ────────────────────────────────────────────────────────
if not credentials_configured():
    st.error(
        "watsonx.ai credentials are not configured. "
        "Please set WATSONX_API_KEY, WATSONX_PROJECT_ID, and WATSONX_URL in .env."
    )
    st.stop()


def _run_analysis(complaint_text: str) -> dict:
    """Call the full pipeline and return the parsed result dict (Preserves AI & DB logic)."""
    raw_response = analyze_complaint(complaint_text)
    result = parse_response(raw_response)
    result["raw_text"] = complaint_text
    result["raw_llm_response"] = raw_response
    result["submitted_at"] = datetime.utcnow().isoformat()
    # Serialise key_facts list for DB storage
    result["key_facts"] = json.dumps(result.get("key_facts", []))
    record_id = insert_complaint(result)
    # Restore list form for display
    result["key_facts"] = json.loads(result["key_facts"])
    result["record_id"] = record_id
    return result


def _display_results(result: dict) -> None:
    """Render structured AI Analysis Result with strict equal card heights and alignment."""
    st.divider()
    summary_text = result.get("summary", "No summary available.")
    category_text = result.get("category", "Unclear")
    severity_text = result.get("severity", "Medium")
    priority_text = result.get("priority", "Urgent")
    location_text = result.get("location", "Unclear")
    duration_text = result.get("duration", "Unclear")
    affected_text = result.get("affected_people", "Unclear")

    key_facts = result.get("key_facts", [])
    if isinstance(key_facts, str):
        try:
            key_facts = json.loads(key_facts)
        except Exception:
            key_facts = [key_facts]

    missing_info = result.get("missing_info", "")
    if isinstance(missing_info, str):
        if missing_info.lower() in ("none identified", "none", "unclear", ""):
            missing_list = ["None identified"]
        else:
            missing_list = [item.strip() for item in missing_info.split(".") if item.strip()]
    elif isinstance(missing_info, list):
        missing_list = missing_info if missing_info else ["None identified"]
    else:
        missing_list = ["None identified"]

    # Header Row with compact green status badge
    badge_bg = "rgba(16, 185, 129, 0.12)"
    badge_border = "rgba(16, 185, 129, 0.3)"
    badge_color = "#34d399"

    st.markdown(
        f"""
        <div style="display: flex; align-items: center; justify-content: space-between; margin-top: 0.5rem; margin-bottom: 1.2rem;">
            <h2 style="font-size: 1.35rem; font-weight: 700; margin: 0;">AI Analysis Result</h2>
            <div style="background: {badge_bg}; border: 1px solid {badge_border}; color: {badge_color}; font-weight: 600; padding: 0.3rem 0.8rem; border-radius: 20px; font-size: 0.82rem; display: inline-flex; align-items: center; gap: 6px;">
                {get_icon_svg('check-circle', color=badge_color, size=14)}
                Analysis Complete
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    facts_items = "".join([f"<li>{fact}</li>" for fact in key_facts]) if key_facts else "<li>No key facts extracted</li>"
    missing_items = "".join([f"<li>{gap}</li>" for gap in missing_list])

    # ── Top Row: Strict 3-Column Grid with Equal Height Alignment ──────────────
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            f"""
            <div class="result-card">
                <div class="card-header-row">
                    <div class="card-icon-box">
                        {get_icon_svg("file-text", color=icon_accent, size=16)}
                    </div>
                    <span class="card-header-title">Summary</span>
                </div>
                <p class="card-body-text">
                    {summary_text}
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            f"""
            <div class="result-card">
                <div class="card-header-row">
                    <div class="card-icon-box">
                        {get_icon_svg("layer", color=icon_accent, size=16)}
                    </div>
                    <span class="card-header-title">Category & Severity</span>
                </div>
                <div style="display: flex; flex-direction: column; gap: 12px; margin-top: 0.2rem;">
                    <div>
                        <div style="font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.04em; color: var(--text-muted); margin-bottom: 0.2rem;">Category</div>
                        <div class="card-body-value">{category_text}</div>
                    </div>
                    <div>
                        <div style="font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.04em; color: var(--text-muted); margin-bottom: 0.25rem;">Severity</div>
                        <div>{get_status_badge_html(severity_text)}</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            f"""
            <div class="result-card">
                <div class="card-header-row">
                    <div class="card-icon-box">
                        {get_icon_svg("alert-triangle", color=icon_accent, size=16)}
                    </div>
                    <span class="card-header-title">AI Priority Recommendation</span>
                </div>
                <div style="flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; gap: 8px;">
                    <div>
                        {get_status_badge_html(priority_text)}
                    </div>
                    <div style="font-size: 0.78rem; color: var(--text-muted);">
                        For municipal review
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)

    # ── Second Row: Clean 2-Column Grid with Equal Height Alignment ───────────
    b_col1, b_col2 = st.columns(2)

    with b_col1:
        st.markdown(
            f"""
            <div class="result-card">
                <div class="card-header-row">
                    <div class="card-icon-box">
                        {get_icon_svg("target", color=icon_accent, size=16)}
                    </div>
                    <span class="card-header-title">Extracted Details</span>
                </div>
                <div class="detail-list" style="margin-top: 0.5rem;">
                    <div class="detail-row">
                        {get_icon_svg("map-pin", color=icon_accent, size=18)}
                        <div><strong style="color: var(--text-primary);">Location:</strong> <span style="color: var(--text-secondary);">{location_text}</span></div>
                    </div>
                    <div class="detail-row">
                        {get_icon_svg("clock", color=icon_accent, size=18)}
                        <div><strong style="color: var(--text-primary);">Duration:</strong> <span style="color: var(--text-secondary);">{duration_text}</span></div>
                    </div>
                    <div class="detail-row">
                        {get_icon_svg("users", color=icon_accent, size=18)}
                        <div><strong style="color: var(--text-primary);">Affected People:</strong> <span style="color: var(--text-secondary);">{affected_text}</span></div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with b_col2:
        st.markdown(
            f"""
            <div class="result-card">
                <div class="card-header-row">
                    <div class="card-icon-box">
                        {get_icon_svg("sparkles", color=icon_accent, size=16)}
                    </div>
                    <span class="card-header-title">Key Facts & Gaps</span>
                </div>
                <div style="margin-top: 0.5rem; display: flex; flex-direction: column; gap: 0.6rem;">
                    <div>
                        <div style="font-weight: 700; color: var(--text-primary); font-size: 0.88rem; margin-bottom: 0.25rem;">Key Facts</div>
                        <ul class="result-bullets">
                            {facts_items}
                        </ul>
                    </div>
                    <div style="border-top: 1px solid var(--border-color); padding-top: 0.6rem;">
                        <div style="font-weight: 700; color: var(--text-primary); font-size: 0.88rem; margin-bottom: 0.25rem;">Missing Information</div>
                        <ul class="result-bullets">
                            {missing_items}
                        </ul>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ── Human Oversight Disclaimer ──────────────────────────────────────────────
    st.markdown(
        f"""
        <div class="disclaimer-box">
            {get_icon_svg("shield-check", color=icon_accent, size=16)}
            <span>AI recommendation for municipal review. Final decisions remain with qualified authorities.</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ── Complaint Input Form ───────────────────────────────────────────────────────
st.markdown(
    """
    <div class="content-card">
        <h3 style="font-size: 1.1rem; margin-bottom: 0.3rem;">Submit a Water Complaint</h3>
        <p style="font-size: 0.88rem; color: var(--text-muted); margin-bottom: 0.8rem;">
            Describe the water-related issue in natural language. Include location, duration, and affected people when available.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

PLACEHOLDER = (
    "Example: There is a large water leak on the corner of Park Avenue and "
    "5th Street. Water has been gushing from the ground since yesterday morning. "
    "The road is flooded and several houses in the area have had no water supply "
    "for over 24 hours. Approximately 30 households are affected."
)

complaint_input = st.text_area(
    "Citizen Complaint Text",
    placeholder=PLACEHOLDER,
    height=160,
    key="complaint_input",
    help="Enter the citizen's complaint in plain text. Minimum 20 characters.",
    label_visibility="collapsed",
)

# Character Counter Caption
char_len = len(complaint_input.strip()) if complaint_input else 0
st.caption(f"Character count: **{char_len}** characters (minimum 20 required)")

col_btn1, col_btn2 = st.columns([2, 1])
with col_btn1:
    analyze_btn = st.button("Analyze Complaint", type="primary", use_container_width=True)
with col_btn2:
    if st.button("Analyze Another Complaint", type="secondary", use_container_width=True):
        for key in ("analysis_result", "complaint_input"):
            st.session_state.pop(key, None)
        st.rerun()

# ── Trigger Analysis ───────────────────────────────────────────────────────────
if analyze_btn:
    if char_len < 20:
        st.error("Please enter at least 20 characters before analyzing.")
    else:
        if "analysis_result" not in st.session_state:
            with st.spinner("Analyzing complaint with IBM Granite on watsonx.ai..."):
                try:
                    st.session_state["analysis_result"] = _run_analysis(complaint_input.strip())
                except RuntimeError as exc:
                    st.error(f"Analysis failed: {exc}")

# Display Results
if "analysis_result" in st.session_state:
    _display_results(st.session_state["analysis_result"])
