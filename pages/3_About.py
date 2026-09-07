"""
pages/3_About.py
About page for the AI-Powered Water Grievance Analyzer.
"""

import pandas as pd
import streamlit as st

from core.ui_icons import get_icon_svg
from core.ui_theme import LOGO_PATH, apply_custom_theme

st.set_page_config(
    page_title="About - Water Grievance Analyzer",
    page_icon=LOGO_PATH,
    layout="wide",
)

apply_custom_theme()

icon_accent = "#38bdf8"

st.markdown(
    f"## {get_icon_svg('info', color=icon_accent, size=24)} About the Project",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='font-size: 1rem; color: var(--text-secondary); margin-bottom: 1.5rem;'>"
    "The <strong>AI-Powered Water Grievance Analyzer</strong> is an intelligent municipal decision-support system "
    "designed to triage and analyze citizen water complaints in alignment with UN Sustainable Development Goal 6."
    "</p>",
    unsafe_allow_html=True,
)

st.divider()

# ── Problem & Solution Grid ───────────────────────────────────────────────────
col_prob, col_sol = st.columns(2)

with col_prob:
    st.markdown(
        f"""
        <div class="content-card" style="height: 100%;">
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 0.8rem;">
                <div class="card-icon-box">{get_icon_svg("target", color=icon_accent, size=18)}</div>
                <h3 style="margin: 0; font-size: 1.1rem;">Problem Statement</h3>
            </div>
            <p style="color: var(--text-secondary); line-height: 1.6; font-size: 0.92rem;">
                Citizens submit urgent water complaints (pipeline leaks, contamination, supply outages, low pressure) in free-form, unstructured natural language.
            </p>
            <ul style="color: var(--text-secondary); padding-left: 1.2rem; line-height: 1.6; font-size: 0.9rem;">
                <li>Manual review is slow and error-prone during supply crises.</li>
                <li>Critical details like location or affected population get buried in long texts.</li>
                <li>Urgent infrastructure failures risk delayed municipal response.</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col_sol:
    st.markdown(
        f"""
        <div class="content-card" style="height: 100%;">
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 0.8rem;">
                <div class="card-icon-box">{get_icon_svg("sparkles", color=icon_accent, size=18)}</div>
                <h3 style="margin: 0; font-size: 1.1rem;">The AI Solution</h3>
            </div>
            <p style="color: var(--text-secondary); line-height: 1.6; font-size: 0.92rem;">
                Leveraging <strong>IBM Granite on watsonx.ai</strong>, our solution automatically extracts structured insights from raw citizen feedback.
            </p>
            <ul style="color: var(--text-secondary); padding-left: 1.2rem; line-height: 1.6; font-size: 0.9rem;">
                <li>Instant issue classification into standard municipal categories.</li>
                <li>Severity rating and AI priority recommendations for fast triage.</li>
                <li>Automated extraction of duration, location, affected count, and key facts.</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)

# ── How AI Works Section ──────────────────────────────────────────────────────
st.markdown(
    f"### {get_icon_svg('cpu', color=icon_accent, size=20)} How the AI Analysis Works",
    unsafe_allow_html=True,
)

st.markdown(
    f"""
    <div class="content-card">
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 1.2rem;">
            <div>
                <h4 style="color: var(--text-primary); margin-bottom: 0.3rem; font-size: 0.95rem;">1. Citizen Input</h4>
                <p style="color: var(--text-secondary); font-size: 0.88rem; margin: 0;">Raw complaint text submitted via municipal portal or hotline.</p>
            </div>
            <div>
                <h4 style="color: var(--text-primary); margin-bottom: 0.3rem; font-size: 0.95rem;">2. IBM Granite Model</h4>
                <p style="color: var(--text-secondary); font-size: 0.88rem; margin: 0;">Model processes text through specialized municipal prompt instructions.</p>
            </div>
            <div>
                <h4 style="color: var(--text-primary); margin-bottom: 0.3rem; font-size: 0.95rem;">3. Safe Parsing</h4>
                <p style="color: var(--text-secondary); font-size: 0.88rem; margin: 0;">Response parser validates JSON output, enums, and key facts array.</p>
            </div>
            <div>
                <h4 style="color: var(--text-primary); margin-bottom: 0.3rem; font-size: 0.95rem;">4. SQLite Storage</h4>
                <p style="color: var(--text-secondary); font-size: 0.88rem; margin: 0;">Analysis is persisted for auditability and municipal review history.</p>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.divider()

# ── UN SDG 6 Alignment ────────────────────────────────────────────────────────
st.markdown(
    f"### {get_icon_svg('water', color=icon_accent, size=20)} UN SDG 6 Alignment",
    unsafe_allow_html=True,
)
st.markdown(
    """
    <div class="content-card" style="border-left: 4px solid var(--accent-blue);">
        <h4 style="color: var(--text-primary); margin-bottom: 0.5rem; font-size: 1rem;">Target 6.1 & Target 6.B — Clean Water & Sanitation</h4>
        <p style="color: var(--text-secondary); line-height: 1.6; margin-bottom: 0; font-size: 0.92rem;">
            Ensuring availability and sustainable management of water requires rapid, transparent resolution of distribution failures. By accelerating municipal response times to leaks and disruptions, this tool directly supports community participation and sustainable water management.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.divider()

# ── Technology Stack ──────────────────────────────────────────────────────────
st.markdown(
    f"### {get_icon_svg('layer', color=icon_accent, size=20)} Technology Stack",
    unsafe_allow_html=True,
)

tech_data = {
    "Layer": [
        "Language Model",
        "AI Platform",
        "SDK",
        "Backend / App",
        "Storage",
        "Data Processing",
    ],
    "Technology": [
        "IBM Granite (or Llama 3.3 Instruct on watsonx)",
        "IBM watsonx.ai (IBM Cloud)",
        "ibm-watsonx-ai Python SDK",
        "Python 3.9+ & Streamlit",
        "SQLite 3",
        "Pandas & JSON Schema Validation",
    ],
    "Role": [
        "Zero-shot complaint analysis & detail extraction",
        "Managed foundation model inference infrastructure",
        "Secure API authentication and text generation",
        "Interactive web dashboard and workflow management",
        "Persistent local complaint log & audit history",
        "Data transformation and tabular aggregation",
    ],
}

st.table(pd.DataFrame(tech_data))

st.divider()

# ── Responsible AI ────────────────────────────────────────────────────────────
st.markdown(
    f"### {get_icon_svg('shield-check', color=icon_accent, size=20)} Responsible AI & Governance",
    unsafe_allow_html=True,
)
st.markdown(
    """
    <div class="content-card">
        <ul style="color: var(--text-secondary); line-height: 1.7; margin-bottom: 0; font-size: 0.9rem;">
            <li><strong>Human-in-the-Loop:</strong> All AI ratings are advisory recommendations. Municipal authorities retain full decision-making authority.</li>
            <li><strong>Strict Hallucination Prevention:</strong> Prompts strictly forbid inventing details not present in citizen text. Unstated fields are labeled as <em>Unclear</em>.</li>
            <li><strong>Missing Info Warning:</strong> Highlights missing critical data (e.g. missing street address) to avoid improper dispatch.</li>
            <li><strong>Data Privacy & Security:</strong> Local SQLite storage ensures citizen record privacy without external telemetry.</li>
        </ul>
    </div>
    """,
    unsafe_allow_html=True,
)

st.caption("Developed for 1M1B AI for Sustainability Virtual Internship in collaboration with IBM SkillsBuild.")