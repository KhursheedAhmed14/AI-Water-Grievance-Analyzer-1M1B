"""
core/response_parser.py
Parses and validates the raw LLM response from IBM Granite / watsonx into a clean,
typed dict with all expected keys and validated enum values.
"""

import json
import re

ALLOWED_CATEGORIES = [
    "Pipeline Leakage",
    "Pipeline Failure",
    "Water Supply Disruption",
    "Low Water Pressure",
    "Other / Unclear",
]

ALLOWED_SEVERITIES = ["Low", "Medium", "High"]

ALLOWED_PRIORITIES = ["Low", "Medium", "High", "Urgent"]

REQUIRED_KEYS = [
    "summary",
    "category",
    "severity",
    "priority",
    "location",
    "duration",
    "affected_people",
    "key_facts",
    "missing_info",
]

_ERROR_DICT: dict = {
    "summary": "Could not parse AI response.",
    "category": "Other / Unclear",
    "severity": "Unclear",
    "priority": "Unclear",
    "location": "Unclear",
    "duration": "Unclear",
    "affected_people": "Unclear",
    "key_facts": [],
    "missing_info": "AI response could not be parsed. Please review raw response.",
}


def _extract_first_json_object(text: str) -> dict | None:
    """
    Safely find and parse the first valid JSON object dictionary from text
    using string-aware bracket balancing instead of greedy regex.
    """
    for start_idx in range(len(text)):
        if text[start_idx] != "{":
            continue

        depth = 0
        in_string = False
        escape = False

        for end_idx in range(start_idx, len(text)):
            char = text[end_idx]

            if in_string:
                if escape:
                    escape = False
                elif char == "\\":
                    escape = True
                elif char == '"':
                    in_string = False
            else:
                if char == '"':
                    in_string = True
                elif char == "{":
                    depth += 1
                elif char == "}":
                    depth -= 1
                    if depth == 0:
                        candidate = text[start_idx : end_idx + 1]
                        try:
                            val = json.loads(candidate)
                            if isinstance(val, dict):
                                return val
                        except (json.JSONDecodeError, ValueError):
                            pass
                        break  # Move to next start_idx if candidate wasn't a valid dict
    return None


def _clean_raw(raw: str) -> str:
    """Strip whitespace and markdown code fences from the raw LLM string."""
    text = raw.strip()
    # Match content inside ```json ... ``` or ``` ... ``` if enclosed
    match = re.search(r"```(?:json)?\s*(.*?)\s*```", text, flags=re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return text


def _normalize_key_facts(value) -> list:
    """
    Ensure key_facts is always a list of strings:
    - list stays list
    - JSON string containing a list becomes a list
    - plain string becomes a one-item list
    - None / empty becomes []
    """
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value if item is not None]
    if isinstance(value, str):
        val_str = value.strip()
        if not val_str:
            return []
        try:
            parsed = json.loads(val_str)
            if isinstance(parsed, list):
                return [str(item) for item in parsed if item is not None]
        except (json.JSONDecodeError, ValueError):
            pass
        return [val_str]
    return []


def parse_response(raw: str) -> dict:
    """
    Parse *raw* LLM output into a validated dict with all expected keys.

    Steps:
    1. Handle empty / invalid input.
    2. Try direct json.loads() on cleaned input.
    3. Try fence-stripped json.loads().
    4. Try safe bracket-matching extraction (_extract_first_json_object).
    5. On total failure, return _ERROR_DICT with raw_response preserved.
    6. Validate enum fields (category, severity, priority).
    7. Normalize key_facts to a list.
    8. Ensure all REQUIRED_KEYS exist.
    """
    if not raw or not isinstance(raw, str):
        err = dict(_ERROR_DICT)
        err["raw_response"] = raw if raw is not None else ""
        return err

    parsed: dict | None = None

    # Step 1: Direct JSON load
    try:
        val = json.loads(raw.strip())
        if isinstance(val, dict):
            parsed = val
    except (json.JSONDecodeError, ValueError):
        pass

    # Step 2: Clean fences & try again
    if parsed is None:
        cleaned = _clean_raw(raw)
        try:
            val = json.loads(cleaned)
            if isinstance(val, dict):
                parsed = val
        except (json.JSONDecodeError, ValueError):
            pass

    # Step 3: Extract first valid JSON object using bracket balancing
    if parsed is None:
        parsed = _extract_first_json_object(raw)

    # Step 4: If parsing completely failed, preserve raw_response and return error dict
    if not isinstance(parsed, dict):
        err = dict(_ERROR_DICT)
        err["raw_response"] = raw
        return err

    # Step 5: Validate enum fields
    if parsed.get("category") not in ALLOWED_CATEGORIES:
        parsed["category"] = "Other / Unclear"
    if parsed.get("severity") not in ALLOWED_SEVERITIES:
        parsed["severity"] = "Unclear"
    if parsed.get("priority") not in ALLOWED_PRIORITIES:
        parsed["priority"] = "Unclear"

    # Step 6: Normalize key_facts
    parsed["key_facts"] = _normalize_key_facts(parsed.get("key_facts"))

    # Step 7: Fill missing keys with defaults
    for key in REQUIRED_KEYS:
        if key not in parsed or parsed[key] is None:
            if key == "missing_info":
                parsed[key] = "None identified"
            elif key == "key_facts":
                parsed[key] = []
            elif key == "category":
                parsed[key] = "Other / Unclear"
            else:
                parsed[key] = "Unclear"

    return parsed
