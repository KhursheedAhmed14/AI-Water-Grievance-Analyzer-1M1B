import json
from datetime import datetime
import pandas as pd
import streamlit as st

from core.auth import get_authenticated_user, logout, require_role
from core.database import (
    get_all_complaints,
    get_complaint_by_id,
    update_complaint_workflow,
)
from core.ui_icons import get_icon_svg
from core.ui_theme import get_status_badge_html

# Enforce Municipal Officer authentication session
require_role("municipal")

icon_accent = "#38bdf8"
text_muted = "#94a3b8"
current_user = get_authenticated_user()


# ============================================================
# HEADER
# ============================================================

st.markdown(
    f"""
    <div style="display:flex; align-items:center; gap:10px; margin-bottom:0.25rem;">
        {get_icon_svg("building", color=icon_accent, size=25)}
        <h2 style="margin:0;">Municipal Dashboard</h2>
    </div>
    """,
    unsafe_allow_html=True,
)
st.markdown(
    f"""
    <p style="font-size:1rem; color:var(--text-secondary); margin-bottom:1.5rem;">
        Monitor, prioritize, and manage AI-analyzed water grievances. Logged in as <strong>{current_user}</strong>.
    </p>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# LOAD COMPLAINTS & SAFE DEFAULTS
# ============================================================

rows = get_all_complaints()

if rows:
    df = pd.DataFrame(rows)
else:
    df = pd.DataFrame(
        columns=[
            "id",
            "reference_id",
            "category",
            "severity",
            "priority",
            "municipal_priority",
            "status",
            "assigned_team",
            "review_notes",
            "raw_text",
            "summary",
            "location",
            "duration",
            "affected_people",
            "key_facts",
            "missing_info",
            "submitted_at",
            "resolved_at",
            "citizen_id",
        ]
    )

# Safe defaults for required fields
if "status" not in df.columns:
    df["status"] = "Pending"

if "assigned_team" not in df.columns:
    df["assigned_team"] = "Unassigned"

if "municipal_priority" not in df.columns:
    df["municipal_priority"] = None

if "review_notes" not in df.columns:
    df["review_notes"] = ""

if "priority" not in df.columns:
    df["priority"] = "Unclear"

if "category" not in df.columns:
    df["category"] = "Unclear"

if "reference_id" not in df.columns:
    df["reference_id"] = None
df["reference_id"] = df["reference_id"].fillna("Reference ID unavailable")

df["status"] = df["status"].fillna("Pending")
df["assigned_team"] = df["assigned_team"].fillna("Unassigned")


# ============================================================
# TOP-LEVEL WORKLOAD METRICS (UNFILTERED)
# ============================================================

total_count = len(df)
high_urgent_count = len(df[df["priority"].isin(["High", "Urgent"])]) if not df.empty else 0
pending_count = len(df[df["status"] == "Pending"]) if not df.empty else 0
resolved_count = len(df[df["status"] == "Resolved"]) if not df.empty else 0


m1, m2, m3, m4 = st.columns(4)

with m1:
    st.markdown(
        f"""
        <div class="saas-metric-card">
            <div class="saas-metric-title">
                {get_icon_svg("file-text", color=text_muted, size=14)}
                Total Complaints
            </div>
            <div class="saas-metric-value">{total_count}</div>
            <div class="saas-metric-sub">All analyzed grievances</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with m2:
    st.markdown(
        f"""
        <div class="saas-metric-card">
            <div class="saas-metric-title">
                {get_icon_svg("alert-triangle", color="#fb923c", size=14)}
                High / Urgent
            </div>
            <div class="saas-metric-value" style="color:#fb923c !important;">
                {high_urgent_count}
            </div>
            <div class="saas-metric-sub">AI recommended High/Urgent</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with m3:
    st.markdown(
        f"""
        <div class="saas-metric-card">
            <div class="saas-metric-title">
                {get_icon_svg("clock", color=icon_accent, size=14)}
                Pending
            </div>
            <div class="saas-metric-value">{pending_count}</div>
            <div class="saas-metric-sub">Awaiting municipal action</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with m4:
    st.markdown(
        f"""
        <div class="saas-metric-card">
            <div class="saas-metric-title">
                {get_icon_svg("check-circle", color="#34d399", size=14)}
                Resolved
            </div>
            <div class="saas-metric-value" style="color:#34d399 !important;">
                {resolved_count}
            </div>
            <div class="saas-metric-sub">Marked as resolved</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)


# ============================================================
# FILTERS
# ============================================================

st.markdown(
    f"""
    <div style="display:flex; align-items:center; gap:8px; margin-bottom:0.8rem;">
        {get_icon_svg("filter", color=icon_accent, size=18)}
        <h3 style="margin:0;">Municipal Complaint Queue</h3>
    </div>
    """,
    unsafe_allow_html=True,
)

f1, f2, f3, f4 = st.columns(4)

with f1:
    priority_options = ["All", "Urgent", "High", "Medium", "Low"]
    selected_priority = st.selectbox("AI Recommendation", priority_options, key="muni_filter_priority")

with f2:
    status_options = ["All", "Pending", "Assigned", "In Progress", "Resolved"]
    selected_status = st.selectbox("Status", status_options, key="muni_filter_status")

with f3:
    category_options = ["All"] + sorted(df["category"].dropna().unique().tolist())
    selected_category = st.selectbox("Category", category_options, key="muni_filter_category")

with f4:
    muni_pri_filter_opts = ["All", "Not Set", "Low", "Medium", "High", "Urgent"]
    selected_muni_pri = st.selectbox("Municipal Priority", muni_pri_filter_opts, key="muni_filter_muni_pri")


# ============================================================
# APPLY FILTERS & QUEUE SORTING
# ============================================================

filtered = df.copy()

if selected_priority != "All":
    filtered = filtered[filtered["priority"] == selected_priority]

if selected_status != "All":
    filtered = filtered[filtered["status"] == selected_status]

if selected_category != "All":
    filtered = filtered[filtered["category"] == selected_category]

if selected_muni_pri != "All":
    if selected_muni_pri == "Not Set":
        filtered = filtered[filtered["municipal_priority"].isna() | (filtered["municipal_priority"] == "Not Set") | (filtered["municipal_priority"] == "")]
    else:
        filtered = filtered[filtered["municipal_priority"] == selected_muni_pri]

# Priority sorting: AI Recommendation order -> Status order -> Newest first
priority_order = {"Urgent": 0, "High": 1, "Medium": 2, "Low": 3}
status_order = {"Pending": 0, "Assigned": 1, "In Progress": 2, "Resolved": 3}

filtered["_priority_order"] = filtered["priority"].map(priority_order).fillna(99)
filtered["_status_order"] = filtered["status"].map(status_order).fillna(99)
filtered = filtered.sort_values(by=["_priority_order", "_status_order", "id"], ascending=[True, True, False])


# ============================================================
# QUEUE TABLE
# ============================================================

st.caption(f"Showing {len(filtered)} of {len(df)} complaints.")

if filtered.empty:
    st.warning("No complaints match the selected filters.")
else:
    # Use reference_id as the visible first column; internal id stays in df for selection.
    # municipal_priority NULL is displayed as "Not Set" here (display-only copy).
    display_cols = [
        "reference_id",
        "category",
        "severity",
        "priority",
        "municipal_priority",
        "status",
        "assigned_team",
        "location",
    ]

    display_df = filtered[display_cols].copy()
    display_df["municipal_priority"] = display_df["municipal_priority"].fillna("Not Set")
    display_df = display_df.rename(
        columns={
            "reference_id": "Reference ID",
            "category": "Category",
            "severity": "Severity",
            "priority": "AI Recommendation",
            "municipal_priority": "Municipal Priority",
            "status": "Status",
            "assigned_team": "Assigned Team",
            "location": "Location",
        }
    )

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Reference ID": st.column_config.TextColumn(width="medium"),
            "Category": st.column_config.TextColumn(width="medium"),
            "Severity": st.column_config.TextColumn(width="small"),
            "AI Recommendation": st.column_config.TextColumn(width="small"),
            "Municipal Priority": st.column_config.TextColumn(width="small"),
            "Status": st.column_config.TextColumn(width="medium"),
            "Assigned Team": st.column_config.TextColumn(width="medium"),
            "Location": st.column_config.TextColumn(width="medium"),
        },
    )


# ============================================================
# COMPLAINT REVIEW & OPERATIONS INTERFACE
# ============================================================

st.markdown("<br>", unsafe_allow_html=True)
st.markdown(
    f"""
    <div style="display:flex; align-items:center; gap:8px; margin-bottom:0.8rem;">
        {get_icon_svg("shield-check", color=icon_accent, size=20)}
        <h3 style="margin:0;">Complaint Details & Municipal Review</h3>
    </div>
    """,
    unsafe_allow_html=True,
)

# Build a reference_id lookup by id for the selectbox label
ref_id_map_muni: dict[int, str] = {
    int(row["id"]): str(row["reference_id"])
    for _, row in df[["id", "reference_id"]].iterrows()
}

available_ids = filtered["id"].tolist() if not filtered.empty else df["id"].tolist()
selected_id = st.selectbox(
    "Select Complaint to Review & Action",
    options=available_ids,
    format_func=lambda x: ref_id_map_muni.get(x, f"WGA-#{x}"),
    key="muni_select_complaint_id",
    placeholder="Choose a complaint to review…",
    index=None,
)

if selected_id is not None:
    rec = next((r for r in rows if r.get("id") == selected_id), None)
    if rec is None:
        rec = get_complaint_by_id(selected_id)

    if rec:
        submitted_str = str(rec.get("submitted_at", ""))[:19].replace("T", " ")
        ref_display = rec.get("reference_id") or "Reference ID unavailable"
        current_status = rec.get("status") or "Pending"

        # ── Compact Context Line Header at top of review area ───────────────
        st.markdown(
            f"""
            <div style="display: flex; justify-content: space-between; align-items: center; background: var(--bg-card-subtle); border: 1px solid var(--border-color); border-radius: 10px; padding: 0.9rem 1.2rem; margin-bottom: 1.2rem;">
                <div>
                    <div style="font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-muted); font-weight: 700; margin-bottom: 0.2rem;">Selected Complaint</div>
                    <h3 style="margin: 0; color: var(--text-primary); font-size: 1.3rem;">{ref_display}</h3>
                </div>
                <div style="display: flex; align-items: center; gap: 1.2rem;">
                    <div>
                        <span style="font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-muted); font-weight: 700; display: block; margin-bottom: 0.2rem;">Current Status</span>
                        {get_status_badge_html(current_status)}
                    </div>
                    <div style="border-left: 1px solid var(--border-color); padding-left: 1.2rem;">
                        <span style="font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-muted); font-weight: 700; display: block; margin-bottom: 0.2rem;">Submission Time</span>
                        <span style="font-size: 0.88rem; color: var(--text-secondary);">{submitted_str} UTC</span>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        rev_col1, rev_col2 = st.columns([3, 2])

        with rev_col1:
            # ── Read-Only Complaint & AI Analysis Details ──────
            with st.container(border=True):
                # ── Section A: Complaint Information ─────────────────────────
                st.markdown("### A. Complaint Information")
                st.markdown("**Original Citizen Complaint**")
                raw_text_val = rec.get("raw_text", "")
                st.info(raw_text_val if raw_text_val else "No complaint text provided.")

                st.divider()

                # ── Section B: AI Analysis ───────────────────────────────────
                st.markdown("### B. AI Analysis")
                summary_val = rec.get("summary", "No summary available.")
                st.markdown(f"**Summary:** {summary_val}")
                st.markdown("<div style='margin-top:0.5rem;'></div>", unsafe_allow_html=True)

                ai_c1, ai_c2, ai_c3 = st.columns(3)
                with ai_c1:
                    st.markdown("**Category**")
                    st.write(rec.get("category", "Unclear"))
                with ai_c2:
                    st.markdown("**Severity**")
                    st.markdown(get_status_badge_html(rec.get("severity", "Medium")), unsafe_allow_html=True)
                with ai_c3:
                    st.markdown("**AI Recommendation**")
                    st.markdown(get_status_badge_html(rec.get("priority", "Urgent")), unsafe_allow_html=True)

                st.markdown("<div style='margin-top:0.8rem;'></div>", unsafe_allow_html=True)
                st.markdown("**Extracted Details**")
                det_c1, det_c2, det_c3 = st.columns(3)
                with det_c1:
                    st.markdown(f"**Location:**\n\n{rec.get('location', 'Unclear')}")
                with det_c2:
                    st.markdown(f"**Duration:**\n\n{rec.get('duration', 'Unclear')}")
                with det_c3:
                    st.markdown(f"**Affected:**\n\n{rec.get('affected_people', 'Unclear')}")

                st.divider()

                # ── Section C: Extracted Information ─────────────────────────
                st.markdown("### C. Extracted Information")
                st.markdown("**Key Facts**")
                raw_facts = rec.get("key_facts", "[]")
                try:
                    facts_list = json.loads(raw_facts) if isinstance(raw_facts, str) else raw_facts
                except Exception:
                    facts_list = []

                if facts_list and isinstance(facts_list, list):
                    for fact in facts_list:
                        st.markdown(f"• {fact}")
                else:
                    st.caption("No key facts extracted")

                st.markdown("<div style='margin-top:0.6rem;'></div>", unsafe_allow_html=True)
                st.markdown("**Missing Information**")
                missing_info = rec.get("missing_info", "None identified")
                if not missing_info or str(missing_info).strip().lower() in ("none", "none identified", ""):
                    missing_info = "None identified"
                st.write(missing_info)

        with rev_col2:
            # ── Editable Municipal Review Section ────────────
            with st.container(border=True):
                # ── Section D: Municipal Review / Human Decision ────────────
                st.markdown("### D. Municipal Review / Human Decision")
                st.caption("Set human operational decisions and dispatch response team")

                # Human oversight notice & explicit decision relationship
                st.markdown(
                    "<p style='font-size:0.78rem; color:var(--text-muted); "
                    "border-left: 2px solid var(--border-color); padding-left: 0.6rem; "
                    "margin-bottom: 0.8rem;'>"
                    "AI Recommendation is advisory. Municipal Priority is the final human operational decision.<br>"
                    "AI recommendations support municipal review. "
                    "Final priority decisions are made by authorized municipal officers."
                    "</p>",
                    unsafe_allow_html=True,
                )

                # Show save confirmation feedback if populated from previous save action
                if "save_success_msg" in st.session_state:
                    st.success(st.session_state.pop("save_success_msg"))

                current_status = rec.get("status") or "Pending"

                # ── AI Recommendation vs Municipal Priority Comparison Container ──
                ai_priority_val = rec.get("priority") or "Unclear"
                raw_muni_pri = rec.get("municipal_priority")  # None if never set
                _muni_pri_opts = ["Not Set", "Low", "Medium", "High", "Urgent"]
                if raw_muni_pri and raw_muni_pri in _muni_pri_opts:
                    current_muni_pri = raw_muni_pri
                else:
                    current_muni_pri = "Not Set"  # never copy AI value

                comp_c1, comp_c2 = st.columns(2)
                with comp_c1:
                    st.markdown("**AI Recommendation**")
                    st.markdown(get_status_badge_html(ai_priority_val), unsafe_allow_html=True)
                    st.caption("<span style='font-size:0.75rem; color:var(--text-muted);'>Advisory AI output</span>", unsafe_allow_html=True)
                with comp_c2:
                    st.markdown("**Current Municipal Priority**")
                    muni_badge_val = current_muni_pri if current_muni_pri != "Not Set" else "Unclear"
                    st.markdown(get_status_badge_html(muni_badge_val), unsafe_allow_html=True)
                    st.caption(f"<span style='font-size:0.75rem; color:var(--text-muted);'>Stored decision ({current_muni_pri})</span>", unsafe_allow_html=True)

                st.markdown("<div style='margin-bottom:0.8rem;'></div>", unsafe_allow_html=True)

                current_team = rec.get("assigned_team") or "Unassigned"
                team_options = [
                    "Unassigned",
                    "Water Supply Team",
                    "Pipeline Maintenance Team",
                    "Emergency Response Team",
                    "Field Inspection Team",
                ]
                if current_team not in team_options:
                    team_options.append(current_team)

                status_opts = ["Pending", "Assigned", "In Progress", "Resolved"]
                if current_status not in status_opts:
                    status_opts.append(current_status)

                is_resolved = current_status == "Resolved"

                if is_resolved:
                    resolved_time_str = str(rec.get("resolved_at", ""))[:19].replace("T", " ")
                    muni_pri_display = current_muni_pri if current_muni_pri != "Not Set" else "Not Set"
                    st.success(
                        f"**Complaint Resolved** on {resolved_time_str} UTC\n\n"
                        f"Team: **{current_team}** | Municipal Priority: **{muni_pri_display}**"
                    )

                    allow_reopen = st.checkbox(
                        "Reopen / Edit Resolved Complaint",
                        value=False,
                        key=f"reopen_{rec['id']}",
                        help="Check this box to unlock and modify municipal review decisions for this resolved complaint.",
                    )

                    if not allow_reopen:
                        st.info("Complaint is locked in Resolved state. Check above to reopen or edit.")

                else:
                    allow_reopen = True

                if not is_resolved or allow_reopen:
                    new_muni_pri_sel = st.selectbox(
                        "Municipal Priority",
                        options=_muni_pri_opts,
                        index=_muni_pri_opts.index(current_muni_pri),
                        key=f"muni_pri_{rec['id']}",
                        help="Final human decision for response priority. AI Recommendation is read-only and unaffected.",
                    )
                    st.caption(
                        "<span style='font-size:0.76rem; color:var(--text-muted);'>"
                        "Final human operational decision</span>",
                        unsafe_allow_html=True,
                    )

                    new_team = st.selectbox(
                        "Assigned Team",
                        options=team_options,
                        index=team_options.index(current_team),
                        key=f"muni_team_{rec['id']}",
                    )

                    new_status = st.selectbox(
                        "Status",
                        options=status_opts,
                        index=status_opts.index(current_status),
                        key=f"muni_status_{rec['id']}",
                        help="Updating status to Resolved automatically records completion time.",
                    )

                    new_notes = st.text_area(
                        "Review Notes",
                        value=rec.get("review_notes") or "",
                        placeholder="Enter officer review notes, field instructions, or resolution details...",
                        height=180,
                        key=f"muni_notes_{rec['id']}",
                    )
                    st.caption(
                        "<span style='font-size:0.76rem; color:var(--text-muted);'>"
                        "Internal notes for municipal review, observations, or operational context."
                        "</span>",
                        unsafe_allow_html=True,
                    )

                    if st.button("Save Municipal Review", type="primary", use_container_width=True, key=f"save_rev_{rec['id']}"):
                        resolved_at_val = (
                            datetime.utcnow().isoformat()
                            if new_status == "Resolved"
                            else (rec.get("resolved_at") if new_status == "Resolved" else None)
                        )
                        muni_pri_to_save = (
                            None if new_muni_pri_sel == "Not Set" else new_muni_pri_sel
                        )
                        success = update_complaint_workflow(
                            complaint_id=rec["id"],
                            status=new_status,
                            assigned_team=new_team,
                            municipal_priority=muni_pri_to_save,
                            review_notes=new_notes,
                            resolved_at=resolved_at_val,
                        )
                        if success:
                            ref_saved = rec.get("reference_id") or f"WGA-#{rec['id']}"
                            st.session_state["save_success_msg"] = (
                                f"Municipal decision saved for **{ref_saved}**\n\n"
                                f"Municipal Priority: **{new_muni_pri_sel}** | Status: **{new_status}** | Assigned Team: **{new_team}**"
                            )
                            st.rerun()
                        else:
                            st.error("Failed to save municipal review.")

            # ── Section E: Municipal Action ──────────────────
            st.markdown("<div style='margin-top: 0.8rem;'></div>", unsafe_allow_html=True)
            with st.container(border=True):
                st.markdown("### E. Municipal Action")
                st.caption("Operational workflow state & next step summary")

                def generate_action_summary(status: str, assigned_team: str, municipal_priority: str | None) -> str:
                    team_clean = assigned_team if assigned_team and assigned_team != "Unassigned" else None

                    if status == "Resolved":
                        return "Complaint has been marked as resolved."
                    elif status == "In Progress":
                        if team_clean:
                            return f"{team_clean} is currently handling this complaint."
                        else:
                            return "The assigned municipal team is currently handling this complaint."
                    elif status == "Assigned":
                        if team_clean:
                            return f"Complaint assigned to {team_clean} for municipal follow-up."
                        else:
                            return "Complaint has been assigned for municipal follow-up."
                    else:  # Pending
                        if team_clean:
                            return f"Complaint assigned to {team_clean} and is pending municipal action."
                        else:
                            return "Complaint is pending municipal team assignment."

                action_text = generate_action_summary(current_status, current_team, raw_muni_pri)

                st.markdown(
                    f"""
                    <div style="background: var(--bg-card-subtle); border: 1px solid var(--border-color); border-radius: 8px; padding: 0.85rem 1rem; margin-bottom: 0.8rem;">
                        <div style="font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-muted); font-weight: 700; margin-bottom: 0.2rem;">Action Summary</div>
                        <div style="font-size: 0.92rem; font-weight: 600; color: var(--text-primary);">{action_text}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                act_m1, act_m2 = st.columns(2)
                with act_m1:
                    st.markdown("**Current Status**")
                    st.markdown(get_status_badge_html(current_status), unsafe_allow_html=True)
                with act_m2:
                    muni_pri_txt = current_muni_pri if current_muni_pri != "Not Set" else "Not Set"
                    st.markdown(f"**Operational Priority:** {muni_pri_txt}")

                st.markdown("<div style='margin-top: 0.4rem;'></div>", unsafe_allow_html=True)
                team_display_txt = current_team if current_team else "Unassigned"
                st.markdown(f"**Assigned Team:** {team_display_txt}")

                notes_val = rec.get("review_notes")
                if notes_val and str(notes_val).strip():
                    st.markdown("<div style='margin-top: 0.4rem;'></div>", unsafe_allow_html=True)
                    st.markdown(f"**Review Notes Context:** <span style='color: var(--text-secondary); font-size: 0.88rem;'>{notes_val}</span>", unsafe_allow_html=True)


# ============================================================
# MUNICIPAL WORKLOAD STATISTICS & DISTRIBUTIONS
# ============================================================

st.markdown("<br>", unsafe_allow_html=True)
st.markdown(
    f"""
    <div style="display:flex; align-items:center; gap:8px; margin-bottom:0.8rem;">
        {get_icon_svg("bar-chart-2", color=icon_accent, size=20)}
        <h3 style="margin:0;">Municipal Workload Statistics</h3>
    </div>
    """,
    unsafe_allow_html=True,
)

s_col1, s_col2, s_col3 = st.columns(3)

with s_col1:
    st.markdown("#### Status Distribution")
    if not df.empty and "status" in df.columns:
        status_counts = (
            df["status"]
            .value_counts()
            .reindex(
                [
                    "Pending",
                    "Assigned",
                    "In Progress",
                    "Resolved",
                ],
                fill_value=0,
            )
        )
        st.bar_chart(status_counts)
    else:
        st.info("No complaint status data available.")

with s_col2:
    st.markdown("#### Category Distribution")
    if not df.empty and "category" in df.columns and not df["category"].dropna().empty:
        category_counts = df["category"].value_counts()
        st.bar_chart(category_counts)
    else:
        st.info("No complaint category data available.")

with s_col3:
    st.markdown("#### AI Recommendation Distribution")
    if not df.empty and "priority" in df.columns:
        ai_pri_counts = (
            df["priority"]
            .value_counts()
            .reindex(
                [
                    "Urgent",
                    "High",
                    "Medium",
                    "Low",
                ],
                fill_value=0,
            )
        )
        st.bar_chart(ai_pri_counts)
    else:
        st.info("No AI recommendation data available.")


