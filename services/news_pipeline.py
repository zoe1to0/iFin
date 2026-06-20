"""Multi-source news retrieval pipeline for Event Analysis.

This pipeline aggregates AkShare and RSS feeds, filters by expanded event
keywords, ranks matches, and prepares a lightweight context string for the
Event Analysis prompt. It does not call any LLM.
"""

from __future__ import annotations

import re
import traceback
import logging
import xml.etree.ElementTree as ET
from html import unescape
from typing import Any
from urllib.parse import quote_plus

try:
    import feedparser
except ModuleNotFoundError:
    feedparser = None

try:
    import requests
except ModuleNotFoundError:
    requests = None

try:
    import akshare as ak
except ModuleNotFoundError:
    ak = None

try:
    from services.akshare_service import AkShareService
except ModuleNotFoundError:
    try:
        from akshare_service import AkShareService
    except ModuleNotFoundError:
        AkShareService = None


logger = logging.getLogger(__name__)

RSS_FEEDS = [
    {"name": "Yahoo Finance", "url": "https://finance.yahoo.com/news/rssindex"},
    {"name": "CNBC", "url": "https://www.cnbc.com/id/100003114/device/rss/rss.html"},
    {"name": "MarketWatch", "url": "https://feeds.content.dowjones.io/public/rss/mw_topstories"},
]

SOURCE_CATALOG = {
    "Yahoo Finance": {"kind": "rss", "url": "https://finance.yahoo.com/news/rssindex"},
    "Yahoo Finance Ticker": {
        "kind": "rss",
        "url_template": "https://feeds.finance.yahoo.com/rss/2.0/headline?s={symbol}&region=US&lang=en-US",
    },
    "CNBC": {"kind": "rss", "url": "https://www.cnbc.com/id/100003114/device/rss/rss.html"},
    "MarketWatch": {"kind": "rss", "url": "https://feeds.content.dowjones.io/public/rss/mw_topstories"},
    "Federal Reserve": {"kind": "rss", "url": "https://www.federalreserve.gov/feeds/press_all.xml"},
    "BLS": {"kind": "rss", "url": "https://www.bls.gov/feed/bls_latest.rss"},
    "BEA": {"kind": "rss", "url": "https://apps.bea.gov/rss/rss.xml"},
    "CoinDesk": {"kind": "rss", "url": "https://www.coindesk.com/arc/outboundfeeds/rss/"},
    "Cointelegraph": {"kind": "rss", "url": "https://cointelegraph.com/rss"},
    "Google News Search": {
        "kind": "query_rss",
        "url_template": "https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en",
    },
    "Reuters": {"kind": "placeholder", "reason": "direct_feed_not_configured"},
    "Bloomberg": {"kind": "placeholder", "reason": "direct_feed_not_configured"},
    "Company IR": {"kind": "placeholder", "reason": "company_ir_adapter_not_configured"},
    "Tencent IR": {"kind": "placeholder", "reason": "tencent_ir_adapter_not_configured"},
    "FRED": {"kind": "placeholder", "reason": "official_release_adapter_not_configured"},
}

_FEED_CACHE: dict[str, tuple[list[dict[str, str]], dict[str, Any]]] = {}
_SOURCE_RUNTIME_FAILURES: dict[str, str] = {}

PREFERRED_RSS_SOURCES = {"Yahoo Finance", "CNBC", "MarketWatch"}
DEFAULT_RELEVANCE_THRESHOLD = 5


def _contains_term(text: str, term: str) -> bool:
    """Match short Latin tokens as words and longer terms as substrings."""
    haystack = (text or "").lower()
    needle = (term or "").strip().lower()
    if not needle:
        return False
    if re.fullmatch(r"[a-z0-9.\-]+", needle) and len(needle) <= 4:
        return bool(re.search(rf"(?<![a-z0-9]){re.escape(needle)}(?![a-z0-9])", haystack))
    return needle in haystack


def build_retrieval_strategy(
    query: str,
    interpretation: dict | None = None,
    topic_info: dict | None = None,
) -> dict[str, Any]:
    """Build strict, intent-aware mandatory term groups for retrieval."""
    normalized = " ".join((query or "").strip().split())
    lower_query = normalized.lower()
    interpretation = interpretation or {}
    topic_info = topic_info or {}

    def strategy(
        label: str,
        groups: list[list[str]],
        terms: list[str],
        threshold: int = DEFAULT_RELEVANCE_THRESHOLD,
        title_required_any: list[str] | None = None,
    ) -> dict:
        return {
            "label": label,
            "required_groups": groups,
            "terms": list(dict.fromkeys([*terms, normalized])),
            "threshold": threshold,
            "title_required_any": title_required_any or [],
        }

    # Named companies take precedence over their surrounding sectors.
    if any(term in lower_query for term in ["英伟达", "nvidia", "nvda"]):
        aliases = ["英伟达", "NVIDIA", "NVDA"]
        return strategy(
            "company:nvidia",
            [aliases],
            aliases + ["earnings", "GPU", "AI chip"],
            title_required_any=aliases,
        )
    if any(term in lower_query for term in ["腾讯", "tencent", "tcehy", "0700"]):
        company = ["腾讯", "Tencent", "TCEHY", "0700"]
        earnings = ["财报", "业绩", "earnings", "revenue", "profit"]
        groups = [company, earnings] if any(term in lower_query for term in ["财报", "业绩", "earnings"]) else [company]
        return strategy(
            "company:tencent",
            groups,
            company + earnings,
            title_required_any=company,
        )
    if any(term in lower_query for term in ["苹果", "apple", "aapl", "wwdc"]):
        aliases = ["Apple", "苹果", "AAPL", "WWDC"]
        if "wwdc" in lower_query:
            return strategy(
                "company:apple_wwdc",
                [["WWDC"]],
                aliases + ["developer", "iOS", "AI"],
                title_required_any=["WWDC"],
            )
        return strategy("company:apple", [aliases], aliases + ["developer", "iOS", "AI"], title_required_any=aliases)

    if any(term in lower_query for term in ["美国cpi", "cpi", "通胀数据", "consumer price"]):
        terms = ["CPI", "inflation", "通胀", "consumer price"]
        return strategy("macro:cpi", [terms], terms + ["core CPI", "Fed"])
    if any(term in lower_query for term in ["美国非农", "非农就业", "非农", "nfp", "nonfarm", "payrolls"]):
        terms = ["nonfarm", "payrolls", "NFP", "jobs report", "非农"]
        return strategy("macro:nonfarm", [terms], terms + ["employment", "就业"])
    if any(term in lower_query for term in ["美联储", "fed", "fomc", "降息", "rate cut"]):
        policy = ["美联储", "Federal Reserve", "Fed", "FOMC"]
        rate = ["降息", "加息", "利率", "rate cut", "rate hike", "interest rate"]
        return strategy("macro:fed", [policy, rate], policy + rate)

    if "ai芯片" in lower_query or (
        any(term in lower_query for term in ["ai", "人工智能"])
        and any(term in lower_query for term in ["芯片", "chip", "semiconductor", "gpu"])
    ):
        ai_terms = ["AI", "人工智能"]
        chip_terms = ["chip", "semiconductor", "GPU", "芯片", "半导体"]
        return strategy("industry:ai_chip", [ai_terms, chip_terms], ai_terms + chip_terms)
    if "机器人" in normalized or any(term in lower_query for term in ["robot", "robotics"]):
        terms = ["robot", "robotics", "机器人"]
        return strategy("industry:robotics", [terms], terms + ["humanoid"])
    if any(term in normalized for term in ["新能源车", "电动车"]) or any(
        term in lower_query for term in ["electric vehicle", "ev market"]
    ):
        terms = ["EV", "electric vehicle", "新能源车", "电动车"]
        return strategy("industry:ev", [terms], terms + ["battery", "电池"])

    if "黄金" in normalized or any(term in lower_query for term in ["gold", "bullion", "xau"]):
        terms = ["gold", "黄金", "bullion", "XAU"]
        return strategy("asset:gold", [terms], terms + ["gold ETF", "央行购金"])
    if any(term in normalized for term in ["原油", "布油"]) or any(
        term in lower_query for term in ["oil", "crude", "brent", "wti"]
    ):
        terms = ["oil", "crude", "Brent", "WTI", "原油", "布油"]
        return strategy("asset:oil", [terms], terms + ["OPEC"])
    if "比特币" in normalized or any(term in lower_query for term in ["bitcoin", "btc"]):
        terms = ["bitcoin", "BTC", "比特币"]
        return strategy("asset:bitcoin", [terms], terms + ["spot ETF", "crypto"])

    configured_terms = interpretation.get("search_keywords", []) or topic_info.get("search_expansion", []) or []
    terms = [str(term) for term in configured_terms if str(term).strip()]
    return strategy("general", [[normalized]] if normalized else [], terms or [normalized], threshold=4)


def build_query_variants(query: str) -> list[str]:
    """Return focused fallback searches without weakening relevance checks."""
    normalized = " ".join((query or "").strip().split())
    lower_query = normalized.lower()
    variants = [normalized] if normalized else []
    configured: list[str] = []
    if any(term in lower_query for term in ["英伟达", "nvidia", "nvda"]):
        configured = ["Nvidia earnings", "Nvidia stock AI chips", "NVDA latest news"]
    elif any(term in lower_query for term in ["腾讯", "tencent", "tcehy", "0700"]):
        configured = ["Tencent earnings", "Tencent quarterly results", "0700.HK earnings"]
    elif any(term in lower_query for term in ["苹果", "apple", "wwdc"]):
        configured = ["Apple WWDC latest", "Apple WWDC AI", "AAPL developer conference"]
    elif "黄金" in normalized or "gold" in lower_query:
        configured = ["gold price Fed rate dollar", "XAUUSD gold ETF flows", "gold latest market news"]
    elif any(term in lower_query for term in ["原油", "布油", "oil", "brent", "wti"]):
        configured = ["crude oil latest news", "Brent oil OPEC", "WTI inventory market"]
    elif any(term in lower_query for term in ["比特币", "bitcoin", "btc"]):
        configured = ["Bitcoin latest news", "BTC spot ETF flows", "Bitcoin market regulation"]
    elif any(term in lower_query for term in ["美国cpi", "cpi", "通胀数据"]):
        configured = ["US CPI latest", "US inflation consumer prices", "core CPI Federal Reserve"]
    elif any(term in lower_query for term in ["美国非农", "非农", "nfp", "nonfarm"]):
        configured = ["US nonfarm payrolls latest", "NFP jobs report", "US payrolls Federal Reserve"]
    elif any(term in lower_query for term in ["美联储", "fed", "降息", "rate cut"]):
        configured = ["Federal Reserve rate cut", "Fed interest rate latest", "FOMC policy news"]
    elif "ai芯片" in lower_query:
        configured = ["AI chips latest news", "AI semiconductor GPU demand", "AI chip export controls"]
    elif "机器人" in normalized or "robot" in lower_query:
        configured = ["robotics latest news", "humanoid robot industry", "robot commercialization orders"]
    elif "新能源车" in normalized or "electric vehicle" in lower_query:
        configured = ["electric vehicle latest news", "EV sales market", "EV battery industry"]
    for variant in configured:
        if variant and variant.lower() not in {item.lower() for item in variants}:
            variants.append(variant)
    return variants[:4]


def _ticker_for_query(query: str) -> str:
    lower_query = (query or "").lower()
    for terms, symbol in [
        (["英伟达", "nvidia", "nvda"], "NVDA"),
        (["腾讯", "tencent", "tcehy", "0700"], "0700.HK"),
        (["苹果", "apple", "aapl", "wwdc"], "AAPL"),
        (["黄金", "gold", "xau"], "GC=F"),
        (["原油", "布油", "oil", "brent", "wti"], "CL=F"),
        (["比特币", "bitcoin", "btc"], "BTC-USD"),
        (["ai芯片", "ai chip"], "SOXX"),
        (["机器人", "robot", "robotics"], "BOTZ"),
        (["新能源车", "电动车", "electric vehicle", "ev market"], "DRIV"),
    ]:
        if any(term in lower_query for term in terms):
            return symbol
    return ""


def build_source_plan(
    query: str,
    interpretation: dict | None = None,
    topic_info: dict | None = None,
) -> list[dict[str, Any]]:
    """Build an ordered, topic-aware source plan including future placeholders."""
    interpretation = interpretation or {}
    topic_info = topic_info or {}
    intent = interpretation.get("primary_intent") or topic_info.get("primary_intent", "")
    topic_type = topic_info.get("topic_type", "general")
    lower_query = (query or "").lower()
    names = ["AkShare"]

    if intent in {"company_event", "earnings_event", "product_event"}:
        names += ["Yahoo Finance Ticker", "Google News Search", "CNBC", "MarketWatch", "Reuters", "Bloomberg"]
        names += ["Tencent IR" if any(term in lower_query for term in ["腾讯", "tencent", "0700"]) else "Company IR"]
    elif intent in {"macro_event", "macro_indicator"} or topic_type == "macro":
        names += ["Federal Reserve", "BLS", "BEA", "Google News Search", "CNBC", "MarketWatch", "FRED"]
    elif intent == "crypto_asset" or topic_type == "crypto":
        names += ["CoinDesk", "Cointelegraph", "Yahoo Finance Ticker", "Google News Search"]
    else:
        names += ["Yahoo Finance Ticker", "Google News Search", "CNBC", "MarketWatch", "Reuters", "Bloomberg"]

    symbol = _ticker_for_query(query)
    plan = []
    for name in names:
        if name == "AkShare":
            plan.append({"name": name, "kind": "api", "available": True})
            continue
        config = SOURCE_CATALOG[name]
        item = {"name": name, **config, "available": config.get("kind") != "placeholder"}
        if name == "Yahoo Finance Ticker":
            item["symbol"] = symbol
            if not symbol:
                item["available"] = False
                item["reason"] = "ticker_not_available"
        plan.append(item)
    return plan


def _extract_keywords(query: str) -> list[str]:
    """Extract simple keywords from a user query for title matching."""
    cleaned_query = query.strip()
    if not cleaned_query:
        return []

    keywords = [cleaned_query]
    parts = re.findall(r"[A-Za-z0-9]+|[\u4e00-\u9fff]{2,}", cleaned_query)
    for part in parts:
        if part not in keywords:
            keywords.append(part)
    return keywords


def expand_query(query: str) -> list[str]:
    """Expand common financial event queries into broader retrieval keywords."""
    keywords = _extract_keywords(query)
    normalized_query = query.lower()

    expansions: list[str] = []
    if any(term in query for term in ["黄金", "黄金股", "有色金属", "避险", "实际利率", "美元"]) or any(
        term in normalized_query for term in ["gold", "gold price", "safe haven", "real yield", "precious metals", "gold miners"]
    ):
        expansions.extend(
            [
                "黄金",
                "gold",
                "gold price",
                "safe haven",
                "real yield",
                "dollar",
                "precious metals",
                "gold miners",
                "黄金股",
                "有色金属",
                "避险",
                "实际利率",
                "美元",
                "central bank gold buying",
            ]
        )

    if any(term in query for term in ["美联储", "降息", "加息", "利率", "联储"]) or any(
        term in normalized_query for term in ["fed", "fomc", "rate cut", "interest rate"]
    ):
        expansions.extend(
            [
                "美联储",
                "Fed",
                "Federal Reserve",
                "FOMC",
                "降息",
                "rate cut",
                "interest rate",
                "rate",
            ]
        )

    if any(term in query for term in ["AI", "芯片", "半导体", "出口限制", "出口管制", "英伟达"]) or any(
        term in normalized_query
        for term in ["ai", "chip", "semiconductor", "nvidia", "export restriction", "export control"]
    ):
        expansions.extend(
            [
                "AI",
                "chip",
                "chips",
                "semiconductor",
                "semiconductors",
                "NVIDIA",
                "Nvidia",
                "export restriction",
                "export control",
                "芯片",
                "半导体",
                "出口限制",
                "出口管制",
                "英伟达",
            ]
        )

    if any(term in normalized_query for term in ["earnings", "revenue", "profit"]) or any(
        term in query for term in ["财报", "业绩", "营收", "利润"]
    ):
        expansions.extend(["earnings", "revenue", "profit", "guidance", "财报", "业绩", "营收", "利润"])

    for keyword in expansions:
        if keyword not in keywords:
            keywords.append(keyword)
    return keywords


def _clean_html(text: str) -> str:
    """Remove simple HTML tags from RSS summaries."""
    text = re.sub(r"<[^>]+>", " ", text or "")
    text = re.sub(r"\s+", " ", text)
    return unescape(text).strip()


def _matches_query(item: dict[str, str], keywords: list[str]) -> bool:
    """Return True when title or summary contains at least one keyword."""
    title = item.get("title", "")
    summary = item.get("summary", "")
    haystack = f"{title} {summary}".lower()
    return any(_contains_term(haystack, keyword) for keyword in keywords if keyword)


def _match_score(item: dict[str, str], keywords: list[str]) -> int:
    """Score news by keyword hits and preferred RSS sources."""
    title = item.get("title", "").lower()
    summary = item.get("summary", "").lower()
    source = item.get("source", "")
    score = 0
    for keyword in keywords:
        keyword = keyword.lower()
        if not keyword:
            continue
        if _contains_term(title, keyword):
            score += 3
        if _contains_term(summary, keyword):
            score += 1
    if source in PREFERRED_RSS_SOURCES:
        score += 1
    return score


def _dedupe_news(news_items: list[dict[str, str]]) -> list[dict[str, str]]:
    """Deduplicate news by URL first, then by title."""
    seen = set()
    deduped = []
    for item in news_items:
        key = item.get("url") or item.get("title")
        key = (key or "").strip().lower()
        if not key or key in seen:
            continue
        seen.add(key)
        deduped.append(item)
    return deduped


def _build_context(event: str, news_items: list[dict[str, str]]) -> str:
    """Merge filtered news into a compact event context string."""
    if not news_items:
        return ""

    context_blocks = [f"Event query: {event}"]
    for index, item in enumerate(news_items, start=1):
        title = item.get("title", "")
        source = item.get("source", "")
        date = item.get("date", "")
        summary = item.get("summary", "")
        url = item.get("url", "")
        context_blocks.append(
            "\n".join(
                [
                    f"{index}. Title: {title}",
                    f"Source: {source}",
                    f"Date: {date}",
                    f"Summary: {summary}",
                    f"URL: {url}",
                ]
            )
        )
    return "\n\n".join(context_blocks)


def fetch_akshare_news(
    limit: int = 50,
    diagnostics: dict[str, Any] | None = None,
) -> list[dict[str, str]]:
    """Fetch AkShare macro news with safe fallback."""
    diagnostics = diagnostics if diagnostics is not None else {}
    diagnostics.setdefault("attempted_sources", [])
    diagnostics.setdefault("successful_sources", [])
    diagnostics.setdefault("failed_sources", [])
    diagnostics["attempted_sources"].append("AkShare")
    if AkShareService is None:
        diagnostics["failed_sources"].append({"source": "AkShare", "reason": "service_unavailable"})
        return []
    try:
        service = AkShareService()
        news_items = service.get_macro_news(limit=limit)
        records = news_items if isinstance(news_items, list) else []
        diagnostics["successful_sources"].append({"source": "AkShare", "item_count": len(records)})
        return records
    except Exception as exc:
        diagnostics["failed_sources"].append(
            {"source": "AkShare", "reason": f"{type(exc).__name__}:{exc}"}
        )
        logger.exception("AkShare retrieval failed")
        return []


def _parse_feed_content(content: bytes, default_source: str, limit: int) -> list[dict[str, str]]:
    """Parse RSS/Atom with feedparser or a standard-library XML fallback."""
    if feedparser is not None:
        parsed = feedparser.parse(content)
        records = []
        for entry in parsed.entries[:limit]:
            entry_source = entry.get("source") or {}
            source = entry_source.get("title", "") if isinstance(entry_source, dict) else ""
            records.append(
                {
                    "title": _clean_html(entry.get("title", "")),
                    "summary": _clean_html(entry.get("summary", "") or entry.get("description", "")),
                    "source": source or default_source,
                    "date": entry.get("published", "") or entry.get("updated", ""),
                    "url": entry.get("link", ""),
                }
            )
        return records

    root = ET.fromstring(content)

    def local_name(element: ET.Element) -> str:
        return element.tag.rsplit("}", 1)[-1].lower()

    def child_text(element: ET.Element, *names: str) -> str:
        wanted = {name.lower() for name in names}
        for child in list(element):
            if local_name(child) in wanted:
                return "".join(child.itertext()).strip()
        return ""

    records = []
    entries = [element for element in root.iter() if local_name(element) in {"item", "entry"}]
    for entry in entries[:limit]:
        link = child_text(entry, "link")
        if not link:
            for child in list(entry):
                if local_name(child) == "link" and child.attrib.get("href"):
                    link = child.attrib["href"]
                    break
        records.append(
            {
                "title": _clean_html(child_text(entry, "title")),
                "summary": _clean_html(child_text(entry, "description", "summary", "content")),
                "source": _clean_html(child_text(entry, "source")) or default_source,
                "date": child_text(entry, "pubdate", "published", "updated", "date"),
                "url": link,
            }
        )
    return records


def _fetch_feed_url(url: str, source: str, limit: int) -> tuple[list[dict[str, str]], dict[str, Any]]:
    if url in _FEED_CACHE:
        records, status = _FEED_CACHE[url]
        return list(records), dict(status)
    status: dict[str, Any] = {
        "source": source,
        "url": url,
        "request_status": "not_started",
        "http_status": None,
        "parse_status": "not_started",
        "item_count": 0,
        "error": "",
        "timed_out": False,
    }
    if requests is None:
        status.update(request_status="failed", error="requests_not_installed")
        return [], status
    try:
        response = requests.get(
            url,
            timeout=12,
            headers={"User-Agent": "Mozilla/5.0 (compatible; iFin/1.0; +https://localhost)"},
        )
        status["http_status"] = response.status_code
        if response.status_code >= 400:
            status.update(request_status="failed", error=f"http_{response.status_code}")
            logger.warning("RSS request failed: %s %s HTTP %s", source, url, response.status_code)
            _FEED_CACHE[url] = ([], status)
            return [], status
        status["request_status"] = "success"
        try:
            records = _parse_feed_content(response.content, source, limit)
            status["parse_status"] = "success"
            status["item_count"] = len(records)
            if not records:
                status["error"] = "parsed_zero_items"
            _FEED_CACHE[url] = (records, status)
            return records, status
        except Exception as exc:
            status.update(parse_status="failed", error=f"parse_error:{type(exc).__name__}:{exc}")
            logger.exception("RSS parse failed: %s %s", source, url)
            _FEED_CACHE[url] = ([], status)
            return [], status
    except requests.Timeout as exc:
        status.update(request_status="failed", error=f"timeout:{exc}", timed_out=True)
        logger.warning("RSS request timed out: %s %s", source, url)
    except Exception as exc:
        status.update(request_status="failed", error=f"request_error:{type(exc).__name__}:{exc}")
        logger.exception("RSS request failed: %s %s", source, url)
    _FEED_CACHE[url] = ([], status)
    return [], status


def fetch_rss_news(
    limit: int = 50,
    source_plan: list[dict[str, Any]] | None = None,
    query_variants: list[str] | None = None,
    diagnostics: dict[str, Any] | None = None,
) -> list[dict[str, str]]:
    """Fetch planned RSS sources and expose request/parse diagnostics."""
    plan = source_plan or [
        {"name": item["name"], "kind": "rss", "url": item["url"], "available": True}
        for item in RSS_FEEDS
    ]
    variants = query_variants or []
    records: list[dict[str, str]] = []
    diagnostics = diagnostics if diagnostics is not None else {}
    diagnostics.setdefault("attempted_sources", [])
    diagnostics.setdefault("successful_sources", [])
    diagnostics.setdefault("failed_sources", [])
    per_source_limit = max(limit, 1)

    for source in plan:
        name = source.get("name", "")
        kind = source.get("kind", "")
        if name == "AkShare" or not source.get("available", False) or kind == "placeholder":
            continue
        if name in _SOURCE_RUNTIME_FAILURES:
            diagnostics["failed_sources"].append(
                {
                    "source": name,
                    "reason": f"runtime_disabled:{_SOURCE_RUNTIME_FAILURES[name]}",
                    "requests": [],
                }
            )
            continue
        urls = []
        if kind == "query_rss":
            urls = [
                source["url_template"].format(query=quote_plus(variant))
                for variant in variants[:3]
                if variant
            ]
        elif source.get("url_template") and source.get("symbol"):
            urls = [source["url_template"].format(symbol=quote_plus(source["symbol"]))]
        elif source.get("url"):
            urls = [source["url"]]
        if not urls:
            continue

        diagnostics["attempted_sources"].append(name)
        source_records = []
        statuses = []
        for url in urls:
            fetched, status = _fetch_feed_url(url, name, per_source_limit)
            source_records.extend(fetched)
            statuses.append(status)
            if status.get("timed_out"):
                _SOURCE_RUNTIME_FAILURES[name] = status.get("error", "timeout")
                break
        records.extend(source_records)
        successful = [status for status in statuses if status.get("request_status") == "success" and status.get("parse_status") == "success"]
        if successful:
            diagnostics["successful_sources"].append(
                {
                    "source": name,
                    "item_count": len(source_records),
                    "requests": statuses,
                }
            )
        else:
            diagnostics["failed_sources"].append(
                {
                    "source": name,
                    "reason": "; ".join(status.get("error", "unknown_error") for status in statuses),
                    "requests": statuses,
                }
            )
    return records


def _evaluate_relevance(item: dict[str, str], strategy: dict) -> dict[str, Any]:
    title = item.get("title", "")
    summary = item.get("summary", "")
    haystack = f"{title} {summary}"
    terms = strategy.get("terms", []) or []
    matched_terms = [term for term in terms if _contains_term(haystack, term)]
    missing_groups = [
        group
        for group in strategy.get("required_groups", []) or []
        if not any(_contains_term(haystack, term) for term in group)
    ]
    score = _match_score(item, terms)
    if not missing_groups:
        score += 2 * len(strategy.get("required_groups", []) or [])
    reject_reason = ""
    title_required = strategy.get("title_required_any", []) or []
    if title_required and not any(_contains_term(title, term) for term in title_required):
        reject_reason = "missing_title_anchor"
    elif missing_groups:
        reject_reason = "missing_required_terms"
    elif score < int(strategy.get("threshold", DEFAULT_RELEVANCE_THRESHOLD)):
        reject_reason = "below_relevance_threshold"
    evaluated = dict(item)
    evaluated["relevance_score"] = score
    evaluated["matched_terms"] = list(dict.fromkeys(matched_terms))
    evaluated["reject_reason"] = reject_reason
    return evaluated


def _rank_and_filter_news(
    news_items: list[dict[str, str]],
    strategy: dict,
    limit: int = 5,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Evaluate, filter, and rank news while retaining rejection metadata."""
    scored_news = []
    evaluated_news = []
    for index, item in enumerate(news_items):
        evaluated = _evaluate_relevance(item, strategy)
        evaluated["_order"] = index
        evaluated_news.append(evaluated)
        if evaluated.get("reject_reason"):
            continue
        scored_news.append(evaluated)

    scored_news.sort(key=lambda item: (-item["relevance_score"], item["_order"]))
    return scored_news[:limit], evaluated_news


def search_event_news(
    query: str,
    interpretation: dict | None = None,
    topic_info: dict | None = None,
) -> dict[str, Any]:
    """Search multi-source news and return filtered event context."""
    event = query.strip()
    print(f"[news_pipeline] query: {event}")
    print("[news_pipeline] data sources: AkShare, RSS")
    result = {
        "event": event,
        "news_count": 0,
        "sources": [],
        "titles": [],
        "context": "",
        "items": [],
        "evaluated_items": [],
        "filtered_count": 0,
        "rejected_count": 0,
        "evidence_status": "insufficient",
        "retrieval_strategy": {},
        "source_plan": [],
        "attempted_sources": [],
        "successful_sources": [],
        "failed_sources": [],
        "query_variants": [],
        "source_coverage_failure_reason": "",
    }
    if not event:
        print("[news_pipeline] AkShare: 0")
        print("[news_pipeline] RSS: 0")
        print("[news_pipeline] merged deduped: 0")
        print("[news_pipeline] filtered: 0")
        return result

    source_plan = build_source_plan(event, interpretation, topic_info)
    query_variants = build_query_variants(event)
    diagnostics: dict[str, Any] = {
        "attempted_sources": [],
        "successful_sources": [],
        "failed_sources": [],
    }
    akshare_news = fetch_akshare_news(limit=50, diagnostics=diagnostics)
    rss_news = fetch_rss_news(
        limit=50,
        source_plan=source_plan,
        query_variants=query_variants,
        diagnostics=diagnostics,
    )
    print(f"[news_pipeline] AkShare: {len(akshare_news)}")
    print(f"[news_pipeline] RSS: {len(rss_news)}")

    all_news = akshare_news + rss_news
    deduped_news = _dedupe_news(all_news)
    strategy = build_retrieval_strategy(event, interpretation, topic_info)
    keywords = strategy.get("terms", [])
    result["retrieval_strategy"] = strategy
    print(f"Retrieval strategy: {strategy.get('label', 'general')}")
    print(f"Expanded keywords: {keywords}")
    print(f"Before filtering: {len(deduped_news)} articles")

    matched_news, evaluated_news = _rank_and_filter_news(deduped_news, strategy, limit=5)
    print(f"After filtering: {len(matched_news)} articles")
    print(f"[news_pipeline] merged deduped: {len(deduped_news)}")

    result["news_count"] = len(matched_news)
    result["filtered_count"] = len(matched_news)
    result["rejected_count"] = len(evaluated_news) - len(matched_news)
    result["evidence_status"] = "sufficient" if matched_news else "insufficient"
    result["source_plan"] = [
        {
            "name": item.get("name", ""),
            "kind": item.get("kind", ""),
            "available": item.get("available", False),
            "reason": item.get("reason", ""),
        }
        for item in source_plan
    ]
    result["attempted_sources"] = diagnostics["attempted_sources"]
    result["successful_sources"] = diagnostics["successful_sources"]
    result["failed_sources"] = diagnostics["failed_sources"]
    result["query_variants"] = query_variants
    if not matched_news:
        failed_names = [item.get("source", "") for item in diagnostics["failed_sources"]]
        placeholders = [
            item.get("name", "")
            for item in source_plan
            if not item.get("available", False)
        ]
        reasons = []
        if failed_names:
            reasons.append(f"failed_sources={','.join(failed_names)}")
        if placeholders:
            reasons.append(f"unavailable_sources={','.join(placeholders)}")
        reasons.append("no_articles_passed_relevance_filter")
        result["source_coverage_failure_reason"] = "; ".join(reasons)
    result["sources"] = [
        {
            "source": item.get("source", ""),
            "date": item.get("date", ""),
            "url": item.get("url", ""),
        }
        for item in matched_news
    ]
    result["titles"] = [item.get("title", "") for item in matched_news]
    result["context"] = _build_context(event, matched_news)
    result["items"] = [
        {
            "title": item.get("title", ""),
            "source": item.get("source", ""),
            "date": item.get("date", ""),
            "url": item.get("url", ""),
            "summary": item.get("summary", ""),
            "relevance_score": item.get("relevance_score", 0),
            "matched_terms": item.get("matched_terms", []),
            "reject_reason": item.get("reject_reason", ""),
        }
        for item in matched_news
    ]
    result["evaluated_items"] = [
        {
            "title": item.get("title", ""),
            "source": item.get("source", ""),
            "url": item.get("url", ""),
            "relevance_score": item.get("relevance_score", 0),
            "matched_terms": item.get("matched_terms", []),
            "reject_reason": item.get("reject_reason", ""),
        }
        for item in evaluated_news
    ]
    return result


def _debug_fetch_akshare_macro_news(limit: int = 50) -> list[dict[str, str]]:
    """Fetch AkShare macro news directly and print full exceptions for debugging."""
    print("[debug_news_search] calling data source: AkShare")
    if ak is None:
        print("[debug_news_search] AkShare unavailable: module not installed")
        return []
    try:
        df = ak.stock_news_main_cx()
        if df is None or df.empty:
            print("[debug_news_search] AkShare raw rows: 0")
            return []

        print(f"[debug_news_search] AkShare raw rows: {len(df)}")
        records = []
        for _, row in df.head(max(limit, 0)).iterrows():
            summary = str(row.get("summary", "") or "")
            records.append(
                {
                    "title": str(row.get("title", "") or "") or summary[:60],
                    "source": str(row.get("source", "") or row.get("tag", "") or "AkShare"),
                    "date": str(row.get("date", "") or ""),
                    "url": str(row.get("url", "") or ""),
                    "summary": summary,
                }
            )
        return records
    except Exception:
        print("[debug_news_search] AkShare exception:")
        traceback.print_exc()
        return []


def debug_news_search(query: str) -> dict[str, Any]:
    """Print verbose diagnostics for a news search without changing app logic."""
    print(f"\n=== DEBUG NEWS SEARCH: {query} ===")
    print(f"User input keyword: {query}")
    print("Data sources called: AkShare, RSS")

    akshare_news = _debug_fetch_akshare_macro_news(limit=50)
    rss_news = fetch_rss_news(limit=50)
    print(f"AkShare: {len(akshare_news)}")
    print(f"RSS: {len(rss_news)}")

    all_news = akshare_news + rss_news
    deduped_news = _dedupe_news(all_news)
    keywords = expand_query(query)
    print(f"Expanded keywords: {keywords}")
    print(f"Merged deduped count: {len(deduped_news)}")
    print(f"Before filtering: {len(deduped_news)} articles")

    strategy = build_retrieval_strategy(query)
    matched_news, _ = _rank_and_filter_news(deduped_news, strategy, limit=5)
    context = _build_context(query, matched_news)
    titles = [item.get("title", "") for item in matched_news]

    print(f"After filtering: {len(matched_news)} articles")
    print("Final top titles + source + score:")
    for index, item in enumerate(matched_news, start=1):
        print(f"{index}. [{item.get('source', '')}] score={item.get('relevance_score', 0)} {item.get('title', '')}")
    print(f"Context length: {len(context)}")

    return {
        "event": query,
        "raw_count": len(all_news),
        "deduped_count": len(deduped_news),
        "news_count": len(matched_news),
        "titles": titles,
        "context": context,
    }


if __name__ == "__main__":
    import json

    for test_query in ["美联储降息50bp", "Fed rate cut", "AI芯片出口限制", "Nvidia earnings"]:
        print(json.dumps(debug_news_search(test_query), ensure_ascii=False, indent=2))
