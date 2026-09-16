"""
pages/3_Citizen_Login.py
Citizen Portal Login for the AI-Powered Water Grievance Analyzer.
"""

import streamlit as st

from core.auth import get_authenticated_user, is_citizen_authenticated, logout, render_citizen_login_form
from core.ui_icons import get_icon_svg

icon_accent = "#38bdf8"

st.markdown(
    f"""
    <div style="display:flex; align-items:center; gap:10px; margin-bottom:0.25rem;">
        {get_icon_svg("user", color=icon_accent, size=26)}
        <h2 style="margin:0;">Citizen Portal Access</h2>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <p style="font-size:1rem; color:var(--text-secondary); margin-bottom:1.5rem;">
        Public portal for citizens to submit water grievances and track resolution status.
    </p>
    """,
    unsafe_allow_html=True,
)

if is_citizen_authenticated():
    user = get_authenticated_user()
    st.markdown(
        f"""
        <div class="content-card" style="max-width: 580px; margin: 1.5rem auto; padding: 2rem;">
            <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 1rem;">
                <div class="card-icon-box">{get_icon_svg("check-circle", color="#34d399", size=22)}</div>
                <div>
                    <h3 style="margin: 0; font-size: 1.2rem;">Citizen Session Active</h3>
                    <p style="margin: 0.2rem 0 0 0; font-size: 0.88rem; color: var(--text-muted);">
                        Signed in as <strong>{user}</strong>
                    </p>
                </div>
            </div>
            <p style="font-size: 0.9rem; color: var(--text-secondary);">
                You can submit new water complaints for IBM Granite AI analysis or track your existing complaints.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2 = st.columns(2)
    with c1:
        if st.button("Submit Water Complaint", type="primary", use_container_width=True):
            st.switch_page("pages/1_Submit_Complaint.py")
    with c2:
        if st.button("Sign Out", type="secondary", use_container_width=True):
            logout()
            st.rerun()
else:
    if st.button("← Back to Role Selection", type="secondary"):
        st.switch_page("app.py")
    render_citizen_login_form()
