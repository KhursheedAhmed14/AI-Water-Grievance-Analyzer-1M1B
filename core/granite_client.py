"""
core/granite_client.py
IBM watsonx.ai SDK wrapper for IBM Granite / watsonx models.
ModelInference is instantiated lazily (inside the function) so that importing
this module never triggers an API connection.
"""

from __future__ import annotations

# Cached working model ID across calls
_CACHED_MODEL_ID: str | None = None

# Ordered model candidates tailored for watsonx regions (au-syd, us-south, eu-de, etc.)
DEFAULT_MODEL_CANDIDATES = [
    "meta-llama/llama-3-3-70b-instruct",
    "ibm/granite-3-8b-instruct",
    "ibm/granite-3-1-8b-base",
    "meta-llama/llama-3-1-8b",
]


def _get_working_model(credentials, project_id: str, params: dict, prompt: str) -> str:
    """
    Attempt to run generation with candidate models and return the first working raw response.
    Automatically caches the successfully working model ID.
    """
    global _CACHED_MODEL_ID
    from config.settings import get_credentials
    from ibm_watsonx_ai.foundation_models import ModelInference

    _, _, _, watsonx_model_id = get_credentials()

    candidates = []
    if watsonx_model_id:
        candidates.append(watsonx_model_id)
    if _CACHED_MODEL_ID and _CACHED_MODEL_ID not in candidates:
        candidates.append(_CACHED_MODEL_ID)

    for candidate in DEFAULT_MODEL_CANDIDATES:
        if candidate not in candidates:
            candidates.append(candidate)

    last_exception = None
    for model_id in candidates:
        try:
            model = ModelInference(
                model_id=model_id,
                credentials=credentials,
                project_id=project_id,
                params=params,
            )
            response: str = model.generate_text(prompt=prompt)
            _CACHED_MODEL_ID = model_id
            return response
        except Exception as exc:
            last_exception = exc
            err_str = str(exc).lower()
            if "not supported for this environment" in err_str or "not supported" in err_str or "400" in err_str:
                continue
            else:
                raise

    raise RuntimeError(f"Granite API call failed with all candidate models: {last_exception}")


def analyze_complaint(text: str) -> str:
    """
    Send *text* to IBM Granite / watsonx model via watsonx.ai and return the raw response string.

    The prompt is constructed by core.prompt_builder.build_prompt().
    Credentials are read from config.settings at call time.

    Raises:
        RuntimeError: if credentials are not configured or the API call fails.
    """
    from config.settings import get_credentials
    from core.prompt_builder import build_prompt

    api_key, project_id, url, _ = get_credentials()

    if not (api_key and project_id and url):
        raise RuntimeError(
            "watsonx.ai credentials are not configured. "
            "Set WATSONX_API_KEY, WATSONX_PROJECT_ID, and WATSONX_URL in your .env file."
        )

    try:
        from ibm_watsonx_ai import Credentials
        from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as Params

        credentials = Credentials(url=url, api_key=api_key)

        params = {
            Params.MAX_NEW_TOKENS: 512,
            Params.TEMPERATURE: 0,
            Params.DECODING_METHOD: "greedy",
        }

        prompt = build_prompt(text)
        return _get_working_model(credentials, project_id, params, prompt)

    except RuntimeError:
        raise
    except Exception as exc:
        raise RuntimeError(f"Granite API call failed: {exc}") from exc


def test_connection() -> bool:
    """
    Send a minimal prompt to verify that credentials are valid and a model
    is reachable. Returns True on success, False on any error.
    Used only for the credential-validation notice in the UI.
    """
    try:
        from config.settings import get_credentials
        from ibm_watsonx_ai import Credentials
        from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as Params

        api_key, project_id, url, _ = get_credentials()

        if not (api_key and project_id and url):
            return False

        credentials = Credentials(url=url, api_key=api_key)
        params = {
            Params.MAX_NEW_TOKENS: 5,
            Params.TEMPERATURE: 0,
            Params.DECODING_METHOD: "greedy",
        }
        _get_working_model(credentials, project_id, params, "Say OK")
        return True
    except Exception:
        return False
