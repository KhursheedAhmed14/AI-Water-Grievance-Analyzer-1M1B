"""
core/landing.py
Role Selection Landing Page definition for AI-Powered Water Grievance Analyzer.
"""

import streamlit as st

from config.settings import credentials_configured
from core.auth import get_authenticated_user, get_current_role
from core.ui_icons import get_icon_svg
from core.ui_theme import get_logo_base64


def render_role_selection_landing():
    """Render high-impact landing page matching requested mockup design."""
    logo_b64 = get_logo_base64()
    logo_html = (
        f'<img src="{logo_b64}" class="sidebar-logo-img" alt="Water Logo"/>'
        if logo_b64
        else get_icon_svg("water", color="#38bdf8", size=32)
    )

    # ── Top Bar Header ────────────────────────────────────────────────────────
    st.markdown(
        f"""
        <div class="landing-top-bar">
            <div class="landing-top-logo">
                <div class="sidebar-logo-wrapper" style="width: 44px; height: 44px;">
                    {logo_html}
                </div>
                <div>
                    <div class="landing-top-title">Water</div>
                    <div class="landing-top-subtitle">Grievance Analyzer</div>
                </div>
            </div>
            <div style="font-size: 0.88rem; color: #94a3b8; letter-spacing: 0.05em; font-weight: 500;">
                AI for a Water-Secure Tomorrow
            </div>
            <div class="landing-top-sdg">
                <div class="landing-top-sdg-tag">Clean Water. Stronger Communities.</div>
                <div class="landing-top-sdg-val">SDG 6 — Clean Water and Sanitation</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Credentials Status Notice (if not configured) ──────────────────────────
    if not credentials_configured():
        st.error(
            "IBM watsonx.ai credentials are not configured. "
            "Set WATSONX_API_KEY, WATSONX_PROJECT_ID, and WATSONX_URL in .env.",
        )

    # ── Main Hero Title Block ──────────────────────────────────────────────────
    st.markdown(
        """
        <div class="landing-hero">
            <h1 class="landing-hero-title">Water <span class="landing-hero-glow-blue">Grievance</span> Analyzer</h1>
            <p class="landing-hero-tagline">Report. Analyze. Resolve. For a Healthier Tomorrow.</p>
        </div>

        <div class="role-section-header">
            <h2 class="role-section-title">How would you like to continue?</h2>
            <p class="role-section-subtitle">Choose your role to access the appropriate portal</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    current_role = get_current_role()
    active_user = get_authenticated_user()

    # ── Two Role Selection Cards Grid ─────────────────────────────────────────
    role_col1, role_col2 = st.columns(2)

    with role_col1:
        st.markdown(
            f"""
            <div class="landing-card-citizen">
                <div>
                    <div class="role-icon-circle-blue">
                        {get_icon_svg("user", color="#38bdf8", size=28, centered=True)}
                    </div>
                    <h3 class="role-card-title">Citizen</h3>
                    <p class="role-card-desc">Report water-related problems and track your complaints.</p>
                    <ul class="role-card-features">
                        <li>{get_icon_svg("file-text", color="#38bdf8", size=18)} Submit a water complaint</li>
                        <li>{get_icon_svg("search", color="#38bdf8", size=18)} View your complaints</li>
                        <li>{get_icon_svg("bell", color="#38bdf8", size=18)} Get status updates</li>
                    </ul>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("<div style='margin-top: 0.75rem;'></div>", unsafe_allow_html=True)
        st.markdown('<div class="btn-citizen">', unsafe_allow_html=True)
        if current_role == "citizen":
            st.info(f"Signed in as Citizen (**{active_user}**)")
            if st.button("Continue as Citizen →", type="primary", use_container_width=True, key="landing_citizen_btn"):
                st.switch_page("pages/1_Submit_Complaint.py")
        else:
            if st.button("Continue as Citizen →", type="primary", use_container_width=True, key="landing_citizen_btn"):
                st.switch_page("pages/3_Citizen_Login.py")
        st.markdown('</div>', unsafe_allow_html=True)

    with role_col2:
        st.markdown(
            f"""
            <div class="landing-card-municipal">
                <div>
                    <div class="role-icon-circle-green">
                        {get_icon_svg("building", color="#34d399", size=28, centered=True)}
                    </div>
                    <h3 class="role-card-title">Municipal Team</h3>
                    <p class="role-card-desc">Review, prioritize, and manage water grievances.</p>
                    <ul class="role-card-features">
                        <li>{get_icon_svg("layout", color="#34d399", size=18)} Access complaint dashboard</li>
                        <li>{get_icon_svg("users", color="#34d399", size=18)} Assign teams and track progress</li>
                        <li>{get_icon_svg("bar-chart-2", color="#34d399", size=18)} Take action for cleaner communities</li>
                    </ul>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("<div style='margin-top: 0.75rem;'></div>", unsafe_allow_html=True)
        st.markdown('<div class="btn-municipal">', unsafe_allow_html=True)
        if current_role == "municipal":
            st.info(f"Signed in as Officer (**{active_user}**)")
            if st.button("Continue as Municipal Team →", type="primary", use_container_width=True, key="landing_muni_btn"):
                st.switch_page("pages/5_Municipal_Dashboard.py")
        else:
            if st.button("Continue as Municipal Team →", type="primary", use_container_width=True, key="landing_muni_btn"):
                st.switch_page("pages/4_Municipal_Login.py")
        st.markdown('</div>', unsafe_allow_html=True)

    # ── 4 Column Feature Icons Bar ───────────────────────────────────────────
    st.markdown(
        f"""
        <div class="landing-features-bar">
            <div class="feature-item">
                <div class="feature-item-icon">{get_icon_svg("feather", color="#34d399", size=20, centered=True)}</div>
                <div>
                    <div class="feature-item-title">Clean Water</div>
                    <div class="feature-item-sub">Better Living</div>
                </div>
            </div>
            <div class="feature-item">
                <div class="feature-item-icon">{get_icon_svg("users", color="#38bdf8", size=20, centered=True)}</div>
                <div>
                    <div class="feature-item-title">Stronger Communities</div>
                    <div class="feature-item-sub">Together We Solve</div>
                </div>
            </div>
            <div class="feature-item">
                <div class="feature-item-icon">{get_icon_svg("cpu", color="#38bdf8", size=20, centered=True)}</div>
                <div>
                    <div class="feature-item-title">AI-Powered</div>
                    <div class="feature-item-sub">Smart Solutions</div>
                </div>
            </div>
            <div class="feature-item">
                <div class="feature-item-icon">{get_icon_svg("globe", color="#38bdf8", size=20, centered=True)}</div>
                <div>
                    <div class="feature-item-title">Sustainable Future</div>
                    <div class="feature-item-sub">For Generations</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Footer Bar ────────────────────────────────────────────────────────────
    st.markdown(
        """
        <div class="landing-footer-bar">
            <div>
                <strong style="color: #ffffff;">Water Grievance Analyzer</strong> — An AI-powered solution for SDG 6
            </div>
            <div>
                Clean Water Today. Brighter Tomorrow.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# Role Selection Page target for st.navigation
page_landing = st.Page(render_role_selection_landing, title="Role Selection", default=True)
