"""Rule-based topic routing for Event Analysis.

The router consumes centralized THEME_PACKAGES and keeps only lightweight
matching logic here.
"""

from __future__ import annotations

import re

from services.theme_packages import THEME_MATCH_ORDER, THEME_PACKAGES, get_theme_package


def _normalize(query: str) -> str:
    return " ".join((query or "").strip().split())


def _contains_any(text: str, keywords: list[str]) -> bool:
    lower_text = text.lower()
    return any(keyword.lower() in lower_text for keyword in keywords)


def _format_query_templates(items: list[dict], query: str) -> list[dict[str, str]]:
    formatted = []
    for item in items:
        if not isinstance(item, dict):
            continue
        formatted.append(
            {
                "label": str(item.get("label", "")).format(query=query),
                "query": str(item.get("query", "")).format(query=query),
            }
        )
    return formatted


INTENT_BY_TOPIC = {
    "precious_metal": "asset_trend",
    "crypto": "crypto_asset",
    "commodity": "commodity_asset",
    "macro": "macro_event",
    "company": "company_event",
    "ai_sector": "sector_trend",
    "semiconductor": "sector_trend",
    "robotics": "sector_trend",
    "new_energy_vehicle": "sector_trend",
    "real_estate": "sector_trend",
    "general": "vague_query",
}


def _package_response(raw_query: str, topic_type: str, primary_intent: str = "") -> dict:
    normalized_query = _normalize(raw_query)
    package = get_theme_package(topic_type)
    search_expansion = [normalized_query] if normalized_query else []
    for term in package.get("search_expansion", []):
        if term and term not in search_expansion:
            search_expansion.append(term)

    return {
        "raw_query": raw_query or "",
        "normalized_query": normalized_query,
        "topic_type": topic_type,
        "primary_intent": primary_intent or INTENT_BY_TOPIC.get(topic_type, "vague_query"),
        "topic_label": package.get("label", ""),
        "data_pack": package.get("data_pack", []),
        "search_expansion": search_expansion,
        "suggested_queries": _format_query_templates(
            package.get("suggested_queries", []),
            normalized_query,
        ),
        "logic_chain_template": package.get("logic_chain_template", []),
        "prompt_rules": package.get("prompt_rules", []),
    }


def route_topic(query: str) -> dict:
    """Route a broad market query into a centralized theme package."""
    raw_query = query or ""
    normalized_query = _normalize(raw_query)
    if not normalized_query:
        return _package_response(raw_query, "general")

    lower_query = normalized_query.lower()
    if any(term in lower_query for term in ["英伟达", "nvidia", "nvda"]):
        return _package_response(raw_query, "company", "company_event")
    if any(term in lower_query for term in ["腾讯", "tencent", "tcehy", "0700"]):
        intent = "earnings_event" if any(
            term in lower_query for term in ["财报", "业绩", "earnings", "revenue", "profit"]
        ) else "company_event"
        return _package_response(raw_query, "company", intent)
    if any(term in lower_query for term in ["苹果", "apple", "aapl", "wwdc"]):
        return _package_response(
            raw_query,
            "company",
            "product_event" if "wwdc" in lower_query else "company_event",
        )
    if any(term in lower_query for term in ["美国cpi", "cpi", "通胀数据", "consumer price"]):
        return _package_response(raw_query, "macro", "macro_indicator")
    if any(term in lower_query for term in ["美国非农", "非农就业", "非农", "nfp", "nonfarm", "payrolls"]):
        return _package_response(raw_query, "macro", "macro_indicator")

    company_package = THEME_PACKAGES["company"]
    company_names = {keyword.lower() for keyword in company_package.get("keywords", [])}
    ticker_like = bool(re.fullmatch(r"[A-Z]{2,5}", normalized_query))
    ticker_exclusions = {"AI", "BTC", "ETH", "CPI", "FOMC", "WTI", "OPEC"}
    if normalized_query.lower() in company_names or (
        ticker_like and normalized_query.upper() not in ticker_exclusions
    ):
        return _package_response(raw_query, "company")

    for topic_type in THEME_MATCH_ORDER:
        package = THEME_PACKAGES.get(topic_type, {})
        if _contains_any(normalized_query, package.get("keywords", [])):
            return _package_response(raw_query, topic_type)

    return _package_response(raw_query, "general")


if __name__ == "__main__":
    import json

    for item in ["黄金", "AI", "芯片", "英伟达", "比特币", "美联储降息50bp", "房地产", "原油"]:
        print(item)
        print(json.dumps(route_topic(item), ensure_ascii=False, indent=2))
