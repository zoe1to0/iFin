"""Unified market data access layer for Event Analysis.

Priority:
1. AkShare
2. yfinance
3. internal mock state

Mock values are only an internal unavailable-data marker. The UI should not
render them as market data.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Callable

import pandas as pd

try:
    import akshare as ak
except ModuleNotFoundError:
    ak = None

try:
    import yfinance as yf
except ModuleNotFoundError:
    yf = None


logger = logging.getLogger(__name__)

YFINANCE_CACHE_DIR = Path.home() / "Documents" / "Codex" / ".ifin_yfinance_cache"
if yf is not None:
    try:
        YFINANCE_CACHE_DIR.mkdir(parents=True, exist_ok=True)
        yf.set_tz_cache_location(str(YFINANCE_CACHE_DIR))
    except Exception:
        pass


MARKET_DATA_DEFAULT = {
    "label": "",
    "current": "",
    "change_1d": "",
    "change_1m": "",
    "change_3m": "",
    "change_1y": "",
    "percentile_1y": "",
    "as_of": "",
    "period": "",
    "source": "",
    "is_mock": True,
}


class MarketDataService:
    """Provide normalized market data for Event Analysis modules."""

    def get_gold_data(self) -> dict[str, Any]:
        """Return gold data, using GLD as yfinance proxy if needed."""
        akshare_result = self._fetch_akshare_gold()
        if not akshare_result.get("is_mock"):
            return akshare_result

        yfinance_result = self._fetch_yahoo_history(
            symbol="GLD",
            label="黄金价格代理",
            source="Yahoo Finance: GLD proxy",
        )
        if not yfinance_result.get("is_mock"):
            return yfinance_result

        return self._mock_with_log(label="黄金价格代理", source="Market data unavailable")

    def get_dxy_data(self) -> dict[str, Any]:
        """Return US Dollar Index data."""
        akshare_result = self._fetch_akshare_dxy()
        if not akshare_result.get("is_mock"):
            return akshare_result

        for symbol, source in [
            ("DX-Y.NYB", "Yahoo Finance: DX-Y.NYB"),
            ("^DXY", "Yahoo Finance: ^DXY"),
        ]:
            yfinance_result = self._fetch_yahoo_history(
                symbol=symbol,
                label="美元指数",
                source=source,
            )
            if not yfinance_result.get("is_mock"):
                return yfinance_result

        return self._mock_with_log(label="美元指数", source="Market data unavailable")

    def get_us10y_data(self) -> dict[str, Any]:
        """Return US 10-year Treasury yield data."""
        akshare_result = self._fetch_akshare_us10y()
        if not akshare_result.get("is_mock"):
            return akshare_result

        yfinance_result = self._fetch_yahoo_history(
            symbol="^TNX",
            label="10年期美债收益率",
            source="Yahoo Finance: ^TNX",
        )
        if not yfinance_result.get("is_mock"):
            return yfinance_result

        return self._mock_with_log(label="10年期美债收益率", source="Market data unavailable")

    def get_gold_etf_data(self) -> dict[str, Any]:
        """Return GLD ETF data."""
        yfinance_result = self._fetch_yahoo_history(
            symbol="GLD",
            label="黄金 ETF",
            source="Yahoo Finance: GLD",
        )
        if not yfinance_result.get("is_mock"):
            return yfinance_result
        return self._mock_with_log(label="黄金 ETF", source="Market data unavailable")

    def get_equity_or_etf_data(
        self,
        symbol: str,
        label: str,
        source_label: str = "Yahoo Finance",
    ) -> dict[str, Any]:
        """Return normalized Yahoo Finance data for an equity or ETF symbol."""
        clean_symbol = (symbol or "").strip().upper()
        display_label = label or clean_symbol or "Equity / ETF"
        if not clean_symbol:
            return self._mock_with_log(
                label=display_label,
                source="Market data unavailable",
            )

        yfinance_result = self._fetch_yahoo_history(
            symbol=clean_symbol,
            label=display_label,
            source=f"{source_label}: {clean_symbol}",
        )
        if not yfinance_result.get("is_mock"):
            return yfinance_result

        return self._mock_with_log(
            label=display_label,
            source="Market data unavailable",
        )

    def get_ai_sector_data(self) -> dict[str, dict[str, Any]]:
        """Return the first AI sector market data pack."""
        ai_etf = self.get_equity_or_etf_data("BOTZ", "AI相关ETF")
        if ai_etf.get("is_mock"):
            ai_etf = self.get_equity_or_etf_data("AIQ", "AI相关ETF")

        return {
            "nvda": self.get_equity_or_etf_data("NVDA", "英伟达"),
            "qqq": self.get_equity_or_etf_data("QQQ", "纳斯达克100 ETF"),
            "ai_etf": ai_etf,
            "amd": self.get_equity_or_etf_data("AMD", "AMD"),
        }

    def get_semiconductor_data(self) -> dict[str, dict[str, Any]]:
        """Return the first semiconductor market data pack."""
        return {
            "soxx": self.get_equity_or_etf_data("SOXX", "半导体ETF"),
            "nvda": self.get_equity_or_etf_data("NVDA", "英伟达"),
            "amd": self.get_equity_or_etf_data("AMD", "AMD"),
            "tsm": self.get_equity_or_etf_data("TSM", "台积电"),
        }

    def get_sector_data(self, symbol: str) -> dict[str, Any]:
        """Return sector/index proxy data for the provided Yahoo symbol."""
        yfinance_result = self._fetch_yahoo_history(
            symbol=symbol,
            label=symbol or "板块指标",
            source=f"Yahoo Finance: {symbol}",
        )
        if not yfinance_result.get("is_mock"):
            return yfinance_result
        return self._mock_with_log(label=symbol or "板块指标", source="Market data unavailable")

    def _fetch_akshare_gold(self) -> dict[str, Any]:
        """Try AkShare gold data with several known interfaces."""
        if ak is None:
            return self._mock_market_data(label="黄金价格代理", source="AkShare unavailable")

        start, end = self._date_range()
        candidates: list[Callable[[], pd.DataFrame]] = []
        if hasattr(ak, "spot_hist_sge"):
            candidates.extend(
                [
                    lambda: ak.spot_hist_sge(symbol="Au99.99"),
                    lambda: ak.spot_hist_sge(symbol="Au(T+D)"),
                ]
            )
        if hasattr(ak, "futures_foreign_hist"):
            candidates.append(lambda: ak.futures_foreign_hist(symbol="XAU"))
        if hasattr(ak, "index_investing_global"):
            candidates.append(
                lambda: ak.index_investing_global(
                    country="美国",
                    index_name="Gold",
                    period="每日",
                    start_date=start,
                    end_date=end,
                )
            )

        return self._first_valid_akshare_result(
            candidates=candidates,
            label="黄金价格代理",
            source="AkShare",
        )

    def _fetch_akshare_dxy(self) -> dict[str, Any]:
        """Try AkShare Dollar Index data."""
        if ak is None:
            return self._mock_market_data(label="美元指数", source="AkShare unavailable")

        start, end = self._date_range()
        candidates: list[Callable[[], pd.DataFrame]] = []
        if hasattr(ak, "index_investing_global"):
            candidates.append(
                lambda: ak.index_investing_global(
                    country="美国",
                    index_name="美元指数",
                    period="每日",
                    start_date=start,
                    end_date=end,
                )
            )
        if hasattr(ak, "currency_hist"):
            candidates.append(
                lambda: ak.currency_hist(
                    symbol="美元指数",
                    period="每日",
                    start_date=start,
                    end_date=end,
                )
            )

        return self._first_valid_akshare_result(
            candidates=candidates,
            label="美元指数",
            source="AkShare",
        )

    def _fetch_akshare_us10y(self) -> dict[str, Any]:
        """Try AkShare US 10-year Treasury yield data."""
        if ak is None:
            return self._mock_market_data(label="10年期美债收益率", source="AkShare unavailable")

        start, _ = self._date_range()
        candidates: list[Callable[[], pd.DataFrame]] = []
        if hasattr(ak, "bond_zh_us_rate"):
            candidates.append(lambda: ak.bond_zh_us_rate(start_date=start))
        if hasattr(ak, "macro_bank_usa_interest_rate"):
            candidates.append(lambda: ak.macro_bank_usa_interest_rate())

        return self._first_valid_akshare_result(
            candidates=candidates,
            label="10年期美债收益率",
            source="AkShare + Macro Data",
            preferred_close_keywords=["10", "十年", "10年", "美国:国债收益率:10年"],
        )

    def _first_valid_akshare_result(
        self,
        candidates: list[Callable[[], pd.DataFrame]],
        label: str,
        source: str,
        preferred_close_keywords: list[str] | None = None,
    ) -> dict[str, Any]:
        for candidate in candidates:
            try:
                data_frame = candidate()
                result = self._normalize_dataframe_result(
                    data_frame=data_frame,
                    label=label,
                    source=source,
                    preferred_close_keywords=preferred_close_keywords,
                )
                if not result.get("is_mock"):
                    self._log_source("AKSHARE", label)
                    return result
            except Exception:
                continue
        return self._mock_market_data(label=label, source=source)

    def _fetch_yahoo_history(
        self,
        symbol: str,
        label: str,
        source: str,
    ) -> dict[str, Any]:
        """Fetch one year of Yahoo Finance history and normalize changes."""
        if yf is None:
            return self._mock_market_data(label=label, source="yfinance unavailable")

        try:
            ticker = yf.Ticker(symbol)
            history = ticker.history(period="1y", interval="1d", auto_adjust=False)
            result = self._normalize_dataframe_result(
                data_frame=history,
                label=label,
                source=source,
                close_columns=["Close"],
            )
            if not result.get("is_mock"):
                self._log_source("YFINANCE", label)
            return result
        except Exception:
            return self._mock_market_data(label=label, source=source)

    def _normalize_dataframe_result(
        self,
        data_frame: pd.DataFrame | None,
        label: str,
        source: str,
        close_columns: list[str] | None = None,
        preferred_close_keywords: list[str] | None = None,
    ) -> dict[str, Any]:
        if data_frame is None or data_frame.empty:
            return self._mock_market_data(label=label, source=source)

        close = self._extract_close_series(
            data_frame,
            close_columns=close_columns,
            preferred_close_keywords=preferred_close_keywords,
        )
        if close.empty:
            return self._mock_market_data(label=label, source=source)

        close = pd.to_numeric(close, errors="coerce").dropna()
        if close.empty:
            return self._mock_market_data(label=label, source=source)
        close = close.tail(252)

        current = float(close.iloc[-1])
        as_of = self._extract_as_of(data_frame, close)
        return {
            "label": label,
            "current": self._format_number(current),
            "change_1d": self._format_change(close, 1),
            "change_1m": self._format_change(close, 21),
            "change_3m": self._format_change(close, 63),
            "change_1y": self._format_change(close, len(close) - 1),
            "percentile_1y": self._format_percentile(close, current),
            "as_of": as_of,
            "period": "近1年",
            "source": source,
            "is_mock": False,
        }

    @staticmethod
    def _extract_close_series(
        data_frame: pd.DataFrame,
        close_columns: list[str] | None = None,
        preferred_close_keywords: list[str] | None = None,
    ) -> pd.Series:
        close_columns = close_columns or []
        common_columns = [
            "Close",
            "close",
            "收盘",
            "收盘价",
            "最新价",
            "价格",
            "现价",
            "value",
            "数值",
        ]
        for column in [*close_columns, *common_columns]:
            if column in data_frame.columns:
                return data_frame[column]

        preferred_close_keywords = preferred_close_keywords or []
        for keyword in preferred_close_keywords:
            for column in data_frame.columns:
                if keyword in str(column):
                    return data_frame[column]

        numeric_frame = data_frame.select_dtypes(include="number")
        if numeric_frame.empty:
            return pd.Series(dtype="float64")
        return numeric_frame.iloc[:, -1]

    @staticmethod
    def _extract_as_of(data_frame: pd.DataFrame, close: pd.Series) -> str:
        date_columns = ["日期", "date", "Date", "时间", "time"]
        for column in date_columns:
            if column in data_frame.columns:
                value = data_frame[column].dropna().iloc[-1]
                parsed = pd.to_datetime(value, errors="coerce")
                if pd.notna(parsed):
                    return parsed.date().isoformat()
                return str(value)

        if len(close.index) > 0:
            index_value = close.index[-1]
            parsed = pd.to_datetime(index_value, errors="coerce")
            if pd.notna(parsed):
                return parsed.date().isoformat()
            return str(index_value)
        return ""

    @staticmethod
    def _format_number(value: float) -> str:
        return f"{value:.2f}"

    @staticmethod
    def _format_change(close: pd.Series, offset: int) -> str:
        if len(close) < 2:
            return ""
        safe_offset = min(max(offset, 1), len(close) - 1)
        base = float(close.iloc[-1 - safe_offset])
        current = float(close.iloc[-1])
        if base == 0:
            return ""
        return f"{((current / base) - 1) * 100:.2f}%"

    @staticmethod
    def _format_percentile(close: pd.Series, current: float) -> str:
        if len(close) < 2:
            return ""
        percentile = (close <= current).mean() * 100
        return f"{percentile:.0f}%"

    @staticmethod
    def _date_range() -> tuple[str, str]:
        end = datetime.now().date()
        start = end - timedelta(days=370)
        return start.strftime("%Y%m%d"), end.strftime("%Y%m%d")

    def _mock_with_log(self, label: str, source: str) -> dict[str, Any]:
        self._log_source("MOCK", label)
        return self._mock_market_data(label=label, source=source)

    @staticmethod
    def _mock_market_data(**overrides: Any) -> dict[str, Any]:
        """Return an internal unavailable-data state."""
        data = MARKET_DATA_DEFAULT.copy()
        data.update(overrides)
        data["is_mock"] = True
        return data

    @staticmethod
    def _log_source(source: str, label: str) -> None:
        logger.info("Market Data Source: %s | %s", source, label)


if __name__ == "__main__":
    import json
    import logging

    logging.basicConfig(level=logging.INFO)
    service = MarketDataService()
    print("gold")
    print(json.dumps(service.get_gold_data(), ensure_ascii=False, indent=2))
    print("dxy")
    print(json.dumps(service.get_dxy_data(), ensure_ascii=False, indent=2))
    print("us10y")
    print(json.dumps(service.get_us10y_data(), ensure_ascii=False, indent=2))
