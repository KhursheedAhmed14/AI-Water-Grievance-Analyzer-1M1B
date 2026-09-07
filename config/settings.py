"""
config/settings.py
Loads watsonx.ai credentials from the .env file and exposes them as
module-level constants.  Import this module wherever credentials are needed.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).parent.parent
LOGO_PATH = str(PROJECT_ROOT / "assets" / "water_grievance_logo.png")

# Always reload environment variables from .env if updated
load_dotenv(override=True)

WATSONX_API_KEY: str = os.getenv("WATSONX_API_KEY", "")
WATSONX_PROJECT_ID: str = os.getenv("WATSONX_PROJECT_ID", "")
WATSONX_URL: str = os.getenv("WATSONX_URL", "")
WATSONX_MODEL_ID: str = os.getenv("WATSONX_MODEL_ID", "")


def get_credentials():
    load_dotenv(override=True)
    return (
        os.getenv("WATSONX_API_KEY", ""),
        os.getenv("WATSONX_PROJECT_ID", ""),
        os.getenv("WATSONX_URL", ""),
        os.getenv("WATSONX_MODEL_ID", ""),
    )


def credentials_configured() -> bool:
    """Return True only when all three watsonx.ai credentials are non-empty."""
    api_key, project_id, url, _ = get_credentials()
    return bool(api_key and project_id and url)
