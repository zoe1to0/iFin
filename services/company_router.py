"""Local company identity resolution for the Company V2 MVP.

This module intentionally uses a small deterministic registry. It performs no
network requests and does not infer companies that are not explicitly listed.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field


@dataclass(frozen=True)
class CompanyResolution:
    """Normalized company identity returned by :func:`resolve_company`."""

    resolved: bool
    company_id: str = ""
    display_name: str = ""
    legal_name: str = ""
    ticker: str = ""
    market: str = ""
    exchange: str = ""
    confidence: float = 0.0
    candidates: list[dict[str, str]] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-serializable representation."""
        return asdict(self)


COMPANY_REGISTRY: dict[str, dict[str, object]] = {
    "US_NVDA": {
        "display_name": "NVIDIA",
        "legal_name": "NVIDIA Corporation",
        "ticker": "NVDA",
        "market": "US",
        "exchange": "NASDAQ",
        "aliases": ["NVDA", "NVIDIA", "英伟达"],
    },
    "US_AAPL": {
        "display_name": "Apple",
        "legal_name": "Apple Inc.",
        "ticker": "AAPL",
        "market": "US",
        "exchange": "NASDAQ",
        "aliases": ["AAPL", "APPLE", "苹果"],
    },
    "US_META": {
        "display_name": "Meta",
        "legal_name": "Meta Platforms, Inc.",
        "ticker": "META",
        "market": "US",
        "exchange": "NASDAQ",
        "aliases": ["META", "FACEBOOK"],
    },
    "US_GOOGL": {
        "display_name": "Alphabet",
        "legal_name": "Alphabet Inc.",
        "ticker": "GOOGL",
        "market": "US",
        "exchange": "NASDAQ",
        "aliases": ["GOOG", "GOOGL", "GOOGLE", "ALPHABET"],
    },
    "US_TSLA": {
        "display_name": "Tesla",
        "legal_name": "Tesla, Inc.",
        "ticker": "TSLA",
        "market": "US",
        "exchange": "NASDAQ",
        "aliases": ["TSLA", "TESLA", "特斯拉"],
    },
    "HK_0700": {
        "display_name": "腾讯",
        "legal_name": "Tencent Holdings Limited",
        "ticker": "0700.HK",
        "market": "HK",
        "exchange": "HKEX",
        "aliases": ["0700", "0700.HK", "TENCENT", "腾讯", "腾讯控股"],
    },
    "HK_9988": {
        "display_name": "阿里巴巴",
        "legal_name": "Alibaba Group Holding Limited",
        "ticker": "9988.HK",
        "market": "HK",
        "exchange": "HKEX",
        "aliases": ["9988", "9988.HK", "ALIBABA", "阿里巴巴", "阿里"],
    },
    "HK_1810": {
        "display_name": "小米",
        "legal_name": "Xiaomi Corporation",
        "ticker": "1810.HK",
        "market": "HK",
        "exchange": "HKEX",
        "aliases": ["1810", "1810.HK", "XIAOMI", "小米", "小米集团"],
    },
}


def _normalize_alias(value: str) -> str:
    """Normalize user input without applying fuzzy company-name matching."""
    return " ".join((value or "").strip().split()).casefold()


def _build_alias_index() -> dict[str, str]:
    index: dict[str, str] = {}
    for company_id, company in COMPANY_REGISTRY.items():
        for alias in company.get("aliases", []):
            normalized = _normalize_alias(str(alias))
            if normalized:
                index[normalized] = company_id
    return index


ALIAS_INDEX = _build_alias_index()


def resolve_company(query: str) -> CompanyResolution:
    """Resolve a supported company alias into a normalized local identity."""
    normalized = _normalize_alias(query)
    company_id = ALIAS_INDEX.get(normalized)
    if not company_id:
        return CompanyResolution(resolved=False)

    company = COMPANY_REGISTRY[company_id]
    canonical_ticker = _normalize_alias(str(company["ticker"]))
    confidence = 1.0 if normalized == canonical_ticker else 0.98
    return CompanyResolution(
        resolved=True,
        company_id=company_id,
        display_name=str(company["display_name"]),
        legal_name=str(company["legal_name"]),
        ticker=str(company["ticker"]),
        market=str(company["market"]),
        exchange=str(company["exchange"]),
        confidence=confidence,
    )


if __name__ == "__main__":
    import json

    for sample in ["英伟达", "NVDA", "腾讯", "0700.HK"]:
        print(f"\n=== {sample} ===")
        print(json.dumps(resolve_company(sample).to_dict(), ensure_ascii=False, indent=2))
