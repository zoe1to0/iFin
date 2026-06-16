"""AkShare data access service.

AkShare is the preferred experimental real-data layer for iFin after Yahoo
Finance rate limiting. This module is intentionally not wired into the UI yet.
All public methods fail safely and return empty data structures instead of
raising errors into the app.
"""

from __future__ import annotations

from typing import Any

import akshare as ak


class AkShareService:
    """Small safe wrapper around selected AkShare market and news interfaces."""

    @staticmethod
    def _clean_value(value: Any) -> Any:
        """Convert missing dataframe values into None and keep simple values."""
        if value is None:
            return None
        try:
            if hasattr(value, "item"):
                value = value.item()
            if isinstance(value, float) and value != value:
                return None
        except (TypeError, ValueError):
            return None
        return value

    @staticmethod
    def _to_float(value: Any) -> float | None:
        """Safely convert AkShare numeric fields to float."""
        value = AkShareService._clean_value(value)
        if value in (None, "", "-", "--"):
            return None
        try:
            return float(str(value).replace(",", "").replace("%", ""))
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _to_text(value: Any) -> str:
        """Safely convert AkShare dataframe cells to strings."""
        value = AkShareService._clean_value(value)
        if value is None:
            return ""
        return str(value)

    @staticmethod
    def _pick(row: Any, candidates: list[str]) -> Any:
        """Return the first available value from a dataframe row."""
        for key in candidates:
            if key in row:
                return row.get(key)
        return None

    def get_stock_news(self, keyword: str, limit: int = 10) -> list[dict[str, str]]:
        """Return stock or keyword-related news from AkShare.

        On any AkShare/network/dataframe failure, return an empty list.
        """
        try:
            df = ak.stock_news_em(symbol=keyword)
            if df is None or df.empty:
                return []

            records = []
            for _, row in df.head(max(limit, 0)).iterrows():
                records.append(
                    {
                        "title": self._to_text(
                            self._pick(row, ["新闻标题", "标题", "title"])
                        ),
                        "source": self._to_text(
                            self._pick(row, ["文章来源", "来源", "媒体名称", "source"])
                        ),
                        "date": self._to_text(
                            self._pick(row, ["发布时间", "日期", "时间", "date"])
                        ),
                        "url": self._to_text(
                            self._pick(row, ["新闻链接", "链接", "url", "URL"])
                        ),
                        "summary": self._to_text(
                            self._pick(row, ["新闻内容", "内容", "摘要", "summary"])
                        ),
                    }
                )
            return records
        except Exception:
            return []

    def get_a_stock_snapshot(self, symbol: str) -> dict[str, Any]:
        """Return an A-share stock snapshot from AkShare with safe None fields."""
        fallback = {
            "symbol": symbol,
            "name": "",
            "price": None,
            "change_pct": None,
            "volume": None,
        }
        try:
            df = ak.stock_zh_a_spot_em()
            if df is None or df.empty:
                return fallback

            symbol_text = str(symbol).strip()
            matched = df[df["代码"].astype(str) == symbol_text] if "代码" in df.columns else df.iloc[0:0]
            if matched.empty:
                return fallback

            row = matched.iloc[0]
            return {
                "symbol": self._to_text(self._pick(row, ["代码"])) or symbol,
                "name": self._to_text(self._pick(row, ["名称"])),
                "price": self._to_float(self._pick(row, ["最新价", "最新", "价格"])),
                "change_pct": self._to_float(self._pick(row, ["涨跌幅", "涨幅", "change_pct"])),
                "volume": self._to_float(self._pick(row, ["成交量", "volume"])),
            }
        except Exception:
            return fallback

    def get_macro_news(self, limit: int = 10) -> list[dict[str, str]]:
        """Return macro-market news-like items from AkShare.

        Uses AkShare's Caixin data/news stream when available. On failure,
        return an empty list.
        """
        try:
            df = ak.stock_news_main_cx()
            if df is None or df.empty:
                return []

            records = []
            for _, row in df.head(max(limit, 0)).iterrows():
                summary = self._to_text(
                    self._pick(row, ["摘要", "内容", "新闻内容", "summary"])
                )
                records.append(
                    {
                        "title": self._to_text(self._pick(row, ["标题", "新闻标题", "title"]))
                        or summary[:60],
                        "source": self._to_text(
                            self._pick(row, ["来源", "文章来源", "source", "tag"])
                        ),
                        "date": self._to_text(
                            self._pick(row, ["发布时间", "日期", "时间", "date"])
                        ),
                        "url": self._to_text(
                            self._pick(row, ["链接", "新闻链接", "url", "URL"])
                        ),
                        "summary": summary,
                    }
                )
            return records
        except Exception:
            return []


if __name__ == "__main__":
    service = AkShareService()
    print(service.get_macro_news(limit=5))
    print(service.get_stock_news("人工智能", limit=5))
    print(service.get_a_stock_snapshot("600519"))
