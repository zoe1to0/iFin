"""Yahoo Finance data access service.

This module provides a small data layer around yfinance. It does not connect
to any LLM, does not modify UI state, and is intended for manual data-layer
verification before the app consumes real market data.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import yfinance as yf


class YahooFinanceService:
    """Read company, stock, news, and financial summary data from Yahoo Finance."""

    def _get_ticker(self, ticker: str) -> yf.Ticker | None:
        """Create a yfinance ticker object for a non-empty ticker symbol."""
        symbol = ticker.strip().upper()
        if not symbol:
            return None
        return yf.Ticker(symbol)

    @staticmethod
    def _clean_number(value: Any) -> int | float | None:
        """Convert pandas/numpy/yfinance numeric values into plain Python numbers."""
        if value is None:
            return None
        try:
            if hasattr(value, "item"):
                value = value.item()
            if isinstance(value, float) and value != value:
                return None
            if isinstance(value, int):
                return value
            if isinstance(value, float):
                return value
            return float(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _format_published(value: Any) -> str:
        """Format a Yahoo publish timestamp as an ISO date-time string."""
        if value is None:
            return ""
        try:
            return datetime.fromtimestamp(int(value), tz=timezone.utc).isoformat()
        except (TypeError, ValueError, OSError):
            return str(value)

    @staticmethod
    def _first_statement_value(statement: Any, labels: list[str]) -> int | float | None:
        """Return the latest available value for the first matching statement row."""
        if statement is None or getattr(statement, "empty", True):
            return None
        for label in labels:
            if label in statement.index:
                row = statement.loc[label].dropna()
                if not row.empty:
                    return YahooFinanceService._clean_number(row.iloc[0])
        return None

    def get_company_profile(self, ticker: str) -> dict[str, Any] | None:
        """Return company profile fields from ticker.info, or None when unavailable."""
        try:
            ticker_obj = self._get_ticker(ticker)
            if ticker_obj is None:
                return None

            info = ticker_obj.info or {}
            profile = {
                "name": info.get("longName") or info.get("shortName") or "",
                "sector": info.get("sector") or "",
                "industry": info.get("industry") or "",
                "market_cap": self._clean_number(info.get("marketCap")),
                "country": info.get("country") or "",
            }
            if not any(profile.values()):
                return None
            return profile
        except Exception:
            return None

    def get_stock_snapshot(self, ticker: str) -> dict[str, Any] | None:
        """Return latest price, 5-day percentage change, volume, and market cap."""
        try:
            ticker_obj = self._get_ticker(ticker)
            if ticker_obj is None:
                return None

            history = ticker_obj.history(period="5d")
            if history is None or history.empty:
                return None

            closes = history["Close"].dropna()
            if closes.empty:
                return None

            latest_price = self._clean_number(closes.iloc[-1])
            previous_price = self._clean_number(closes.iloc[0])
            change_pct = None
            if latest_price is not None and previous_price not in (None, 0):
                change_pct = ((float(latest_price) - float(previous_price)) / float(previous_price)) * 100

            volume = None
            if "Volume" in history:
                volumes = history["Volume"].dropna()
                if not volumes.empty:
                    volume = self._clean_number(volumes.iloc[-1])

            info = ticker_obj.info or {}
            snapshot = {
                "price": latest_price,
                "change_pct": change_pct,
                "volume": volume,
                "market_cap": self._clean_number(info.get("marketCap")),
            }
            if not any(value is not None for value in snapshot.values()):
                return None
            return snapshot
        except Exception:
            return None

    def get_company_news(self, ticker: str, limit: int = 5) -> list[dict[str, str]] | None:
        """Return recent Yahoo Finance news items for a ticker."""
        try:
            ticker_obj = self._get_ticker(ticker)
            if ticker_obj is None:
                return None

            raw_news = ticker_obj.news or []
            news_items = []
            for item in raw_news[: max(limit, 0)]:
                news_items.append(
                    {
                        "title": item.get("title") or "",
                        "publisher": item.get("publisher") or "",
                        "link": item.get("link") or "",
                        "published": self._format_published(item.get("providerPublishTime")),
                    }
                )
            return news_items or None
        except Exception:
            return None

    def get_financial_summary(self, ticker: str) -> dict[str, Any] | None:
        """Return latest revenue, net income, total assets, and cash values."""
        try:
            ticker_obj = self._get_ticker(ticker)
            if ticker_obj is None:
                return None

            financials = ticker_obj.financials
            balance_sheet = ticker_obj.balance_sheet
            summary = {
                "revenue": self._first_statement_value(financials, ["Total Revenue", "Operating Revenue"]),
                "net_income": self._first_statement_value(financials, ["Net Income", "Net Income Common Stockholders"]),
                "total_assets": self._first_statement_value(balance_sheet, ["Total Assets"]),
                "cash": self._first_statement_value(
                    balance_sheet,
                    [
                        "Cash And Cash Equivalents",
                        "Cash Cash Equivalents And Short Term Investments",
                        "Cash Financial",
                    ],
                ),
            }
            if not any(value is not None for value in summary.values()):
                return None
            return summary
        except Exception:
            return None


if __name__ == "__main__":
    import json

    service = YahooFinanceService()
    for symbol in ["AAPL", "MSFT", "TSLA", "NVDA"]:
        print(f"\n=== {symbol} ===")
        print("Profile:")
        print(json.dumps(service.get_company_profile(symbol), ensure_ascii=False, indent=2))
        print("Snapshot:")
        print(json.dumps(service.get_stock_snapshot(symbol), ensure_ascii=False, indent=2))
        print("News:")
        print(json.dumps(service.get_company_news(symbol), ensure_ascii=False, indent=2))
        print("Financial Summary:")
        print(json.dumps(service.get_financial_summary(symbol), ensure_ascii=False, indent=2))
