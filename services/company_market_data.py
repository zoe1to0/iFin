"""Company Market Layer MVP.

The service normalizes a small Yahoo Finance snapshot for companies supported
by the local Company Router. Missing external data remains missing; the module
does not estimate market values or raise provider failures into callers.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

try:
    import yfinance as yf
except ModuleNotFoundError:  # pragma: no cover - deployment dependency guard
    yf = None

try:
    from services.company_router import CompanyResolution, resolve_company
except ModuleNotFoundError:  # Support direct local execution from services/.
    from company_router import CompanyResolution, resolve_company

YahooFinanceService = None
if yf is not None:
    try:
        from services.yahoo_service import YahooFinanceService
    except ModuleNotFoundError:  # Support direct local execution from services/.
        from yahoo_service import YahooFinanceService


MARKET_FIELDS = [
    "price",
    "open",
    "high",
    "low",
    "volume",
    "market_cap",
    "pe_ratio",
]

SUPPORTED_TICKERS = {
    "NVDA",
    "AAPL",
    "META",
    "GOOG",
    "GOOGL",
    "TSLA",
    "0700.HK",
    "9988.HK",
    "1810.HK",
}

CURRENCY_BY_MARKET = {
    "US": "USD",
    "HK": "HKD",
}


def _clean_number(value: Any) -> int | float | None:
    """Convert provider values to JSON-safe numbers."""
    if value is None:
        return None
    try:
        if hasattr(value, "item"):
            value = value.item()
        if isinstance(value, float) and value != value:
            return None
        if isinstance(value, int | float):
            return value
        return float(value)
    except (TypeError, ValueError):
        return None


def _identity_from_input(
    company_resolution: CompanyResolution | Mapping[str, Any] | str,
    market: str = "",
) -> dict[str, Any]:
    """Normalize supported router, mapping, or ticker input."""
    if isinstance(company_resolution, CompanyResolution):
        return company_resolution.to_dict()

    if isinstance(company_resolution, Mapping):
        return {
            "resolved": bool(company_resolution.get("resolved", True)),
            "company_id": str(company_resolution.get("company_id", "")),
            "ticker": str(company_resolution.get("ticker", "")).strip().upper(),
            "market": str(company_resolution.get("market", market)).strip().upper(),
        }

    query = str(company_resolution or "").strip()
    resolution = resolve_company(query)
    if resolution.resolved:
        return resolution.to_dict()

    ticker = query.upper()
    normalized_market = str(market or "").strip().upper()
    if normalized_market in {"US", "HK"} and ticker in SUPPORTED_TICKERS:
        local_ticker = ticker.removesuffix(".HK")
        return {
            "resolved": True,
            "company_id": f"{normalized_market}_{local_ticker}",
            "ticker": ticker,
            "market": normalized_market,
        }

    return {
        "resolved": False,
        "company_id": "",
        "ticker": ticker,
        "market": normalized_market,
    }


def _empty_snapshot(identity: Mapping[str, Any]) -> dict[str, Any]:
    market = str(identity.get("market", "")).upper()
    snapshot = {
        "company_id": str(identity.get("company_id", "")),
        "ticker": str(identity.get("ticker", "")),
        "market": market,
        "currency": CURRENCY_BY_MARKET.get(market, ""),
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
        "missing_fields": list(MARKET_FIELDS),
    }
    return snapshot


def _format_observation_time(index_value: Any) -> str:
    if index_value is None:
        return ""
    try:
        return index_value.isoformat()
    except (AttributeError, TypeError, ValueError):
        return str(index_value)


def _apply_history(snapshot: dict[str, Any], history: Any) -> None:
    if history is None or getattr(history, "empty", True):
        return

    row = history.iloc[-1]
    close = _clean_number(row.get("Close"))
    volume = _clean_number(row.get("Volume"))
    if close is not None:
        snapshot["price"] = close
    snapshot["open"] = _clean_number(row.get("Open"))
    snapshot["high"] = _clean_number(row.get("High"))
    snapshot["low"] = _clean_number(row.get("Low"))
    if volume is not None:
        snapshot["volume"] = volume
    snapshot["updated_at"] = _format_observation_time(history.index[-1])


def _finalize_status(snapshot: dict[str, Any]) -> dict[str, Any]:
    missing_fields = [field for field in MARKET_FIELDS if snapshot.get(field) is None]
    available_count = len(MARKET_FIELDS) - len(missing_fields)
    snapshot["missing_fields"] = missing_fields
    if available_count == len(MARKET_FIELDS):
        snapshot["data_status"] = "available"
    elif available_count > 0:
        snapshot["data_status"] = "partial"
    else:
        snapshot["data_status"] = "unavailable"
        snapshot["source"] = ""
    return snapshot


def get_company_market_snapshot(
    company_resolution: CompanyResolution | Mapping[str, Any] | str,
    market: str = "",
) -> dict[str, Any]:
    """Return a safe Company V2 market snapshot for a supported company.

    ``market`` is only needed when a raw ticker is supplied outside a resolved
    Company Router record. A-share data is intentionally unavailable in this
    MVP.
    """
    identity = _identity_from_input(company_resolution, market=market)
    snapshot = _empty_snapshot(identity)
    ticker = str(identity.get("ticker", ""))
    resolved_market = str(identity.get("market", "")).upper()

    if (
        not identity.get("resolved")
        or resolved_market not in {"US", "HK"}
        or ticker not in SUPPORTED_TICKERS
    ):
        return snapshot

    # Reuse the existing Yahoo service for its safe public snapshot first.
    if YahooFinanceService is not None:
        try:
            base = YahooFinanceService().get_stock_snapshot(ticker) or {}
            snapshot["price"] = _clean_number(base.get("price"))
            snapshot["volume"] = _clean_number(base.get("volume"))
            snapshot["market_cap"] = _clean_number(base.get("market_cap"))
        except Exception:
            pass

    # Add fields not exposed by YahooFinanceService without changing it.
    if yf is not None:
        try:
            ticker_data = yf.Ticker(ticker)
            history = ticker_data.history(period="5d", interval="1d", auto_adjust=False)
            _apply_history(snapshot, history)

            info = ticker_data.info or {}
            market_cap = _clean_number(info.get("marketCap"))
            if market_cap is not None:
                snapshot["market_cap"] = market_cap
            snapshot["pe_ratio"] = _clean_number(info.get("trailingPE"))
            snapshot["currency"] = str(
                info.get("currency") or snapshot["currency"]
            ).upper()
        except Exception:
            pass

    if any(snapshot.get(field) is not None for field in MARKET_FIELDS):
        snapshot["source"] = "Yahoo Finance"
    return _finalize_status(snapshot)


if __name__ == "__main__":
    import json

    for sample in ["NVDA", "AAPL", "0700.HK", "腾讯", "UNKNOWN"]:
        result = get_company_market_snapshot(resolve_company(sample))
        output = {
            "company_id": result["company_id"],
            "ticker": result["ticker"],
            "data_status": result["data_status"],
            "source": result["source"],
            "missing_fields": result["missing_fields"],
        }
        print(f"\n=== {sample} ===")
        print(json.dumps(output, ensure_ascii=False, indent=2))
