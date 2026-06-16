"""Parser utilities for future Event Analysis LLM responses."""

import re
import json
from html import unescape

from schemas.event_schema import EVENT_ANALYSIS_SCHEMA


MARKET_POSITION_DEFAULTS = {
    "direction": "不确定",
    "percentile": "待数据接入",
    "peer_position": "待数据接入",
    "data_note": "当前为新闻语境判断，非实时行情计算",
    "current": "",
    "change_1d": "",
    "change_1m": "",
    "change_3m": "",
    "change_1y": "",
    "percentile_1y": "",
    "as_of": "",
    "period": "",
    "source": "",
    "is_mock": False,
}

KEY_DATA_DEFAULTS = {
    "current": "",
    "change_1d": "",
    "change_1m": "",
    "change_3m": "",
    "change_1y": "",
    "percentile_1y": "",
    "as_of": "",
    "period": "",
    "source": "",
    "is_mock": False,
    "data_note": "",
}

HTML_TAG_PATTERN = re.compile(r"</?(div|span|p|br)\b[^>]*>", re.IGNORECASE)


def _clean_html_text(value: str) -> str:
    return HTML_TAG_PATTERN.sub("", unescape(value or "")).strip()


def _clean_html_tags(value):
    if isinstance(value, str):
        return _clean_html_text(value)
    if isinstance(value, list):
        return [_clean_html_tags(item) for item in value]
    if isinstance(value, dict):
        return {key: _clean_html_tags(item) for key, item in value.items()}
    return value


def _clean_json_fence(raw_response: str) -> str:
    text = (raw_response or "").strip()
    if text.startswith("```json"):
        text = text[len("```json") :].strip()
    elif text.startswith("```"):
        text = text[len("```") :].strip()
    if text.endswith("```"):
        text = text[:-3].strip()
    return text


def _default_event_response() -> dict:
    return {
        field: "" if spec.get("type") == "string" else []
        for field, spec in EVENT_ANALYSIS_SCHEMA.items()
    }


def parse_event_response(raw_response: str) -> dict:
    """Parse a raw LLM response into a validated Event Analysis dictionary."""
    try:
        parsed = json.loads(_clean_json_fence(raw_response))
    except (TypeError, json.JSONDecodeError):
        return _default_event_response()

    if not isinstance(parsed, dict):
        return _default_event_response()

    parsed = _clean_html_tags(parsed)
    return validate_event_schema(parsed)


def validate_event_schema(data: dict) -> dict:
    """Ensure all Event Analysis schema fields are present with safe defaults."""
    validated = _default_event_response()
    if not isinstance(data, dict):
        return validated

    for field, spec in EVENT_ANALYSIS_SCHEMA.items():
        value = data.get(field, validated[field])
        if spec.get("type") == "string":
            validated[field] = value if isinstance(value, str) else ""
        elif spec.get("type") == "array":
            validated[field] = value if isinstance(value, list) else []

    validated["market_position"] = _normalize_market_position(
        validated.get("market_position")
    )
    validated["key_data"] = _normalize_key_data(validated.get("key_data"))
    validated["logic_chain"] = _normalize_logic_chain(
        validated.get("logic_chain")
    )
    validated["evidence_pool"] = _normalize_evidence_pool(
        validated.get("evidence_pool")
    )
    for field in [
        "bull_case",
        "bear_case",
        "risk_radar",
        "historical_cases",
        "next_watch",
    ]:
        validated[field] = _normalize_evidence_ids(validated.get(field))
    return validated


def _copy_market_data_fields(item: dict, defaults: dict) -> dict:
    return {
        "current": item.get("current", defaults["current"]),
        "change_1d": item.get("change_1d", defaults["change_1d"]),
        "change_1m": item.get("change_1m", defaults["change_1m"]),
        "change_3m": item.get("change_3m", defaults["change_3m"]),
        "change_1y": item.get("change_1y", defaults["change_1y"]),
        "percentile_1y": item.get("percentile_1y", defaults["percentile_1y"]),
        "as_of": item.get("as_of", defaults["as_of"]),
        "period": item.get("period", defaults["period"]),
        "source": item.get("source", defaults["source"]),
        "is_mock": item.get("is_mock", defaults["is_mock"]),
        "data_note": item.get("data_note", defaults.get("data_note", "")),
    }


def _normalize_market_position(value: list) -> list:
    normalized = []
    for item in value if isinstance(value, list) else []:
        if isinstance(item, dict):
            normalized_item = {
                "name": item.get("name", ""),
                "position": item.get("position", ""),
                "direction": item.get(
                    "direction", MARKET_POSITION_DEFAULTS["direction"]
                ),
                "percentile": item.get(
                    "percentile", MARKET_POSITION_DEFAULTS["percentile"]
                ),
                "peer_position": item.get(
                    "peer_position", MARKET_POSITION_DEFAULTS["peer_position"]
                ),
                "explanation": item.get("explanation", ""),
            }
            normalized_item.update(_copy_market_data_fields(item, MARKET_POSITION_DEFAULTS))
            normalized_item["data_note"] = normalized_item.get("data_note") or MARKET_POSITION_DEFAULTS["data_note"]
            normalized.append(normalized_item)
        elif isinstance(item, str):
            normalized.append(
                {
                    "name": item,
                    "position": "不确定",
                    "direction": MARKET_POSITION_DEFAULTS["direction"],
                    "percentile": MARKET_POSITION_DEFAULTS["percentile"],
                    "peer_position": MARKET_POSITION_DEFAULTS["peer_position"],
                    "data_note": MARKET_POSITION_DEFAULTS["data_note"],
                    "explanation": "",
                    "current": "",
                    "change_1d": "",
                    "change_1m": "",
                    "change_3m": "",
                    "change_1y": "",
                    "percentile_1y": "",
                    "as_of": "",
                    "period": "",
                    "source": "",
                    "is_mock": False,
                }
            )
    return normalized


def _normalize_key_data(value: list) -> list:
    normalized = []
    for item in value if isinstance(value, list) else []:
        if isinstance(item, dict):
            normalized_item = {
                "name": item.get("name", ""),
                "trend": item.get("trend", ""),
                "explanation": item.get("explanation", ""),
                "value": item.get("value", ""),
            }
            normalized_item.update(_copy_market_data_fields(item, KEY_DATA_DEFAULTS))
            normalized.append(normalized_item)
        elif isinstance(item, str):
            normalized.append(
                {
                    "name": item,
                    "trend": "",
                    "explanation": "",
                    "value": "",
                    **KEY_DATA_DEFAULTS,
                }
            )
    return normalized


def _normalize_logic_chain(value: list) -> list:
    normalized = []
    for index, item in enumerate(value if isinstance(value, list) else [], start=1):
        if isinstance(item, dict):
            evidence_ids = item.get("evidence_ids", [])
            if not isinstance(evidence_ids, list):
                evidence_ids = []
            normalized.append(
                {
                    "step": item.get("step") or f"Step {index}",
                    "title": item.get("title", ""),
                    "content": item.get("content", ""),
                    "description": item.get("description")
                    or item.get("explanation", ""),
                    "evidence_ids": [
                        str(evidence_id)
                        for evidence_id in evidence_ids
                        if isinstance(evidence_id, (str, int))
                    ],
                }
            )
        elif isinstance(item, str):
            normalized.append(
                {
                    "step": f"Step {index}",
                    "title": "",
                    "content": item,
                    "description": "",
                    "evidence_ids": [],
                }
            )
    return normalized


def _normalize_evidence_pool(value: list) -> list:
    normalized = []
    for index, item in enumerate(value if isinstance(value, list) else [], start=1):
        if not isinstance(item, dict):
            continue
        normalized.append(
            {
                "id": item.get("id") or f"news_{index}",
                "title": item.get("title", ""),
                "source": item.get("source", ""),
                "date": item.get("date", ""),
                "url": item.get("url", ""),
                "summary": item.get("summary", ""),
            }
        )
    return normalized


def _normalize_evidence_ids(value: list) -> list:
    normalized = []
    for item in value if isinstance(value, list) else []:
        if isinstance(item, dict):
            evidence_ids = item.get("evidence_ids", [])
            if not isinstance(evidence_ids, list):
                evidence_ids = []
            item["evidence_ids"] = [
                str(evidence_id)
                for evidence_id in evidence_ids
                if isinstance(evidence_id, (str, int))
            ]
            normalized.append(item)
        else:
            normalized.append(item)
    return normalized
