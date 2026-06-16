"""Parser utilities for future Reports LLM responses."""

import json

from schemas.report_schema import REPORT_ANALYSIS_SCHEMA


def _clean_json_fence(raw_response: str) -> str:
    text = (raw_response or "").strip()
    if text.startswith("```json"):
        text = text[len("```json") :].strip()
    elif text.startswith("```"):
        text = text[len("```") :].strip()
    if text.endswith("```"):
        text = text[:-3].strip()
    return text


def _default_report_response() -> dict:
    return {
        field: "" if spec.get("type") == "string" else []
        for field, spec in REPORT_ANALYSIS_SCHEMA.items()
    }


def parse_report_response(raw_response: str) -> dict:
    """Parse a raw LLM response into a validated Reports dictionary."""
    try:
        parsed = json.loads(_clean_json_fence(raw_response))
    except (TypeError, json.JSONDecodeError):
        return _default_report_response()

    if not isinstance(parsed, dict):
        return _default_report_response()

    return validate_report_schema(parsed)


def validate_report_schema(data: dict) -> dict:
    """Ensure all Reports schema fields are present with safe defaults."""
    validated = _default_report_response()
    if not isinstance(data, dict):
        return validated

    for field, spec in REPORT_ANALYSIS_SCHEMA.items():
        value = data.get(field, validated[field])
        if spec.get("type") == "string":
            validated[field] = value if isinstance(value, str) else ""
        elif spec.get("type") == "array":
            validated[field] = value if isinstance(value, list) else []
    return validated
