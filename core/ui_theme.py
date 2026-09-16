"""
core/ui_theme.py
Custom styling system and UI component rendering for AI-Powered Water Grievance Analyzer.
Provides modern municipal civic-tech design tokens, dark background theme, card styles,
status badges, and clean typography.
"""

import base64
from pathlib import Path
import urllib.parse
import streamlit as st
from core.auth import get_authenticated_user, get_current_role, logout
from core.ui_icons import get_icon_svg

PROJECT_ROOT = Path(__file__).parent.parent
LOGO_PATH = str(PROJECT_ROOT / "assets" / "water_grievance_logo.png")


@st.cache_data
def get_logo_base64() -> str:
    """Return base64 encoded data URI for the website logo image (cached to eliminate lag)."""
    try:
        p = Path(LOGO_PATH)
        if p.exists():
            data = base64.b64encode(p.read_bytes()).decode("utf-8")
            return f"data:image/png;base64,{data}"
    except Exception:
        pass
    return ""


@st.cache_data
def get_svg_data_uri(name: str, color: str = "#38bdf8", size: int = 18) -> str:
    """Return URL-encoded SVG data URI string for CSS background-image (cached for performance)."""
    svg_str = get_icon_svg(name, color=color, size=size)
    encoded = urllib.parse.quote(svg_str)
    return f"data:image/svg+xml;charset=utf-8,{encoded}"


def render_sidebar_top_branding():
    """Render top logo and website branding block in sidebar ONLY when authenticated."""
    role = get_current_role()
    if not role:
        return

    logo_b64 = get_logo_base64()
    accent_color = "#38bdf8"
    logo_html = (
        f'<img src="{logo_b64}" class="sidebar-logo-img" alt="Water Grievance Logo"/>'
        if logo_b64
        else get_icon_svg("water", color=accent_color, size=32)
    )

    st.sidebar.markdown(
        f"""
        <div class="sidebar-top-branding">
            <div class="sidebar-brand-header">
                <div class="sidebar-logo-wrapper">
                    {logo_html}
                </div>
                <div class="sidebar-title-wrapper">
                    <div class="brand-title">Water</div>
                    <div class="brand-subtitle">Grievance Analyzer</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar_account():
    """Render bottom account status badge and single Sign Out Session button in sidebar ONLY when authenticated."""
    role = get_current_role()
    if not role:
        return

    active_user = get_authenticated_user()
    role_label = "Citizen" if role == "citizen" else "Officer"
    role_color = "#38bdf8" if role == "citizen" else "#34d399"
    badge_bg = "rgba(56, 189, 248, 0.12)" if role == "citizen" else "rgba(52, 211, 153, 0.12)"
    badge_border = "rgba(56, 189, 248, 0.3)" if role == "citizen" else "rgba(52, 211, 153, 0.3)"
    icon_name = "user" if role == "citizen" else "shield-check"

    st.sidebar.markdown(
        f"""
        <div class="sidebar-account-badge">
            <div class="sidebar-user-badge" style="background:{badge_bg}; border:1px solid {badge_border};">
                <div class="sidebar-badge-header">
                    {get_icon_svg(icon_name, color=role_color, size=15)}
                    <span class="sidebar-role-title" style="color:{role_color};"><strong>{role_label}:</strong></span>
                </div>
                <div class="sidebar-user-email" style="color:{role_color};">{active_user}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.sidebar.button("Sign Out", key="sidebar_logout_btn", use_container_width=True):
        logout()
        st.rerun()


def render_sidebar_branding():
    """Render complete top branding in sidebar."""
    st.session_state["theme"] = "dark"
    render_sidebar_top_branding()


def apply_custom_theme():
    """Inject municipal civic-tech CSS styling for a clean, professional Dark background theme."""
    st.session_state["theme"] = "dark"

    role = get_current_role()
    sidebar_hide_css = ""
    if not role:
        sidebar_hide_css = """
        section[data-testid="stSidebar"],
        [data-testid="stSidebarNav"],
        [data-testid="stSidebarCollapsedControl"] {
            display: none !important;
            width: 0px !important;
        }
        [data-testid="stMainBlockContainer"],
        .main .block-container {
            max-width: 1200px !important;
            padding-left: 2rem !important;
            padding-right: 2rem !important;
        }
        """

    nav_icon_color = "#38bdf8"
    nav_active_color = "#ffffff"

    home_svg = get_svg_data_uri("home", color=nav_icon_color, size=18)
    home_active = get_svg_data_uri("home", color=nav_active_color, size=18)
    search_svg = get_svg_data_uri("search", color=nav_icon_color, size=18)
    search_active = get_svg_data_uri("search", color=nav_active_color, size=18)
    file_svg = get_svg_data_uri("file-text", color=nav_icon_color, size=18)
    file_active = get_svg_data_uri("file-text", color=nav_active_color, size=18)
    user_svg = get_svg_data_uri("user", color=nav_icon_color, size=18)
    user_active = get_svg_data_uri("user", color=nav_active_color, size=18)
    lock_svg = get_svg_data_uri("lock", color=nav_icon_color, size=18)
    lock_active = get_svg_data_uri("lock", color=nav_active_color, size=18)
    building_svg = get_svg_data_uri("building", color=nav_icon_color, size=18)
    building_active = get_svg_data_uri("building", color=nav_active_color, size=18)
    info_svg = get_svg_data_uri("info", color=nav_icon_color, size=18)
    info_active = get_svg_data_uri("info", color=nav_active_color, size=18)

    file_plus_svg_cyan = get_svg_data_uri("file-plus", color="#38bdf8", size=20)
    file_plus_svg_white = get_svg_data_uri("file-plus", color="#ffffff", size=20)

    file_svg_cyan = get_svg_data_uri("file-text", color="#38bdf8", size=20)
    file_svg_white = get_svg_data_uri("file-text", color="#ffffff", size=20)

    dashboard_svg_cyan = get_svg_data_uri("dashboard", color="#38bdf8", size=20)
    dashboard_svg_white = get_svg_data_uri("dashboard", color="#ffffff", size=20)

    building_svg_cyan = get_svg_data_uri("building", color="#38bdf8", size=20)
    building_svg_white = get_svg_data_uri("building", color="#ffffff", size=20)

    info_svg_cyan = get_svg_data_uri("info", color="#38bdf8", size=20)
    info_svg_white = get_svg_data_uri("info", color="#ffffff", size=20)

    logout_svg_muted = get_svg_data_uri("log-out", color="#94a3b8", size=16)
    logout_svg_hover = get_svg_data_uri("log-out", color="#f87171", size=16)

    theme_variables = f"""
        --bg-app: #0f172a;
        --bg-card: #1e293b;
        --bg-card-subtle: #172133;
        --bg-sidebar: #0b132b;
        --border-color: #334155;
        --border-light: #1e293b;
        --text-primary: #f8fafc;
        --text-secondary: #cbd5e1;
        --text-muted: #94a3b8;
        --accent-blue: #0284c7;
        --accent-blue-hover: #0369a1;
        --accent-blue-light: #38bdf8;
        --hero-bg: linear-gradient(135deg, #0f172a 0%, #1e293b 60%, #0369a1 100%);
        --hero-text: #ffffff;
        --card-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
        --badge-urgent-bg: rgba(239, 68, 68, 0.15);
        --badge-urgent-color: #f87171;
        --badge-urgent-border: rgba(239, 68, 68, 0.3);
        --badge-high-bg: rgba(249, 115, 22, 0.15);
        --badge-high-color: #fb923c;
        --badge-high-border: rgba(249, 115, 22, 0.3);
        --badge-medium-bg: rgba(245, 158, 11, 0.15);
        --badge-medium-color: #fbbf24;
        --badge-medium-border: rgba(245, 158, 11, 0.3);
        --badge-low-bg: rgba(14, 165, 233, 0.15);
        --badge-low-color: #38bdf8;
        --badge-low-border: rgba(14, 165, 233, 0.3);
        --badge-info-bg: rgba(148, 163, 184, 0.15);
        --badge-info-color: #cbd5e1;
        --badge-info-border: rgba(148, 163, 184, 0.3);
    """

    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

        :root {{
            {theme_variables}
        }}

        html, body, [class*="css"] {{
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
        }}

        /* App Main Background */
        .stApp,
        [data-testid="stAppViewContainer"],
        [data-testid="stMain"],
        [data-testid="stMainBlockContainer"],
        [data-testid="stHeader"],
        .main,
        section.main {{
            background-color: var(--bg-app) !important;
            color: var(--text-primary) !important;
        }}

        /* Hide default Streamlit top header toolbar, deploy button & developer main menu */
        header[data-testid="stHeader"],
        [data-testid="stToolbar"],
        [data-testid="stDecoration"],
        #MainMenu {{
            display: none !important;
            visibility: hidden !important;
        }}

        /* Logged Out Full-Width Sidebar Hide Rule */
        {sidebar_hide_css}

        /* Global Headings */
        h1, h2, h3, h4, h5, h6 {{
            color: var(--text-primary) !important;
            font-weight: 700 !important;
            letter-spacing: -0.01em !important;
        }}

        p, span, label, div {{
            color: var(--text-primary);
        }}

        /* Hero Banner */
        .hero-banner {{
            background: var(--hero-bg);
            color: var(--hero-text);
            padding: 2rem 2.2rem;
            border-radius: 14px;
            margin-bottom: 1.8rem;
            box-shadow: 0 10px 25px -5px rgba(2, 132, 199, 0.2);
        }}
        .hero-banner h1 {{
            color: #ffffff !important;
            font-weight: 700;
            font-size: 2.1rem;
            margin-bottom: 0.5rem;
            letter-spacing: -0.02em;
        }}
        .hero-banner p {{
            color: #e0f2fe !important;
            font-size: 1rem;
            margin-bottom: 0;
            opacity: 0.95;
            line-height: 1.5;
        }}
        .sdg-tag {{
            display: inline-flex;
            align-items: center;
            background: rgba(255, 255, 255, 0.18);
            backdrop-filter: blur(6px);
            border: 1px solid rgba(255, 255, 255, 0.3);
            color: #ffffff !important;
            font-size: 0.8rem;
            font-weight: 600;
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            margin-bottom: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}

        /* High-Impact Mockup Landing Page Aesthetics */
        .landing-top-bar {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0.5rem 0 1.2rem 0;
            border-bottom: 1px solid rgba(51, 65, 85, 0.4);
            margin-bottom: 1.8rem;
        }}
        .landing-top-logo {{
            display: flex;
            align-items: center;
            gap: 12px;
        }}
        .landing-top-title {{
            font-size: 1.35rem;
            font-weight: 800;
            letter-spacing: -0.02em;
            color: #ffffff !important;
            line-height: 1.1;
        }}
        .landing-top-subtitle {{
            font-size: 0.82rem;
            color: #38bdf8 !important;
            font-weight: 600;
        }}
        .landing-top-sdg {{
            text-align: right;
        }}
        .landing-top-sdg-tag {{
            font-size: 0.78rem;
            color: #94a3b8;
        }}
        .landing-top-sdg-val {{
            font-weight: 700;
            color: #38bdf8 !important;
            font-size: 0.92rem;
        }}

        .landing-hero {{
            text-align: center;
            padding: 0.5rem 0 1.5rem 0;
        }}
        .landing-hero-pretitle {{
            font-size: 0.88rem;
            text-transform: uppercase;
            letter-spacing: 0.18em;
            color: #38bdf8 !important;
            font-weight: 700;
            margin-bottom: 0.6rem;
        }}
        .landing-hero-title {{
            font-size: 3.1rem !important;
            font-weight: 800 !important;
            color: #ffffff !important;
            letter-spacing: -0.03em !important;
            line-height: 1.15;
            margin-bottom: 0.6rem;
        }}
        .landing-hero-glow-blue {{
            background: linear-gradient(135deg, #38bdf8 0%, #0284c7 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            filter: drop-shadow(0 0 16px rgba(56, 189, 248, 0.45));
        }}
        .landing-hero-tagline {{
            font-size: 1.05rem;
            color: #cbd5e1 !important;
            font-weight: 500;
            margin-bottom: 1.8rem;
        }}

        .role-section-header {{
            text-align: center;
            margin-bottom: 2rem;
        }}
        .role-section-title {{
            font-size: 1.55rem;
            font-weight: 700;
            color: #ffffff !important;
            margin-bottom: 0.3rem;
        }}
        .role-section-subtitle {{
            font-size: 0.95rem;
            color: #94a3b8 !important;
        }}

        /* Glassmorphic Landing Cards */
        .landing-card-citizen {{
            background: linear-gradient(180deg, rgba(30, 41, 59, 0.75) 0%, rgba(15, 23, 42, 0.95) 100%);
            border: 1.5px solid rgba(56, 189, 248, 0.35);
            border-radius: 20px;
            padding: 2.2rem 2rem;
            box-shadow: 0 12px 35px -10px rgba(2, 132, 199, 0.3);
            transition: all 0.25s ease;
            position: relative;
            overflow: hidden;
            height: 100%;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }}
        .landing-card-citizen:hover {{
            border-color: rgba(56, 189, 248, 0.65);
            box-shadow: 0 16px 45px -8px rgba(56, 189, 248, 0.4);
            transform: translateY(-3px);
        }}

        .landing-card-municipal {{
            background: linear-gradient(180deg, rgba(30, 41, 59, 0.75) 0%, rgba(15, 23, 42, 0.95) 100%);
            border: 1.5px solid rgba(52, 211, 153, 0.35);
            border-radius: 20px;
            padding: 2.2rem 2rem;
            box-shadow: 0 12px 35px -10px rgba(16, 185, 129, 0.3);
            transition: all 0.25s ease;
            position: relative;
            overflow: hidden;
            height: 100%;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }}
        .landing-card-municipal:hover {{
            border-color: rgba(52, 211, 153, 0.65);
            box-shadow: 0 16px 45px -8px rgba(52, 211, 153, 0.4);
            transform: translateY(-3px);
        }}

        .role-icon-circle-blue,
        .role-icon-circle-green {{
            width: 56px;
            height: 56px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 1.2rem;
        }}
        .role-icon-circle-blue {{
            background: rgba(2, 132, 199, 0.25);
            border: 1px solid rgba(56, 189, 248, 0.4);
        }}
        .role-icon-circle-green {{
            background: rgba(16, 185, 129, 0.25);
            border: 1px solid rgba(52, 211, 153, 0.4);
        }}
        /* Force SVGs to be centered and have no horizontal offset inside circles */
        .role-icon-circle-blue svg,
        .role-icon-circle-green svg,
        .feature-item-icon svg {{
            display: block !important;
            margin: 0 !important;
            flex-shrink: 0;
        }}

        .role-card-title {{
            font-size: 1.75rem;
            font-weight: 700;
            color: #ffffff !important;
            margin-bottom: 0.4rem;
        }}
        .role-card-desc {{
            font-size: 0.95rem;
            color: #cbd5e1 !important;
            margin-bottom: 1.5rem;
            line-height: 1.5;
        }}
        .role-card-features {{
            list-style: none;
            padding: 0;
            margin: 0 0 1.8rem 0;
            display: flex;
            flex-direction: column;
            gap: 12px;
        }}
        .role-card-features li {{
            display: flex;
            align-items: center;
            gap: 12px;
            font-size: 0.92rem;
            color: #e2e8f0 !important;
            font-weight: 500;
        }}

        /* 4 Column Feature Bar */
        .landing-features-bar {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 1rem;
            margin-top: 3rem;
            margin-bottom: 2rem;
            padding-top: 1.8rem;
            border-top: 1px solid rgba(51, 65, 85, 0.4);
        }}
        .feature-item {{
            display: flex;
            align-items: center;
            gap: 12px;
            background: rgba(30, 41, 59, 0.4);
            border: 1px solid rgba(51, 65, 85, 0.5);
            padding: 0.85rem 1rem;
            border-radius: 12px;
        }}
        .feature-item-icon {{
            width: 40px;
            height: 40px;
            min-width: 40px;
            border-radius: 50%;
            background: rgba(15, 23, 42, 0.6);
            border: 1px solid var(--border-color);
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .feature-item-title {{
            font-size: 0.88rem;
            font-weight: 700;
            color: #ffffff !important;
            line-height: 1.2;
        }}
        .feature-item-sub {{
            font-size: 0.78rem;
            color: #94a3b8 !important;
        }}

        .landing-footer-bar {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 1.2rem 0 0.5rem 0;
            border-top: 1px solid rgba(51, 65, 85, 0.4);
            font-size: 0.82rem;
            color: #94a3b8;
        }}

        /* Button Customizations for Citizen & Municipal */
        .btn-citizen button,
        .stButton.btn-citizen > button {{
            background: linear-gradient(135deg, #0284c7 0%, #38bdf8 100%) !important;
            color: #ffffff !important;
            border: none !important;
            border-radius: 12px !important;
            padding: 0.75rem 1.5rem !important;
            font-size: 1rem !important;
            font-weight: 700 !important;
            box-shadow: 0 4px 15px rgba(2, 132, 199, 0.4) !important;
            transition: all 0.2s ease !important;
        }}
        .btn-citizen button:hover,
        .stButton.btn-citizen > button:hover {{
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 20px rgba(56, 189, 248, 0.5) !important;
        }}

        .btn-municipal button,
        .stButton.btn-municipal > button {{
            background: linear-gradient(135deg, #10b981 0%, #34d399 100%) !important;
            color: #ffffff !important;
            border: none !important;
            border-radius: 12px !important;
            padding: 0.75rem 1.5rem !important;
            font-size: 1rem !important;
            font-weight: 700 !important;
            box-shadow: 0 4px 15px rgba(16, 185, 129, 0.4) !important;
            transition: all 0.2s ease !important;
        }}
        .btn-municipal button:hover,
        .stButton.btn-municipal > button:hover {{
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 20px rgba(52, 211, 153, 0.5) !important;
        }}

        /* Municipal Metric Cards */
        .saas-metric-card {{
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 1.15rem 1.25rem;
            box-shadow: var(--card-shadow);
            transition: transform 0.15s ease, box-shadow 0.15s ease;
        }}
        .saas-metric-card:hover {{
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        }}
        .saas-metric-title {{
            font-size: 0.8rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            color: var(--text-muted) !important;
            margin-bottom: 0.35rem;
        }}
        .saas-metric-value {{
            font-size: 1.75rem;
            font-weight: 700;
            color: var(--accent-blue-light) !important;
            line-height: 1.2;
        }}
        .saas-metric-sub {{
            font-size: 0.78rem;
            color: var(--text-muted) !important;
            margin-top: 0.3rem;
        }}

        /* Status Badges */
        .badge {{
            display: inline-flex;
            align-items: center;
            padding: 0.35rem 0.75rem;
            border-radius: 20px;
            font-size: 0.82rem;
            font-weight: 600;
            letter-spacing: 0.01em;
        }}
        .badge-urgent {{ background: var(--badge-urgent-bg); color: var(--badge-urgent-color) !important; border: 1px solid var(--badge-urgent-border); }}
        .badge-high   {{ background: var(--badge-high-bg); color: var(--badge-high-color) !important; border: 1px solid var(--badge-high-border); }}
        .badge-medium {{ background: var(--badge-medium-bg); color: var(--badge-medium-color) !important; border: 1px solid var(--badge-medium-border); }}
        .badge-low    {{ background: var(--badge-low-bg); color: var(--badge-low-color) !important; border: 1px solid var(--badge-low-border); }}
        .badge-info   {{ background: var(--badge-info-bg); color: var(--badge-info-color) !important; border: 1px solid var(--badge-info-border); }}
        .badge-unclear{{ background: var(--badge-info-bg); color: var(--badge-info-color) !important; border: 1px solid var(--badge-info-border); }}

        /* Content & Feature Cards */
        .content-card {{
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 1.35rem 1.45rem;
            margin-bottom: 1rem;
            box-shadow: var(--card-shadow);
        }}
        .content-card h3, .content-card h4 {{
            color: var(--text-primary) !important;
            margin-top: 0;
            font-weight: 600;
        }}

        /* Universal Height Stretching Rules for Streamlit Column Containers */
        [data-testid="stHorizontalBlock"] {{
            align-items: stretch !important;
        }}
        [data-testid="stColumn"] {{
            display: flex !important;
            flex-direction: column !important;
        }}
        [data-testid="stColumn"] > div,
        [data-testid="stColumn"] [data-testid="stVerticalBlockBorderWrapper"],
        [data-testid="stColumn"] [data-testid="stVerticalBlock"] {{
            height: 100% !important;
            display: flex !important;
            flex-direction: column !important;
            flex: 1 1 auto !important;
        }}

        /* Prevent input widgets & form controls from getting stretched or squished */
        [data-testid="stColumn"] [data-testid="stElementContainer"]:has(.stTextArea),
        [data-testid="stColumn"] [data-testid="stElementContainer"]:has(.stSelectbox),
        [data-testid="stColumn"] [data-testid="stElementContainer"]:has(.stTextInput),
        [data-testid="stColumn"] [data-testid="stElementContainer"]:has(.stButton),
        [data-testid="stElementContainer"]:has(.stTextArea),
        [data-testid="stElementContainer"]:has(.stSelectbox),
        [data-testid="stElementContainer"]:has(.stTextInput),
        [data-testid="stElementContainer"]:has(.stButton) {{
            height: auto !important;
            flex: 0 0 auto !important;
        }}

        /* Ensure stTextArea has full natural height without clipping or scrollbar */
        [data-testid="stTextArea"],
        .stTextArea {{
            height: auto !important;
            min-height: 140px !important;
        }}

        /* Result Card Grid Item Styling */
        .result-card {{
            background: var(--bg-card) !important;
            border: 1px solid var(--border-color) !important;
            border-radius: 12px !important;
            padding: 22px 24px !important;
            box-shadow: var(--card-shadow) !important;
            height: 100% !important;
            min-height: 100% !important;
            box-sizing: border-box !important;
            display: flex !important;
            flex-direction: column !important;
            justify-content: flex-start !important;
            flex: 1 1 auto !important;
        }}
        .card-header-row {{
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 0.85rem;
        }}
        .card-icon-box {{
            width: 32px;
            height: 32px;
            min-width: 32px;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: var(--bg-card-subtle);
            border: 1px solid var(--border-color);
        }}
        /* Center SVG icons perfectly in all icon box containers */
        .card-icon-box svg {{
            display: block !important;
            margin: 0 !important;
            flex-shrink: 0;
        }}
        .card-header-title {{
            font-size: 1rem;
            font-weight: 700;
            color: var(--text-primary) !important;
        }}
        .card-body-text {{
            font-size: 0.92rem;
            line-height: 1.5;
            color: var(--text-secondary) !important;
            margin-top: 0;
            margin-bottom: 0;
        }}
        .card-body-value {{
            font-size: 0.98rem;
            font-weight: 700;
            color: var(--text-primary) !important;
        }}
        .detail-list {{
            display: flex;
            flex-direction: column;
            gap: 12px;
        }}
        .detail-row {{
            display: flex;
            align-items: center;
            gap: 10px;
            font-size: 0.92rem;
            color: var(--text-primary) !important;
        }}
        .result-bullets {{
            color: var(--text-secondary) !important;
            margin-bottom: 0;
            padding-left: 1.1rem;
            font-size: 0.9rem;
            line-height: 1.55;
        }}
        .result-bullets li {{
            margin-bottom: 0.25rem;
        }}

        /* Button Customization */
        .stButton>button {{
            border-radius: 8px !important;
            font-weight: 600 !important;
            padding: 0.5rem 1.1rem !important;
            transition: all 0.15s ease !important;
            font-size: 0.9rem !important;
        }}
        .stButton>button[kind="primary"] {{
            background: var(--accent-blue) !important;
            color: #ffffff !important;
            border: none !important;
            box-shadow: 0 2px 6px rgba(2, 132, 199, 0.3) !important;
        }}
        .stButton>button[kind="primary"]:hover {{
            background: var(--accent-blue-hover) !important;
            transform: translateY(-1px) !important;
            box-shadow: 0 4px 12px rgba(2, 132, 199, 0.45) !important;
        }}
        .stButton>button[kind="secondary"] {{
            background: var(--bg-card) !important;
            color: var(--text-secondary) !important;
            border: 1px solid var(--border-color) !important;
        }}
        .stButton>button[kind="secondary"]:hover {{
            background: var(--bg-card-subtle) !important;
            border-color: var(--text-muted) !important;
            color: var(--text-primary) !important;
        }}

        /* Textarea & Input Fields */
        .stTextArea textarea, .stTextInput input, .stSelectbox select {{
            background-color: var(--bg-card) !important;
            color: var(--text-primary) !important;
            border: 1px solid var(--border-color) !important;
            border-radius: 8px !important;
            padding: 0.65rem 0.85rem !important;
            font-family: inherit !important;
            font-size: 0.92rem !important;
        }}
        /* Hide Streamlit Ctrl+Enter instruction overlay text completely */
        [data-testid="stTextArea"] [data-testid="stWidgetInstructions"],
        [data-testid="stTextArea"] small,
        .stTextArea [data-testid="stWidgetInstructions"],
        div[data-baseweb="textarea"] + div,
        div[data-baseweb="textarea"] ~ * {{
            display: none !important;
            visibility: hidden !important;
            height: 0 !important;
        }}
        .stTextArea textarea {{
            line-height: 1.5 !important;
            resize: vertical !important;
        }}
        .stTextArea textarea:focus, .stTextInput input:focus {{
            border-color: var(--accent-blue-light) !important;
            box-shadow: 0 0 0 2px rgba(56, 189, 248, 0.25) !important;
        }}

        /* Sidebar Styling */
        section[data-testid="stSidebar"] {{
            background-color: var(--bg-sidebar) !important;
            border-right: 1px solid var(--border-color) !important;
            width: 270px !important;
            overflow: hidden !important;
        }}
        section[data-testid="stSidebar"] > div:first-child {{
            overflow: hidden !important;
            height: 100% !important;
        }}
        [data-testid="stSidebarContent"] {{
            overflow: hidden !important;
        }}

        [data-testid="stSidebarContent"] {{
            display: flex !important;
            flex-direction: column !important;
            height: 100% !important;
            padding-top: 0.5rem !important;
            padding-left: 0.8rem !important;
            padding-right: 0.8rem !important;
            padding-bottom: 1rem !important;
            overflow-y: auto !important;
        }}
        [data-testid="stSidebarUserContent"],
        [data-testid="stSidebarUserContent"] > div,
        [data-testid="stSidebarUserContent"] [data-testid="stVerticalBlock"] {{
            display: contents !important;
        }}
        /* Hide unwanted horizontal rule lines below sign-out button */
        [data-testid="stSidebarUserContent"] hr,
        [data-testid="stSidebarUserContent"] [data-testid="stHorizontalBlock"] hr,
        [data-testid="stSidebarUserContent"] [data-testid="stMarkdownContainer"] hr,
        section[data-testid="stSidebar"] hr,
        section[data-testid="stSidebar"] [data-testid="stHorizontalRule"] {{
            display: none !important;
        }}
        /* Strip borders from sidebar element containers that cause thin line artifacts */
        section[data-testid="stSidebar"] [data-testid="stElementContainer"] {{
            border: none !important;
            outline: none !important;
            box-shadow: none !important;
        }}
        /* Hide completely empty stElementContainer dividers in sidebar */
        section[data-testid="stSidebar"] [data-testid="stElementContainer"]:not(:has(*)) {{
            display: none !important;
            height: 0 !important;
            margin: 0 !important;
            padding: 0 !important;
        }}
        /* Target Streamlit's stVerticalBlockBorderWrapper - the source of 2 thin border lines */
        section[data-testid="stSidebar"] [data-testid="stVerticalBlockBorderWrapper"],
        section[data-testid="stSidebar"] .stVerticalBlockBorderWrapper,
        section[data-testid="stSidebar"] [class*="VerticalBlock"],
        section[data-testid="stSidebar"] [class*="block-container"] {{
            border: none !important;
            border-top: none !important;
            border-bottom: none !important;
            outline: none !important;
            box-shadow: none !important;
        }}
        /* Hide any stray top-border rule Streamlit adds to stBottom element */
        section[data-testid="stSidebar"] [data-testid="stBottom"] {{
            border: none !important;
            display: none !important;
        }}
        /* Nuclear option: suppress ALL visible borders inside stSidebarUserContent children */
        [data-testid="stSidebarUserContent"] > * {{
            border-top: none !important;
            border-bottom: none !important;
        }}



        section[data-testid="stSidebar"] [data-testid="stLogo"],
        section[data-testid="stSidebar"] img[data-testid="stLogo"],
        section[data-testid="stSidebar"] [data-testid="stSidebarHeader"],
        section[data-testid="stSidebar"] [data-testid="stSidebarNavSeparator"] {{
            display: none !important;
        }}

        /* 1. Sidebar Top Branding Block */
        .sidebar-top-branding,
        div:has(> .sidebar-top-branding),
        div[data-testid="stElementContainer"]:has(.sidebar-top-branding) {{
            order: 1 !important;
            flex: 0 0 auto !important;
        }}

        /* 2. Middle Navigation Block - collapse height to fit items so it doesn't push bottom content */
        [data-testid="stSidebarNav"],
        [data-testid="stSidebarNav"] > div,
        [data-testid="stSidebarNav"] ul {{
            order: 2 !important;
            flex: 0 0 auto !important;
            flex-grow: 0 !important;
            height: auto !important;
            min-height: 0 !important;
            max-height: none !important;
            padding-top: 0.2rem !important;
        }}

        /* 3. Bottom Identity Badge Container */
        .sidebar-account-badge,
        div:has(> .sidebar-account-badge),
        div[data-testid="stElementContainer"]:has(.sidebar-account-badge) {{
            order: 3 !important;
            margin-top: auto !important;
            flex: 0 0 auto !important;
            padding-top: 0.6rem !important;
            margin-bottom: 0.75rem !important;
            box-sizing: border-box !important;
        }}

        /* 4. Bottom Logout Button Container */
        div[data-testid="stElementContainer"]:has(button[key="sidebar_logout_btn"]),
        div.stButton:has(> button[key="sidebar_logout_btn"]),
        div[data-testid="stElementContainer"]:has(.sidebar-account-badge) + div[data-testid="stElementContainer"],
        div[data-testid="stElementContainer"]:has(.sidebar-account-badge) + div.stButton {{
            order: 4 !important;
            flex: 0 0 auto !important;
            margin-top: 0 !important;
            padding-top: 0 !important;
            margin-bottom: 0.8rem !important;
            box-sizing: border-box !important;
        }}

        /* Sidebar Identity Badge Box Styling */
        .sidebar-account-badge {{
            width: 100%;
            box-sizing: border-box;
        }}

        .sidebar-user-badge {{
            padding: 0.55rem 0.75rem;
            border-radius: 8px;
            display: flex;
            flex-direction: column;
            gap: 3px;
            width: 100%;
            box-sizing: border-box;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.25);
        }}

        .sidebar-badge-header {{
            display: flex;
            align-items: center;
            gap: 6px;
            font-size: 0.82rem;
            line-height: 1.2;
        }}

        .sidebar-role-title {{
            font-size: 0.82rem;
            font-weight: 700;
        }}

        .sidebar-user-email {{
            font-size: 0.8rem;
            font-weight: 600;
            padding-left: 21px;
            word-break: break-all;
            overflow-wrap: anywhere;
            line-height: 1.25;
        }}

        /* Logout button styling inside sidebar */
        section[data-testid="stSidebar"] button[key="sidebar_logout_btn"] {{
            background: rgba(30, 41, 59, 0.6) !important;
            border: 1px solid var(--border-color) !important;
            color: var(--text-secondary) !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
            transition: all 0.15s ease !important;
        }}
        section[data-testid="stSidebar"] button[key="sidebar_logout_btn"]:hover {{
            background: rgba(239, 68, 68, 0.15) !important;
            border-color: rgba(239, 68, 68, 0.4) !important;
            color: #f87171 !important;
        }}

        /* Hide stray elements or dividers after the logout button */
        div[data-testid="stElementContainer"]:has(button[key="sidebar_logout_btn"]) ~ div,
        div[data-testid="stElementContainer"]:has(button[key="sidebar_logout_btn"]) ~ * {{
            display: none !important;
        }}

        /* Extra safety: hide any empty/near-empty stElementContainers inside sidebar user content */
        [data-testid="stSidebarUserContent"] [data-testid="stElementContainer"]:empty,
        section[data-testid="stSidebar"] [data-testid="stBottom"],
        section[data-testid="stSidebar"] [data-testid="stAppViewBlockContainer"] hr,
        section[data-testid="stSidebar"] [data-testid="stMainBlockContainer"] hr {{
            display: none !important;
        }}

        [data-testid="stSidebarNavSectionHeader"], 
        [data-testid="stSidebarNav"] span[data-testid="stHeader"],
        [data-testid="stSidebarNav"] h2 {{
            font-size: 0.72rem !important;
            font-weight: 700 !important;
            text-transform: uppercase !important;
            letter-spacing: 0.08em !important;
            color: var(--accent-blue-light) !important;
            margin-top: 1.1rem !important;
            margin-bottom: 0.35rem !important;
            padding-left: 0.4rem !important;
        }}
        [data-testid="stSidebarNavLink"],
        a[data-testid="stSidebarNavLink"] {{
            border-radius: 8px !important;
            padding: 0.6rem 0.85rem !important;
            transition: all 0.15s ease !important;
            text-decoration: none !important;
            margin-bottom: 0.25rem !important;
            display: flex !important;
            align-items: center !important;
            border: 1px solid transparent !important;
        }}
        [data-testid="stSidebarNavLink"] p,
        [data-testid="stSidebarNavLink"] span,
        a[data-testid="stSidebarNavLink"] p,
        a[data-testid="stSidebarNavLink"] span {{
            color: var(--text-secondary) !important;
            font-weight: 600 !important;
            font-size: 0.92rem !important;
        }}
        [data-testid="stSidebarNavLink"]:hover,
        a[data-testid="stSidebarNavLink"]:hover {{
            background-color: var(--bg-card-subtle) !important;
        }}
        [data-testid="stSidebarNavLink"]:hover p,
        [data-testid="stSidebarNavLink"]:hover span,
        a[data-testid="stSidebarNavLink"]:hover p,
        a[data-testid="stSidebarNavLink"]:hover span {{
            color: var(--text-primary) !important;
        }}
        [data-testid="stSidebarNavLink"][aria-current="page"],
        a[data-testid="stSidebarNavLink"][aria-current="page"] {{
            background: var(--accent-blue) !important;
            border-color: var(--accent-blue) !important;
        }}
        [data-testid="stSidebarNavLink"][aria-current="page"] p,
        [data-testid="stSidebarNavLink"][aria-current="page"] span,
        a[data-testid="stSidebarNavLink"][aria-current="page"] p,
        a[data-testid="stSidebarNavLink"][aria-current="page"] span {{
            color: #ffffff !important;
            font-weight: 700 !important;
        }}

        /* === Professional SVG Vector Icon System Integration for Sidebar Nav === */
        [data-testid="stSidebarNavLink"] [data-testid="stIconMaterial"],
        a[data-testid="stSidebarNavLink"] [data-testid="stIconMaterial"] {{
            display: none !important;
        }}

        [data-testid="stSidebarNavLink"]::before,
        a[data-testid="stSidebarNavLink"]::before {{
            content: "" !important;
            display: inline-block !important;
            width: 20px !important;
            height: 20px !important;
            min-width: 20px !important;
            min-height: 20px !important;
            margin-right: 10px !important;
            background-repeat: no-repeat !important;
            background-position: center !important;
            background-size: contain !important;
            flex-shrink: 0 !important;
            vertical-align: middle !important;
        }}

        /* === NAV ICON ASSIGNMENT ===
           Streamlit URLs: Submit Complaint="/", My Complaints="/My_Complaints",
           About="/About", Dashboard="/Dashboard"
           ================================================================= */

        /* Default (fallback) = file-plus for Submit Complaint (href="/") */
        [data-testid="stSidebarNavLink"]::before,
        a[data-testid="stSidebarNavLink"]::before {{
            background-image: url("{file_plus_svg_cyan}") !important;
        }}
        [data-testid="stSidebarNavLink"][aria-current="page"]::before,
        [data-testid="stSidebarNavLink"]:hover::before {{
            background-image: url("{file_plus_svg_white}") !important;
        }}

        /* My Complaints (file-text icon) — exact Streamlit URL: /My_Complaints */
        a[data-testid="stSidebarNavLink"][href*="My_Complaints"]::before {{
            background-image: url("{file_svg_cyan}") !important;
        }}
        a[data-testid="stSidebarNavLink"][href*="My_Complaints"][aria-current="page"]::before,
        a[data-testid="stSidebarNavLink"][href*="My_Complaints"]:hover::before {{
            background-image: url("{file_svg_white}") !important;
        }}

        /* Municipal Dashboard (dashboard icon) — exact Streamlit URL: /Dashboard */
        a[data-testid="stSidebarNavLink"][href*="Dashboard"]::before {{
            background-image: url("{dashboard_svg_cyan}") !important;
        }}
        a[data-testid="stSidebarNavLink"][href*="Dashboard"][aria-current="page"]::before,
        a[data-testid="stSidebarNavLink"][href*="Dashboard"]:hover::before {{
            background-image: url("{dashboard_svg_white}") !important;
        }}

        /* About (info-circle icon) — exact Streamlit URL: /About
           Listed LAST so it wins cascade over the default fallback above. */
        a[data-testid="stSidebarNavLink"][href*="About"]::before {{
            background-image: url("{info_svg_cyan}") !important;
        }}
        a[data-testid="stSidebarNavLink"][href*="About"][aria-current="page"]::before,
        a[data-testid="stSidebarNavLink"][href*="About"]:hover::before {{
            background-image: url("{info_svg_white}") !important;
        }}


        /* Sidebar Branding Header */
        .sidebar-brand-header {{
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 0.75rem 0.25rem 1rem 0.25rem;
            margin-bottom: 0.75rem;
            border-bottom: 1px solid var(--border-color);
        }}
        .sidebar-logo-wrapper {{
            width: 42px;
            height: 42px;
            min-width: 42px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: var(--bg-card);
            border-radius: 10px;
            border: 1px solid var(--border-color);
            padding: 4px;
        }}
        .sidebar-logo-img {{
            width: 100% !important;
            height: 100% !important;
            border-radius: 6px !important;
            object-fit: cover !important;
            display: block !important;
        }}
        .sidebar-title-wrapper {{
            display: flex;
            flex-direction: column;
            justify-content: center;
        }}
        .brand-title {{
            color: var(--text-primary) !important;
            font-size: 1.1rem !important;
            font-weight: 700 !important;
            line-height: 1.15 !important;
            letter-spacing: -0.01em !important;
        }}
        .brand-subtitle {{
            color: var(--text-muted) !important;
            font-size: 0.85rem !important;
            font-weight: 600 !important;
            line-height: 1.15 !important;
        }}

        /* Sidebar Page Links */
        section[data-testid="stSidebar"] a[data-testid="stPageLink-nav"],
        section[data-testid="stSidebar"] div[data-testid="stSidebarUserContent"] a {{
            border-radius: 8px !important;
            padding: 0.6rem 0.85rem !important;
            transition: all 0.15s ease !important;
            text-decoration: none !important;
            margin-bottom: 0.25rem !important;
            display: flex !important;
            align-items: center !important;
            border: 1px solid transparent;
        }}
        section[data-testid="stSidebar"] .sidebar-nav-container a,
        section[data-testid="stSidebar"] .sidebar-nav-container p,
        section[data-testid="stSidebar"] .sidebar-nav-container span,
        section[data-testid="stSidebar"] [data-testid="stPageLink-nav"] p,
        section[data-testid="stSidebar"] [data-testid="stPageLink-nav"] span,
        section[data-testid="stSidebar"] a[data-testid="stPageLink-nav"] p,
        section[data-testid="stSidebar"] a[data-testid="stPageLink-nav"] span {{
            color: var(--text-secondary) !important;
            font-weight: 600 !important;
            font-size: 0.92rem !important;
        }}
        section[data-testid="stSidebar"] [data-testid="stPageLink-nav"]:hover,
        section[data-testid="stSidebar"] a[data-testid="stPageLink-nav"]:hover {{
            background-color: var(--bg-card-subtle) !important;
        }}
        section[data-testid="stSidebar"] [data-testid="stPageLink-nav"]:hover p,
        section[data-testid="stSidebar"] [data-testid="stPageLink-nav"]:hover span,
        section[data-testid="stSidebar"] a[data-testid="stPageLink-nav"]:hover p,
        section[data-testid="stSidebar"] a[data-testid="stPageLink-nav"]:hover span {{
            color: var(--text-primary) !important;
        }}
        section[data-testid="stSidebar"] [data-testid="stPageLink-nav"][aria-current="page"],
        section[data-testid="stSidebar"] a[data-testid="stPageLink-nav"][aria-current="page"] {{
            background: var(--accent-blue) !important;
            border-color: var(--accent-blue) !important;
        }}
        section[data-testid="stSidebar"] [data-testid="stPageLink-nav"][aria-current="page"] p,
        section[data-testid="stSidebar"] [data-testid="stPageLink-nav"][aria-current="page"] span,
        section[data-testid="stSidebar"] a[data-testid="stPageLink-nav"][aria-current="page"] p,
        section[data-testid="stSidebar"] a[data-testid="stPageLink-nav"][aria-current="page"] span {{
            color: #ffffff !important;
            font-weight: 700 !important;
        }}

        .sidebar-section-header {{
            font-size: 0.72rem !important;
            font-weight: 700 !important;
            text-transform: uppercase !important;
            letter-spacing: 0.08em !important;
            color: var(--accent-blue-light) !important;
            margin-top: 1.1rem !important;
            margin-bottom: 0.35rem !important;
            padding-left: 0.4rem !important;
        }}

        /* Dataframe Overrides */
        [data-testid="stDataFrame"] {{
            border-radius: 8px !important;
            border: 1px solid var(--border-color) !important;
            overflow: hidden !important;
        }}

        /* Disclaimer Footer Box */
        .disclaimer-box {{
            display: flex;
            align-items: center;
            gap: 8px;
            background: var(--bg-card-subtle);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 0.6rem 0.9rem;
            font-size: 0.82rem;
            color: var(--text-muted);
            margin-top: 1.2rem;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )
    render_sidebar_branding()


STATUS_CITIZEN_EXPLANATIONS = {
    "Pending": "Your complaint has been submitted and is awaiting municipal review.",
    "Assigned": "Your complaint has been assigned to the municipal team for follow-up.",
    "In Progress": "Your complaint is currently being handled by the municipal team.",
    "Resolved": "Your complaint has been marked as resolved.",
}


def get_citizen_status_explanation(status: str) -> str:
    """Return concise citizen-friendly status explanation string."""
    return STATUS_CITIZEN_EXPLANATIONS.get(
        str(status).strip(),
        "Your complaint status is currently being tracked by the municipal team."
    )


def get_status_badge_html(text: str) -> str:
    """Return HTML string for a status badge with SVG vector icons."""
    val_lower = str(text).lower().strip()
    icon_color = "#38bdf8"

    if val_lower in ("urgent",):
        css_cls = "badge-urgent"
        svg = get_icon_svg("alert-triangle", color="#f87171", size=14)
    elif val_lower in ("high",):
        css_cls = "badge-high"
        svg = get_icon_svg("alert-triangle", color="#fb923c", size=14)
    elif val_lower in ("medium", "pending"):
        css_cls = "badge-medium"
        svg = get_icon_svg("clock", color="#fbbf24", size=14)
    elif val_lower in ("low", "assigned"):
        css_cls = "badge-low"
        svg = get_icon_svg("user", color="#38bdf8", size=14)
    elif val_lower in ("in progress",):
        css_cls = "badge-low"
        svg = get_icon_svg("clock", color="#38bdf8", size=14)
    elif val_lower in ("resolved",):
        css_cls = "badge-low"
        svg = get_icon_svg("check-circle", color="#34d399", size=14)
    elif val_lower in ("unclear",):
        css_cls = "badge-unclear"
        svg = get_icon_svg("info", color="#94a3b8", size=14)
    else:
        css_cls = "badge-info"
        svg = get_icon_svg("water", color=icon_color, size=14)
    return f'<span class="badge {css_cls}">{svg}{text}</span>'

