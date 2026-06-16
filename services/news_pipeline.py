"""Multi-source news retrieval pipeline for Event Analysis.

This pipeline aggregates AkShare and RSS feeds, filters by expanded event
keywords, ranks matches, and prepares a lightweight context string for the
Event Analysis prompt. It does not call any LLM.
"""

from __future__ import annotations

import re
import traceback
from html import unescape
from typing import Any

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


RSS_FEEDS = [
    {
        "source": "Yahoo Finance",
        "url": "https://finance.yahoo.com/news/rssindex",
    },
    {
        "source": "CNBC",
        "url": "https://www.cnbc.com/id/100003114/device/rss/rss.html",
    },
    {
        "source": "MarketWatch",
        "url": "https://feeds.content.dowjones.io/public/rss/mw_topstories",
    },
]

PREFERRED_RSS_SOURCES = {"Yahoo Finance", "CNBC", "MarketWatch"}


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
    return any(keyword.lower() in haystack for keyword in keywords if keyword)


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
        if keyword in title:
            score += 3
        if keyword in summary:
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


def fetch_akshare_news(limit: int = 50) -> list[dict[str, str]]:
    """Fetch AkShare macro news with safe fallback."""
    if AkShareService is None:
        return []
    try:
        service = AkShareService()
        news_items = service.get_macro_news(limit=limit)
        return news_items if isinstance(news_items, list) else []
    except Exception:
        print("[news_pipeline] AkShare exception:")
        traceback.print_exc()
        return []


def fetch_rss_news(limit: int = 50) -> list[dict[str, str]]:
    """Fetch and normalize RSS news from configured feeds."""
    if feedparser is None or requests is None:
        return []
    records: list[dict[str, str]] = []
    per_feed_limit = max(limit, 1)

    for feed in RSS_FEEDS:
        source = feed["source"]
        url = feed["url"]
        try:
            response = requests.get(
                url,
                timeout=15,
                headers={"User-Agent": "iFin/1.0 (+https://localhost)"},
            )
            response.raise_for_status()
            parsed = feedparser.parse(response.content)
            for entry in parsed.entries[:per_feed_limit]:
                records.append(
                    {
                        "title": _clean_html(entry.get("title", "")),
                        "summary": _clean_html(entry.get("summary", "")),
                        "source": source,
                        "date": entry.get("published", "") or entry.get("updated", ""),
                        "url": entry.get("link", ""),
                    }
                )
        except Exception:
            print(f"[news_pipeline] RSS exception: {source}")
            traceback.print_exc()

    return records[:limit]


def _rank_and_filter_news(news_items: list[dict[str, str]], keywords: list[str], limit: int = 5) -> list[dict[str, Any]]:
    """Filter, score, and rank news while preserving original order for ties."""
    scored_news = []
    for index, item in enumerate(news_items):
        if not _matches_query(item, keywords):
            continue
        score = _match_score(item, keywords)
        ranked_item = dict(item)
        ranked_item["_score"] = score
        ranked_item["_order"] = index
        scored_news.append(ranked_item)

    scored_news.sort(key=lambda item: (-item["_score"], item["_order"]))
    return scored_news[:limit]


def search_event_news(query: str) -> dict[str, Any]:
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
    }
    if not event:
        print("[news_pipeline] AkShare: 0")
        print("[news_pipeline] RSS: 0")
        print("[news_pipeline] merged deduped: 0")
        print("[news_pipeline] filtered: 0")
        return result

    akshare_news = fetch_akshare_news(limit=50)
    rss_news = fetch_rss_news(limit=50)
    print(f"[news_pipeline] AkShare: {len(akshare_news)}")
    print(f"[news_pipeline] RSS: {len(rss_news)}")

    all_news = akshare_news + rss_news
    deduped_news = _dedupe_news(all_news)
    keywords = expand_query(event)
    print(f"Expanded keywords: {keywords}")
    print(f"Before filtering: {len(deduped_news)} articles")

    matched_news = _rank_and_filter_news(deduped_news, keywords, limit=5)
    print(f"After filtering: {len(matched_news)} articles")
    print(f"[news_pipeline] merged deduped: {len(deduped_news)}")

    result["news_count"] = len(matched_news)
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
        }
        for item in matched_news
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

    matched_news = _rank_and_filter_news(deduped_news, keywords, limit=5)
    context = _build_context(query, matched_news)
    titles = [item.get("title", "") for item in matched_news]

    print(f"After filtering: {len(matched_news)} articles")
    print("Final top titles + source + score:")
    for index, item in enumerate(matched_news, start=1):
        print(f"{index}. [{item.get('source', '')}] score={item.get('_score', 0)} {item.get('title', '')}")
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
