"""
pages/2_Review_History.py
Browse, filter, and inspect past water complaint analyses stored in SQLite.
Provides safe, confirmed record deletion for development and testing.
"""

import json

import pandas as pd
import streamlit as st

from core.auth import get_current_role, get_current_user_id, require_role
from core.database import (
    delete_complaint,
    get_complaint_by_id,
    get_complaints_by_citizen,
)
from core.response_parser import ALLOWED_CATEGORIES, ALLOWED_PRIORITIES, ALLOWED_SEVERITIES
from core.ui_icons import get_icon_svg
from core.ui_theme import get_citizen_status_explanation, get_status_badge_html

# Enforce Citizen authentication session
require_role("citizen")

del_color = "#f87171"
icon_accent = "#38bdf8"
text_muted = "#94a3b8"

# ── Page Header ───────────────────────────────────────────────────────────────
st.markdown(
    f"## {get_icon_svg('history', color=icon_accent, size=24)} My Complaints & Status Tracking",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='font-size: 1rem; color: var(--text-secondary); margin-bottom: 1.2rem;'>"
    "Track the resolution status, AI analysis, and details of your submitted water grievances."
    "</p>",
    unsafe_allow_html=True,
)

# Load data owned by authenticated citizen
citizen_id = get_current_user_id()
rows = get_complaints_by_citizen(citizen_id)

if not rows:
    st.info(
        "No complaints submitted yet. "
        "Go to **Submit Complaint** to report a water grievance."
    )
    st.stop()

df = pd.DataFrame(rows)

# ── Main Content Filter Controls (Moved out of Sidebar) ─────────────────────
st.markdown(
    f"### {get_icon_svg('filter', color=icon_accent, size=18)} Filter Records",
    unsafe_allow_html=True,
)

f_col1, f_col2, f_col3 = st.columns(3)

with f_col1:
    cat_options = ["All"] + ALLOWED_CATEGORIES
    sel_category = st.selectbox("Category", cat_options, index=0, key="citizen_filter_category")

with f_col2:
    sev_options = ["All"] + ALLOWED_SEVERITIES
    sel_severity = st.selectbox("Severity", sev_options, index=0, key="citizen_filter_severity")

with f_col3:
    pri_options = ["All"] + ALLOWED_PRIORITIES
    sel_priority = st.selectbox("AI Recommendation", pri_options, index=0, key="citizen_filter_priority")

search_query = st.text_input(
    "Search Text",
    placeholder="Location, keyword...",
    help="Search raw text or location",
    key="citizen_filter_search",
)

st.markdown("<div style='margin-bottom: 1.2rem;'></div>", unsafe_allow_html=True)

# Filter logic
filtered = df.copy()
if sel_category != "All":
    filtered = filtered[filtered["category"] == sel_category]
if sel_severity != "All":
    filtered = filtered[filtered["severity"] == sel_severity]
if sel_priority != "All":
    filtered = filtered[filtered["priority"] == sel_priority]
if search_query.strip():
    q = search_query.strip().lower()
    filtered = filtered[
        filtered["raw_text"].fillna("").str.lower().str.contains(q)
        | filtered["summary"].fillna("").str.lower().str.contains(q)
        | filtered["location"].fillna("").str.lower().str.contains(q)
    ]

# Summary Metrics Cards
m1, m2, m3, m4 = st.columns(4)
with m1:
    st.markdown(
        f"""
        <div class="saas-metric-card">
            <div class="saas-metric-title">{get_icon_svg("file-text", color=text_muted, size=14)} Total Complaints</div>
            <div class="saas-metric-value">{len(df)}</div>
            <div class="saas-metric-sub">{len(filtered)} matching filter</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with m2:
    high_urg_count = len(df[df["priority"].isin(["High", "Urgent"]) | df["severity"].isin(["High", "Urgent"])])
    sev_color = "#fb923c"
    st.markdown(
        f"""
        <div class="saas-metric-card">
            <div class="saas-metric-title">{get_icon_svg("alert-triangle", color=sev_color, size=14)} High/Urgent Complaints</div>
            <div class="saas-metric-value" style="color: {sev_color} !important;">{high_urg_count}</div>
            <div class="saas-metric-sub">Critical priority rating</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with m3:
    water_supply_count = len(df[df["category"] == "Water Supply Disruption"])
    st.markdown(
        f"""
        <div class="saas-metric-card">
            <div class="saas-metric-title">{get_icon_svg("water", color=icon_accent, size=14)} Water Supply Issues</div>
            <div class="saas-metric-value">{water_supply_count}</div>
            <div class="saas-metric-sub">Outages & supply failures</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with m4:
    other_count = len(df[df["category"].isin(["Other / Unclear", "Unclear"])])
    st.markdown(
        f"""
        <div class="saas-metric-card">
            <div class="saas-metric-title">{get_icon_svg("info", color=text_muted, size=14)} Other / Unclear</div>
            <div class="saas-metric-value">{other_count}</div>
            <div class="saas-metric-sub">Non-water or vague</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)

if filtered.empty:
    st.warning("No complaints analyzed yet matching the selected filters.")
    st.stop()

# Table Display
filtered["summary_short"] = filtered["summary"].fillna("").str.slice(0, 85) + filtered["summary"].fillna("").str[85:].apply(
    lambda s: "\u2026" if s else ""
)

# Format reference_id safely for dropdown mapping and summary table display
ref_id_map: dict[int, str] = {}
for _, row in filtered.iterrows():
    rid = row.get("reference_id")
    ref_str = str(rid).strip() if pd.notna(rid) and str(rid).strip() else "Reference ID unavailable"
    ref_id_map[int(row["id"])] = ref_str

filtered["reference_id_display"] = filtered["id"].map(ref_id_map)

display_cols = ["reference_id_display", "submitted_at", "status", "category", "severity", "priority", "summary_short"]
col_rename = {
    "reference_id_display": "Reference ID",
    "submitted_at": "Submitted (UTC)",
    "status": "Status",
    "category": "Category",
    "severity": "Severity",
    "priority": "AI Recommendation",
    "summary_short": "Summary",
}
display_df = filtered[display_cols].rename(columns=col_rename)

st.subheader(f"Complaints Log ({len(filtered)} records)")
st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Reference ID": st.column_config.TextColumn(width="medium"),
        "Submitted (UTC)": st.column_config.TextColumn(width="medium"),
        "Status": st.column_config.TextColumn(width="small"),
        "Category": st.column_config.TextColumn(width="medium"),
        "Severity": st.column_config.TextColumn(width="small"),
        "AI Recommendation": st.column_config.TextColumn(width="small"),
        "Summary": st.column_config.TextColumn(width="large"),
    },
)

# Detail Card Inspector View
st.divider()
st.markdown(
    f"### {get_icon_svg('file-text', color=icon_accent, size=22)} Record Inspector",
    unsafe_allow_html=True,
)

available_ids = filtered["id"].tolist()
selected_id = st.selectbox(
    "Select Complaint to Inspect",
    options=available_ids,
    format_func=lambda x: ref_id_map.get(x, "Reference ID unavailable"),
    index=None,
    placeholder="Choose a complaint…",
    key="citizen_select_record_id",
)

if selected_id is not None:
    record = next((r for r in rows if r.get("id") == selected_id), None)
    if record is None:
        record = get_complaint_by_id(selected_id)

    if record is None or record.get("citizen_id") != citizen_id:
        st.error("Complaint record not found or access denied.")
    else:
        submitted_str = str(record.get("submitted_at", ""))[:19].replace("T", " ")
        ref_id_val = record.get("reference_id")
        ref_id_display = str(ref_id_val).strip() if ref_id_val and str(ref_id_val).strip() else "Reference ID unavailable"
        status_val = record.get("status", "Pending")
        status_explanation = get_citizen_status_explanation(status_val)

        st.markdown(
            f"""
            <div class="content-card">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; flex-wrap: wrap; gap: 0.5rem;">
                    <div>
                        <span style="font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-muted);">Reference ID</span>
                        <h3 style="margin: 0; color: var(--text-primary); font-family: monospace; font-size: 1.3rem;">{ref_id_display}</h3>
                    </div>
                    <div style="text-align: right;">
                        <span style="font-size: 0.78rem; color: var(--text-muted);">Submitted</span>
                        <div style="font-size: 0.9rem; color: var(--text-secondary);">{submitted_str} UTC</div>
                    </div>
                </div>
                <div style="background: rgba(56, 189, 248, 0.06); border: 1px solid rgba(56, 189, 248, 0.2); border-radius: 10px; padding: 1rem; margin-bottom: 1.2rem;">
                    <div style="display: flex; align-items: center; gap: 0.8rem; margin-bottom: 0.45rem; flex-wrap: wrap;">
                        <strong style="color: var(--text-primary); font-size: 0.95rem;">Current Status:</strong>
                        {get_status_badge_html(status_val)}
                    </div>
                    <div style="font-size: 0.9rem; color: var(--text-secondary);">
                        {status_explanation}
                    </div>
                </div>
                <div style="display: flex; align-items: center; gap: 1rem; flex-wrap: wrap;">
                    <div>
                        <span style="color: var(--text-muted); font-size: 0.85rem;">Category:</span> &nbsp;
                        {get_status_badge_html(record.get('category', 'Unclear'))}
                    </div>
                    <div>
                        <span style="color: var(--text-muted); font-size: 0.85rem;">Severity:</span> &nbsp;
                        {get_status_badge_html(record.get('severity', 'Unclear'))}
                    </div>
                    <div>
                        <span style="color: var(--text-muted); font-size: 0.85rem;">AI Recommendation:</span> &nbsp;
                        {get_status_badge_html(record.get('priority', 'Unclear'))}
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("**Original Complaint Text**")
        raw_text_val = record.get("raw_text", "")
        st.info(raw_text_val if raw_text_val else "No complaint text provided.")

        st.markdown("**Executive Summary**")
        st.info(record.get("summary", "—"))

        det1, det2, det3 = st.columns(3)
        det1.metric("Location", record.get("location", "Unclear"))
        det2.metric("Duration", record.get("duration", "Unclear"))
        det3.metric("Affected People", record.get("affected_people", "Unclear"))

        raw_facts = record.get("key_facts", "[]")
        try:
            facts_list = json.loads(raw_facts) if isinstance(raw_facts, str) else raw_facts
        except (json.JSONDecodeError, TypeError):
            facts_list = []

        if facts_list:
            st.markdown("**Key Facts**")
            for fact in facts_list:
                st.markdown(f"- {fact}")

        missing = record.get("missing_info", "None identified")
        if missing and missing.lower() not in ("none identified", "none"):
            missing_bg = "rgba(249, 115, 22, 0.12)"
            missing_border = "rgba(249, 115, 22, 0.3)"
            missing_color = "#fb923c"
            st.markdown(
                f"<div style='background: {missing_bg}; border: 1px solid {missing_border}; border-radius: 8px; padding: 0.8rem 1rem; color: {missing_color}; font-size: 0.9rem; margin-top: 1rem;'>"
                f"{get_icon_svg('alert-triangle', color=missing_color, size=16)} "
                f"<strong>Missing Info:</strong> {missing}</div>",
                unsafe_allow_html=True,
            )
        else:
            ok_bg = "rgba(16, 185, 129, 0.12)"
            ok_border = "rgba(16, 185, 129, 0.3)"
            ok_color = "#34d399"
            st.markdown(
                f"<div style='background: {ok_bg}; border: 1px solid {ok_border}; border-radius: 8px; padding: 0.8rem 1rem; color: {ok_color}; font-size: 0.9rem; margin-top: 1rem;'>"
                f"{get_icon_svg('check-circle', color=ok_color, size=16)} "
                f"<strong>Missing Info:</strong> None identified.</div>",
                unsafe_allow_html=True,
            )

        # Single Record Delete Option
        st.divider()
        st.markdown(
            f"##### {get_icon_svg('trash', color=del_color, size=16)} Delete Complaint",
            unsafe_allow_html=True,
        )
        confirm_single = st.checkbox(f"Confirm deletion of complaint {ref_id_display}", key=f"confirm_del_{selected_id}")
        if st.button(f"Delete Complaint {ref_id_display}", type="primary", disabled=not confirm_single, key=f"btn_del_{selected_id}"):
            if delete_complaint(selected_id):
                st.success(f"Complaint {ref_id_display} deleted successfully.")
                st.rerun()
            else:
                st.error(f"Failed to delete complaint {ref_id_display}.")

