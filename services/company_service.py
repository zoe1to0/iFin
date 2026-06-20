"""Company V2 service orchestrator MVP.

This module composes the local router, defensive market snapshot, mock
evidence pool, and rule-based card adapter. It performs no LLM analysis and
does not retrieve real company filings.
"""

from __future__ import annotations

from typing import Any

try:
    from services.company_card_adapter import build_company_card_pool
    from services.company_evidence import create_mock_company_evidence
    from services.company_market_data import get_company_market_snapshot
    from services.company_router import CompanyResolution, resolve_company
except ModuleNotFoundError:  # Support direct local execution from services/.
    from company_card_adapter import build_company_card_pool
    from company_evidence import create_mock_company_evidence
    from company_market_data import get_company_market_snapshot
    from company_router import CompanyResolution, resolve_company


CURRENCY_BY_MARKET = {
    "US": "USD",
    "HK": "HKD",
}


def _company_profile(resolution: CompanyResolution) -> dict[str, Any]:
    """Build the profile fields supported by the local router only."""
    return {
        "company_id": resolution.company_id,
        "display_name": resolution.display_name,
        "legal_name": resolution.legal_name,
        "ticker": resolution.ticker,
        "exchange": resolution.exchange,
        "market": resolution.market,
        "currency": CURRENCY_BY_MARKET.get(resolution.market, ""),
        "sector": "",
        "industry": "",
        "business_segments": [],
        "related_companies": [],
    }


def _empty_market_snapshot(resolution: CompanyResolution) -> dict[str, Any]:
    return {
        "company_id": resolution.company_id,
        "ticker": resolution.ticker,
        "market": resolution.market,
        "currency": CURRENCY_BY_MARKET.get(resolution.market, ""),
        "price": None,
        "open": None,
        "high": None,
        "low": None,
        "volume": None,
        "market_cap": None,
        "pe_ratio": None,
        "updated_at": "",
        "data_status": "unavailable",
        "source": "",
        "missing_fields": [
            "price",
            "open",
            "high",
            "low",
            "volume",
            "market_cap",
            "pe_ratio",
        ],
    }


def _evidence_status(records: list[dict[str, Any]]) -> str:
    if not records:
        return "insufficient"
    labels = {str(item.get("confidence", "")).casefold() for item in records}
    if labels == {"unverified"}:
        return "unverified"
    if "unverified" in labels:
        return "partial"
    return "sufficient"


def _unresolved_result(query: str) -> dict[str, Any]:
    return {
        "company_profile": {},
        "market_snapshot": {},
        "evidence_pool": [],
        "company_card_pool": [],
        "metadata": {
            "resolved": False,
            "company_id": "",
            "data_mode": "mock_evidence_mvp",
            "evidence_status": "insufficient",
            "market_data_status": "unavailable",
            "warnings": [
                f"Company query could not be resolved by the local router: {query}"
            ],
        },
    }


def run_company_analysis(query: str) -> dict[str, Any]:
    """Run the Company V2 MVP pipeline without LLM or filing retrieval."""
    resolution = resolve_company(query)
    if not resolution.resolved:
        return _unresolved_result(str(query or ""))

    warnings: list[str] = []
    profile = _company_profile(resolution)

    try:
        market_snapshot = get_company_market_snapshot(resolution)
    except Exception as exc:  # Defensive orchestration boundary.
        market_snapshot = _empty_market_snapshot(resolution)
        warnings.append(f"Market snapshot failed safely: {type(exc).__name__}")

    try:
        evidence = create_mock_company_evidence(resolution.company_id)
        evidence_records = [item.to_dict() for item in evidence.evidence]
    except Exception as exc:  # Defensive orchestration boundary.
        evidence = []
        evidence_records = []
        warnings.append(f"Mock evidence creation failed safely: {type(exc).__name__}")

    try:
        card_pool = build_company_card_pool(
            profile,
            market_snapshot,
            evidence,
        )
    except Exception as exc:  # Defensive orchestration boundary.
        card_pool = []
        warnings.append(f"Company card adaptation failed safely: {type(exc).__name__}")

    evidence_status = _evidence_status(evidence_records)
    market_status = str(market_snapshot.get("data_status", "unavailable"))
    if evidence_status == "unverified":
        warnings.append("Evidence contains mock fixtures for structural validation only.")
    elif evidence_status == "insufficient":
        warnings.append("No Company Evidence fixture is available for this company.")
    if market_status != "available":
        warnings.append(f"Company market data status is {market_status}.")

    return {
        "company_profile": profile,
        "market_snapshot": market_snapshot,
        "evidence_pool": evidence_records,
        "company_card_pool": card_pool,
        "metadata": {
            "resolved": True,
            "company_id": resolution.company_id,
            "data_mode": "mock_evidence_mvp",
            "evidence_status": evidence_status,
            "market_data_status": market_status,
            "warnings": warnings,
        },
    }


if __name__ == "__main__":
    import json

    for sample in ["NVDA", "英伟达", "腾讯", "0700.HK", "UNKNOWN"]:
        result = run_company_analysis(sample)
        metadata = result["metadata"]
        cards = result["company_card_pool"]
        output = {
            "query": sample,
            "resolved": metadata["resolved"],
            "company_id": metadata["company_id"],
            "market_data_status": metadata["market_data_status"],
            "evidence_count": len(result["evidence_pool"]),
            "card_count": len(cards),
            "empty_card_count": sum(
                bool(card.get("empty_state")) for card in cards
            ),
        }
        print(json.dumps(output, ensure_ascii=False))
