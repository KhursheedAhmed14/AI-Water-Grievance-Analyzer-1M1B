"""
pages/1_Analyze_Complaint.py
Submit a citizen water complaint for AI-powered analysis using IBM Granite.
"""

import json
from datetime import datetime

import streamlit as st

from config.settings import credentials_configured
from core.auth import get_current_role, require_role
from core.database import get_complaint_by_id, insert_complaint
from core.granite_client import analyze_complaint
from core.response_parser import parse_response
from core.ui_icons import get_icon_svg
from core.ui_theme import get_citizen_status_explanation, get_status_badge_html

# Enforce Citizen authentication session
require_role("citizen")

icon_accent = "#38bdf8"

# ── Page Header ───────────────────────────────────────────────────────────────
st.markdown(
    f"## {get_icon_svg('search', color=icon_accent, size=24)} Submit Water Grievance",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='font-size: 1rem; color: var(--text-secondary); margin-bottom: 1.5rem;'>"
    "Submit your water issue for instant IBM Granite AI analysis and reference ID generation."
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


from core.auth import get_current_user_id, require_role

def _run_analysis(complaint_text: str) -> dict:
    """Call the full pipeline and return the parsed result dict (Preserves AI & DB logic).

    Uses a session-state flag (_submission_in_progress) to guarantee that
    exactly one DB record and one reference ID are created per user submission,
    even if Streamlit reruns the script during the spinner.
    """
    # Guard: if a result is already stored, return it without re-running
    if "analysis_result" in st.session_state:
        return st.session_state["analysis_result"]

    raw_response = analyze_complaint(complaint_text)
    result = parse_response(raw_response)
    result["raw_text"] = complaint_text
    result["raw_llm_response"] = raw_response
    result["submitted_at"] = datetime.utcnow().isoformat()
    # Serialise key_facts list for DB storage
    result["key_facts"] = json.dumps(result.get("key_facts", []))
    citizen_id = get_current_user_id()
    record_id, reference_id = insert_complaint(result, citizen_id=citizen_id)
    # Restore list form for display
    result["key_facts"] = json.loads(result["key_facts"])
    result["record_id"] = record_id
    result["reference_id"] = reference_id
    return result


def _display_results(result: dict) -> None:
    """Render structured AI Analysis Result with strict equal card heights and alignment."""
    st.divider()
    record_id = result.get("record_id")
    reference_id = result.get("reference_id", f"#{record_id if record_id else 'New'}")
    summary_text = result.get("summary", "No summary available.")
    category_text = result.get("category", "Unclear")
    severity_text = result.get("severity", "Medium")
    priority_text = result.get("priority", "Urgent")
    location_text = result.get("location", "Unclear")
    duration_text = result.get("duration", "Unclear")
    affected_text = result.get("affected_people", "Unclear")

    # Fetch live status from result or fallback to DB if needed
    live_status = result.get("status", "Pending")
    if (not live_status or live_status == "Pending") and record_id and isinstance(record_id, int) and "status" not in result:
        live_rec = get_complaint_by_id(record_id)
        if live_rec and live_rec.get("status"):
            live_status = live_rec.get("status")


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

    # ── Professional Success Confirmation Banner ───────────────────────────────
    st.markdown(
        f"""
        <div style="background: rgba(16,185,129,0.10); border: 1.5px solid rgba(16,185,129,0.35);
                    border-radius: 14px; padding: 1.5rem 1.8rem; margin-bottom: 1.4rem;">
            <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 0.9rem;">
                {get_icon_svg('check-circle', color='#34d399', size=28)}
                <h2 style="margin: 0; font-size: 1.35rem; font-weight: 700; color: #34d399;">Complaint Submitted Successfully</h2>
            </div>
            <div style="display: flex; flex-wrap: wrap; gap: 1.2rem; align-items: flex-start; margin-bottom: 1rem;">
                <div>
                    <div style="font-size: 0.75rem; font-weight: 700; text-transform: uppercase;
                                letter-spacing: 0.06em; color: var(--text-muted); margin-bottom: 0.3rem;">Reference ID</div>
                    <div style="font-family: 'Courier New', monospace; font-size: 1.25rem; font-weight: 800;
                                color: #38bdf8; background: rgba(56,189,248,0.10);
                                border: 1px solid rgba(56,189,248,0.3); border-radius: 8px;
                                padding: 0.35rem 0.9rem; letter-spacing: 0.08em; display: inline-block;">
                        {reference_id}
                    </div>
                </div>
                <div style="display: flex; flex-direction: column; gap: 0.35rem; justify-content: flex-end;">
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <span style="font-size: 0.78rem; font-weight: 700; text-transform: uppercase;
                                     letter-spacing: 0.05em; color: var(--text-muted);">Current Status:</span>
                        {get_status_badge_html(live_status)}
                    </div>
                    <div style="font-size: 0.88rem; color: var(--text-secondary); margin-top: 0.1rem;">
                        {get_citizen_status_explanation(live_status)}
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # "View My Complaints" action button — clean label without raw SVG source code
    col_act, _ = st.columns([1, 2])
    with col_act:
        if st.button("View My Complaints", key="btn_view_my_complaints", type="primary", use_container_width=True):
            st.switch_page("pages/2_My_Complaints.py")

    facts_items = "".join([f"<li>{fact}</li>" for fact in key_facts]) if key_facts else "<li>No key facts extracted</li>"
    missing_items = "".join([f"<li>{gap}</li>" for gap in missing_list])

    st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)

    # ── Top Row: 3-Column Grid with Proportional Width Alignment ──────────────
    col1, col2, col3 = st.columns([1.3, 1, 1])

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
    b_col1, b_col2 = st.columns([1, 1.2])

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
    analyze_btn = st.button("Submit Complaint", type="primary", use_container_width=True, key="btn_submit_complaint")
with col_btn2:
    if st.button("Submit Another Complaint", type="secondary", use_container_width=True, key="btn_submit_another"):
        for key in ("analysis_result", "complaint_input"):
            st.session_state.pop(key, None)
        st.rerun()

# ── Trigger Analysis ───────────────────────────────────────────────────────────
if analyze_btn:
    if char_len < 20:
        st.error("Please enter at least 20 characters before submitting.")
    else:
        # Only run analysis+insert if no result is stored yet.
        # This prevents duplicate records on Streamlit reruns or repeated button clicks.
        if "analysis_result" not in st.session_state:
            with st.spinner("Analyzing complaint with IBM Granite on watsonx.ai..."):
                try:
                    result = _run_analysis(complaint_input.strip())
                    st.session_state["analysis_result"] = result
                except RuntimeError as exc:
                    st.error(f"Submission failed: {exc}")

# Display Results
if "analysis_result" in st.session_state:
    _display_results(st.session_state["analysis_result"])
