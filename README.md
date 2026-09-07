# AI-Powered Water Grievance Analyzer

> **SDG 6** — Ensure availability and sustainable management of water and sanitation for all.

A Python/Streamlit prototype that accepts unstructured citizen water-related complaints, sends them to IBM's `ibm/granite-3-8b-instruct` model via the `ibm-watsonx-ai` SDK, and returns structured analysis for municipal human review. Every analysis result is persisted in a local SQLite database.

---

## Project Overview

Municipal water authorities receive a high volume of unstructured citizen complaints (leaks, contamination, billing errors, access issues, etc.). This tool uses IBM Granite — a large language model hosted on IBM watsonx.ai — to automatically:

- **Summarise** the complaint in one plain-English sentence
- **Classify** it into one of five categories: Pipeline Leakage, Pipeline Failure, Water Supply Disruption, Low Water Pressure, or Other / Unclear
- **Assess severity**: Low, Medium, or High
- **Recommend a priority**: Low, Medium, High, or Urgent
- **Extract key facts**: location, duration, number of affected people
- **Identify missing information** that would help resolve the complaint

> ⚠️ **All AI outputs are recommendations only.** Final decisions must always be made by a qualified municipal authority.

---

## SDG 6 Context

**UN Sustainable Development Goal 6** calls for clean water and sanitation for all people by 2030. Efficient triage of citizen complaints about water services is one concrete step toward that goal — ensuring that the most severe issues are escalated quickly and that no complaint is lost in an unmanaged inbox.

---

## Prerequisites

- **Python 3.9 or later**
- **IBM Cloud account** with access to IBM watsonx.ai (a free trial is sufficient)
- `pip` for package installation

---

## IBM watsonx.ai Setup

You will need three pieces of information from IBM Cloud:

1. **API Key**
   - Log in to [IBM Cloud](https://cloud.ibm.com)
   - Go to **Manage → Access (IAM) → API keys**
   - Click **Create an IBM Cloud API key**, give it a name, and copy the key value immediately (it is only shown once)

2. **Project ID**
   - Open [watsonx.ai](https://dataplatform.cloud.ibm.com/wx/home)
   - Create a project (or open an existing one)
   - Go to **Manage → General** inside the project
   - Copy the **Project ID** shown under "General"

3. **Regional URL**
   - Use the URL that matches the region where your watsonx.ai instance is provisioned
   - Common values:
     - `https://us-south.ml.cloud.ibm.com` (Dallas)
     - `https://eu-de.ml.cloud.ibm.com` (Frankfurt)
     - `https://jp-tok.ml.cloud.ibm.com` (Tokyo)

---

## Installation

```bash
# 1. Clone the repository
git clone https://github.com/your-username/AI-Water-Grievance-Analyzer.git
cd AI-Water-Grievance-Analyzer

# 2. Create and activate a virtual environment (recommended)
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure credentials
cp .env.example .env
# Edit .env and fill in WATSONX_API_KEY, WATSONX_PROJECT_ID, WATSONX_URL

# 5. Run the app
streamlit run app.py
```

The app will open at `http://localhost:8501` in your browser.

---

## Project Structure

```
AI-Water-Grievance-Analyzer/
├── app.py                        # Streamlit entry point (multi-page router)
├── pages/
│   ├── 1_Analyze_Complaint.py    # Submit & analyze a complaint
│   ├── 2_Review_History.py       # Browse past analyses from SQLite
│   └── 3_About.py                # SDG 6 context, project info, disclaimer
├── core/
│   ├── __init__.py
│   ├── granite_client.py         # ibm-watsonx-ai SDK wrapper
│   ├── prompt_builder.py         # Builds the structured prompt sent to Granite
│   ├── response_parser.py        # Parses / validates Granite's JSON response
│   └── database.py               # SQLite schema, insert, and query helpers
├── config/
│   └── settings.py               # Reads env vars; exposes typed config constants
├── data/
│   └── grievances.db             # SQLite database (created automatically at runtime)
├── .env.example                  # Template showing required env var names
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

---

## Disclaimer

This application is a **prototype** developed for educational and research purposes as part of the 1 Million 1 Billion (1M1B) AI for Sustainability Virtual Internship in collaboration with IBM SkillsBuild.

- AI-generated outputs are recommendations only and do not constitute official decisions.
- The tool does not store any personally identifiable information beyond the complaint text provided.
- It is not intended for production deployment without further security review, authentication, and validation.
- The developers make no warranty as to the accuracy of any AI-generated analysis.
