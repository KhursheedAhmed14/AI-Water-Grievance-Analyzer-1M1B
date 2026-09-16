"""
pages/4_Municipal_Login.py
Municipal Team Portal Login for the AI-Powered Water Grievance Analyzer.
"""

import streamlit as st

from core.auth import get_authenticated_user, is_municipal_authenticated, logout, render_municipal_login_form
from core.ui_icons import get_icon_svg

icon_accent = "#38bdf8"

st.markdown(
    f"""
    <div style="display:flex; align-items:center; gap:10px; margin-bottom:0.25rem;">
        {get_icon_svg("lock", color=icon_accent, size=26)}
        <h2 style="margin:0;">Municipal Team Portal</h2>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <p style="font-size:1rem; color:var(--text-secondary); margin-bottom:1.5rem;">
        Authorized portal for municipal officers, triage teams, and department personnel.
    </p>
    """,
    unsafe_allow_html=True,
)

if is_municipal_authenticated():
    user = get_authenticated_user()
    st.markdown(
        f"""
        <div class="content-card" style="max-width: 580px; margin: 1.5rem auto; padding: 2rem;">
            <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 1rem;">
                <div class="card-icon-box">{get_icon_svg("check-circle", color="#34d399", size=22)}</div>
                <div>
                    <h3 style="margin: 0; font-size: 1.2rem;">Municipal Officer Session Active</h3>
                    <p style="margin: 0.2rem 0 0 0; font-size: 0.88rem; color: var(--text-muted);">
                        Authenticated as Officer <strong>{user}</strong>
                    </p>
                </div>
            </div>
            <p style="font-size: 0.9rem; color: var(--text-secondary);">
                You have full operational access to the Municipal Dashboard, complaint triage queues, team assignment, and priority decisions.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2 = st.columns(2)
    with c1:
        if st.button("Open Municipal Dashboard", type="primary", use_container_width=True):
            st.switch_page("pages/5_Municipal_Dashboard.py")
    with c2:
        if st.button("Sign Out", type="secondary", use_container_width=True):
            logout()
            st.rerun()
else:
    if st.button("← Back to Role Selection", type="secondary"):
        st.switch_page("app.py")
    render_municipal_login_form()
