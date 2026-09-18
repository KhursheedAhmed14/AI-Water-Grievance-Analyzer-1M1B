"""
app.py
Main Entry Point & Dynamic Navigation Router for AI-Powered Water Grievance Analyzer.
Leverages Streamlit st.navigation and st.Page for dynamic role-based access control.
"""

import streamlit as st

from core.auth import get_current_role
from core.database import ensure_db_initialized
from core.landing import page_landing
from core.ui_theme import LOGO_PATH, apply_custom_theme, render_sidebar_account

# Global Page Config
st.set_page_config(
    page_title="AI-Powered Water Grievance Analyzer",
    page_icon=LOGO_PATH,
    layout="wide",
)

# Initialize Database & Theme (ensure_db_initialized is cached via @st.cache_resource)
ensure_db_initialized()
apply_custom_theme()



# ── Define Streamlit Pages ────────────────────────────────────────────────────
page_citizen_login = st.Page("pages/3_Citizen_Login.py", title="Citizen Login")
page_municipal_login = st.Page("pages/4_Municipal_Login.py", title="Municipal Login")

page_municipal_dashboard = st.Page("pages/5_Municipal_Dashboard.py", title="Dashboard", icon=":material/dashboard:")
page_submit_complaint = st.Page("pages/1_Submit_Complaint.py", title="Submit Complaint", icon=":material/description:")
page_my_complaints = st.Page("pages/2_My_Complaints.py", title="My Complaints", icon=":material/history:")

page_about = st.Page("pages/6_About.py", title="About", icon=":material/info:")


# ── Construct Role-Based Navigation Menu ─────────────────────────────────────
current_role = get_current_role()

if current_role == "citizen":
    nav_structure = {
        "CITIZEN PORTAL": [page_submit_complaint, page_my_complaints],
        "INFO": [page_about],
    }
    pg = st.navigation(nav_structure, position="sidebar")
elif current_role == "municipal":
    nav_structure = {
        "MUNICIPAL PORTAL": [page_municipal_dashboard],
        "INFO": [page_about],
    }
    pg = st.navigation(nav_structure, position="sidebar")
else:
    nav_structure = [page_landing, page_citizen_login, page_municipal_login]
    pg = st.navigation(nav_structure, position="hidden")

pg.run()
render_sidebar_account()

