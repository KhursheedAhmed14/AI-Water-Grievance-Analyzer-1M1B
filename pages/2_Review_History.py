"""
pages/2_Review_History.py
Browse, filter, and inspect past water complaint analyses stored in SQLite.
Provides safe, confirmed record deletion for development and testing.
"""

import json

import pandas as pd
import streamlit as st

from core.database import (
    delete_all_complaints,
    delete_complaint,
    get_all_complaints,
    get_complaint_by_id,
)
from core.response_parser import ALLOWED_CATEGORIES, ALLOWED_PRIORITIES, ALLOWED_SEVERITIES
from core.ui_icons import get_icon_svg
from core.ui_theme import LOGO_PATH, apply_custom_theme, get_status_badge_html

st.set_page_config(
    page_title="Review History - Water Grievance Analyzer",
    page_icon=LOGO_PATH,
    layout="wide",
)

apply_custom_theme()

icon_accent = "#38bdf8"
text_muted = "#94a3b8"

st.markdown(
    f"## {get_icon_svg('history', color=icon_accent, size=24)} Complaint Review History",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='font-size: 1rem; color: var(--text-secondary); margin-bottom: 1.5rem;'>"
    "Browse, filter, and inspect all processed grievances stored in SQLite."
    "</p>",
    unsafe_allow_html=True,
)

# Load data
rows = get_all_complaints()

# Sidebar filter controls
with st.sidebar:
    st.markdown(
        f"### {get_icon_svg('search', color=icon_accent, size=18)} Filter Records",
        unsafe_allow_html=True,
    )

    cat_options = ["All"] + ALLOWED_CATEGORIES
    sel_category = st.selectbox("Category", cat_options, index=0)

    sev_options = ["All"] + ALLOWED_SEVERITIES
    sel_severity = st.selectbox("Severity", sev_options, index=0)

    pri_options = ["All"] + ALLOWED_PRIORITIES
    sel_priority = st.selectbox("Priority", pri_options, index=0)

    search_query = st.text_input("Search Text", placeholder="Location, keyword...", help="Search raw text or location")

    st.caption("Showing newest complaints first.")

    # Database Tools
    st.divider()
    del_color = "#f87171"
    st.markdown(
        f"### {get_icon_svg('trash', color=del_color, size=18)} Database Tools",
        unsafe_allow_html=True,
    )
    with st.expander("Clear Database", expanded=False):
        st.warning("Permanently clears all records and resets Record ID sequence to #1.")
        confirm_all = st.checkbox(
            "I understand this will permanently delete ALL records",
            key="confirm_clear_all",
        )
        if st.button(
            "Clear All Records",
            type="primary",
            disabled=not confirm_all,
            key="btn_clear_all",
            use_container_width=True,
        ):
            deleted_count = delete_all_complaints()
            st.success(f"Cleared {deleted_count} record(s) and reset sequence.")
            st.rerun()

if not rows:
    st.info(
        "No complaints analyzed yet. "
        "Go to **Analyze Complaint** to submit and process your first water grievance."
    )
    st.stop()

df = pd.DataFrame(rows)

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
filtered["summary_short"] = filtered["summary"].str.slice(0, 85) + filtered["summary"].str[85:].apply(
    lambda s: "…" if s else ""
)

display_cols = ["id", "submitted_at", "category", "severity", "priority", "summary_short"]
display_df = filtered[display_cols].rename(
    columns={
        "id": "ID",
        "submitted_at": "Submitted (UTC)",
        "category": "Category",
        "severity": "Severity",
        "priority": "Priority",
        "summary_short": "Summary",
    }
)

st.subheader(f"Complaints Log ({len(filtered)} records)")
st.dataframe(
    display_df,
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

# Detail Card Inspector View
st.divider()
st.markdown(
    f"### {get_icon_svg('file-text', color=icon_accent, size=22)} Record Inspector",
    unsafe_allow_html=True,
)

available_ids = filtered["id"].tolist()
selected_id = st.selectbox(
    "Select Record ID to Inspect",
    options=available_ids,
    format_func=lambda x: f"Record #{x}",
    index=None,
    placeholder="Choose a record ID…",
)

if selected_id is not None:
    record = get_complaint_by_id(selected_id)
    if record is None:
        st.error(f"Record #{selected_id} not found.")
    else:
        st.markdown(
            f"""
            <div class="content-card">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                    <h3 style="margin: 0; color: var(--text-primary);">Record #{selected_id}</h3>
                    <span style="font-size: 0.85rem; color: var(--text-muted);">Submitted: {record.get('submitted_at', '')[:19]} UTC</span>
                </div>
                <div style="margin-bottom: 1rem;">
                    <strong>Status Badges:</strong> &nbsp;
                    {get_status_badge_html(record.get('category', 'Unclear'))} &nbsp;
                    {get_status_badge_html(record.get('severity', 'Unclear'))} &nbsp;
                    {get_status_badge_html(record.get('priority', 'Unclear'))}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("**Original Complaint Text**")
        st.text_area("", value=record.get("raw_text", ""), height=100, disabled=True, key="detail_raw")

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
            f"##### {get_icon_svg('trash', color=del_color, size=16)} Delete Record",
            unsafe_allow_html=True,
        )
        confirm_single = st.checkbox(f"Confirm deletion of Record #{selected_id}", key=f"confirm_del_{selected_id}")
        if st.button(f"Delete Record #{selected_id}", type="primary", disabled=not confirm_single, key=f"btn_del_{selected_id}"):
            if delete_complaint(selected_id):
                st.success(f"Record #{selected_id} deleted successfully.")
                st.rerun()
            else:
                st.error(f"Failed to delete Record #{selected_id}.")
