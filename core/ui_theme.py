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


def render_sidebar_branding():
    """Render website logo, branding title block, and navigation in sidebar."""
    st.session_state["theme"] = "dark"

    logo_b64 = get_logo_base64()
    accent_color = "#38bdf8"
    logo_html = (
        f'<img src="{logo_b64}" class="sidebar-logo-img" alt="Water Grievance Logo"/>'
        if logo_b64
        else get_icon_svg("water", color=accent_color, size=32)
    )

    st.sidebar.markdown(
        f"""
        <div class="sidebar-brand-header">
            <div class="sidebar-logo-wrapper">
                {logo_html}
            </div>
            <div class="sidebar-title-wrapper">
                <div class="brand-title">Water</div>
                <div class="brand-subtitle">Grievance Analyzer</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Render custom navigation links with vector SVG icons
    st.sidebar.markdown('<div class="sidebar-nav-container">', unsafe_allow_html=True)
    st.sidebar.page_link("app.py", label="Dashboard")
    st.sidebar.page_link("pages/1_Analyze_Complaint.py", label="Analyze Complaint")
    st.sidebar.page_link("pages/2_Review_History.py", label="History")
    st.sidebar.page_link("pages/3_About.py", label="About")
    st.sidebar.markdown('</div>', unsafe_allow_html=True)


def apply_custom_theme():
    """Inject municipal civic-tech CSS styling for a clean, professional Dark background theme."""
    st.session_state["theme"] = "dark"

    nav_icon_color = "#38bdf8"
    nav_active_color = "#ffffff"

    home_svg = get_svg_data_uri("home", color=nav_icon_color, size=18)
    home_active = get_svg_data_uri("home", color=nav_active_color, size=18)
    search_svg = get_svg_data_uri("search", color=nav_icon_color, size=18)
    search_active = get_svg_data_uri("search", color=nav_active_color, size=18)
    file_svg = get_svg_data_uri("file-text", color=nav_icon_color, size=18)
    file_active = get_svg_data_uri("file-text", color=nav_active_color, size=18)
    info_svg = get_svg_data_uri("info", color=nav_icon_color, size=18)
    info_active = get_svg_data_uri("info", color=nav_active_color, size=18)

    theme_variables = """
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
        [data-testid="stColumn"] [data-testid="stVerticalBlock"],
        [data-testid="stColumn"] [data-testid="stElementContainer"],
        [data-testid="stColumn"] [data-testid="stMarkdownContainer"],
        [data-testid="stColumn"] .stMarkdown,
        [data-testid="stColumn"] .stMarkdown > div {{
            height: 100% !important;
            display: flex !important;
            flex-direction: column !important;
            flex: 1 1 auto !important;
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
        .stTextArea textarea:focus, .stTextInput input:focus {{
            border-color: var(--accent-blue-light) !important;
            box-shadow: 0 0 0 2px rgba(56, 189, 248, 0.25) !important;
        }}

        /* Sidebar Styling */
        section[data-testid="stSidebar"] {{
            background-color: var(--bg-sidebar) !important;
            border-right: 1px solid var(--border-color) !important;
            width: 270px !important;
        }}
        [data-testid="stSidebarContent"] {{
            display: flex;
            flex-direction: column;
            padding-top: 0.5rem;
            padding-left: 0.8rem;
            padding-right: 0.8rem;
        }}
        [data-testid="stSidebarUserContent"] {{
            order: -1;
        }}
        section[data-testid="stSidebar"] nav,
        section[data-testid="stSidebar"] [data-testid="stSidebarNav"],
        section[data-testid="stSidebar"] [data-testid="stSidebarNavItems"],
        section[data-testid="stSidebar"] [data-testid="stLogo"],
        section[data-testid="stSidebar"] img[data-testid="stLogo"],
        section[data-testid="stSidebar"] [data-testid="stSidebarHeader"],
        section[data-testid="stSidebar"] [data-testid="stSidebarNavSeparator"] {{
            display: none !important;
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

        /* Sidebar Nav SVG Icons */
        .sidebar-nav-container div.element-container:nth-of-type(1) a p::before,
        .sidebar-nav-container > div:nth-child(1) a p::before,
        section[data-testid="stSidebar"] a[href="/"] p::before,
        section[data-testid="stSidebar"] a[href="./"] p::before,
        section[data-testid="stSidebar"] a[href=""] p::before,
        section[data-testid="stSidebar"] a[href*="app"] p::before {{
            content: "" !important;
            display: inline-block !important;
            width: 18px !important;
            height: 18px !important;
            min-width: 18px !important;
            margin-right: 10px !important;
            vertical-align: middle !important;
            background-repeat: no-repeat !important;
            background-size: contain !important;
            background-image: url("{home_svg}") !important;
        }}
        .sidebar-nav-container div.element-container:nth-of-type(1) a:hover p::before,
        .sidebar-nav-container div.element-container:nth-of-type(1) a[aria-current="page"] p::before,
        .sidebar-nav-container > div:nth-child(1) a:hover p::before,
        .sidebar-nav-container > div:nth-child(1) a[aria-current="page"] p::before,
        section[data-testid="stSidebar"] a[href="/"]:hover p::before,
        section[data-testid="stSidebar"] a[href="/"][aria-current="page"] p::before,
        section[data-testid="stSidebar"] a[href="./"]:hover p::before,
        section[data-testid="stSidebar"] a[href="./"][aria-current="page"] p::before,
        section[data-testid="stSidebar"] a[href*="app"]:hover p::before,
        section[data-testid="stSidebar"] a[href*="app"][aria-current="page"] p::before {{
            background-image: url("{home_active}") !important;
        }}

        .sidebar-nav-container div.element-container:nth-of-type(2) a p::before,
        .sidebar-nav-container > div:nth-child(2) a p::before,
        section[data-testid="stSidebar"] a[href*="Analyze_Complaint"] p::before {{
            content: "" !important;
            display: inline-block !important;
            width: 18px !important;
            height: 18px !important;
            min-width: 18px !important;
            margin-right: 10px !important;
            vertical-align: middle !important;
            background-repeat: no-repeat !important;
            background-size: contain !important;
            background-image: url("{search_svg}") !important;
        }}
        .sidebar-nav-container div.element-container:nth-of-type(2) a:hover p::before,
        .sidebar-nav-container div.element-container:nth-of-type(2) a[aria-current="page"] p::before,
        .sidebar-nav-container > div:nth-child(2) a:hover p::before,
        .sidebar-nav-container > div:nth-child(2) a[aria-current="page"] p::before,
        section[data-testid="stSidebar"] a[href*="Analyze_Complaint"]:hover p::before,
        section[data-testid="stSidebar"] a[href*="Analyze_Complaint"][aria-current="page"] p::before {{
            background-image: url("{search_active}") !important;
        }}

        .sidebar-nav-container div.element-container:nth-of-type(3) a p::before,
        .sidebar-nav-container > div:nth-child(3) a p::before,
        section[data-testid="stSidebar"] a[href*="Review_History"] p::before {{
            content: "" !important;
            display: inline-block !important;
            width: 18px !important;
            height: 18px !important;
            min-width: 18px !important;
            margin-right: 10px !important;
            vertical-align: middle !important;
            background-repeat: no-repeat !important;
            background-size: contain !important;
            background-image: url("{file_svg}") !important;
        }}
        .sidebar-nav-container div.element-container:nth-of-type(3) a:hover p::before,
        .sidebar-nav-container div.element-container:nth-of-type(3) a[aria-current="page"] p::before,
        .sidebar-nav-container > div:nth-child(3) a:hover p::before,
        .sidebar-nav-container > div:nth-child(3) a[aria-current="page"] p::before,
        section[data-testid="stSidebar"] a[href*="Review_History"]:hover p::before,
        section[data-testid="stSidebar"] a[href*="Review_History"][aria-current="page"] p::before {{
            background-image: url("{file_active}") !important;
        }}

        .sidebar-nav-container div.element-container:nth-of-type(4) a p::before,
        .sidebar-nav-container > div:nth-child(4) a p::before,
        section[data-testid="stSidebar"] a[href*="About"] p::before {{
            content: "" !important;
            display: inline-block !important;
            width: 18px !important;
            height: 18px !important;
            min-width: 18px !important;
            margin-right: 10px !important;
            vertical-align: middle !important;
            background-repeat: no-repeat !important;
            background-size: contain !important;
            background-image: url("{info_svg}") !important;
        }}
        .sidebar-nav-container div.element-container:nth-of-type(4) a:hover p::before,
        .sidebar-nav-container div.element-container:nth-of-type(4) a[aria-current="page"] p::before,
        .sidebar-nav-container > div:nth-child(4) a:hover p::before,
        .sidebar-nav-container > div:nth-child(4) a[aria-current="page"] p::before,
        section[data-testid="stSidebar"] a[href*="About"]:hover p::before,
        section[data-testid="stSidebar"] a[href*="About"][aria-current="page"] p::before {{
            background-image: url("{info_active}") !important;
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
    elif val_lower in ("medium",):
        css_cls = "badge-medium"
        svg = get_icon_svg("info", color="#fbbf24", size=14)
    elif val_lower in ("low",):
        css_cls = "badge-low"
        svg = get_icon_svg("check-circle", color="#38bdf8", size=14)
    elif val_lower in ("unclear",):
        css_cls = "badge-unclear"
        svg = get_icon_svg("info", color="#94a3b8", size=14)
    else:
        css_cls = "badge-info"
        svg = get_icon_svg("water", color=icon_color, size=14)
    return f'<span class="badge {css_cls}">{svg}{text}</span>'
