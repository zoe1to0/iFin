"""Adapter from the current Event result to the V2 Research Question Card pool."""

from __future__ import annotations

import re
from typing import Any

from services.historical_patterns import get_historical_patterns
from services.watch_metrics import get_watch_metrics


SCHEMA_VERSION = "event_evidence_explorer_v2.v1"
BUILDING_TEXT = "功能建设中。"


CARD_DEFINITIONS = [
    ("what_happened", "市场发生了什么？", "发生了什么", "event_summary"),
    ("why_it_happened", "为什么会这样？", "为什么", "logic_chain"),
    ("who_is_acting", "谁在行动？", "谁在行动", "evidence_pool"),
    ("market_reaction", "市场如何反应？", "市场反应", "evidence_pool"),
    ("supporting_evidence", "支持这个观点的依据？", "支持依据", "bull_case"),
    ("cautious_evidence", "为什么需要谨慎？", "谨慎依据", "bear_case"),
    ("historical_context", "过去发生过什么？", "历史参考", "historical_cases"),
    ("risk_location", "最大的风险在哪里？", "风险所在", "risk_radar"),
    ("noteworthy_data", "哪些数据值得关注？", "关注数据", "key_data"),
    ("what_to_watch", "后续应该关注什么？", "后续关注", "next_watch"),
]


ACTOR_KEYWORDS = {
    "央行与政策机构": [
        "美联储",
        "央行",
        "fed",
        "fomc",
        "central bank",
        "ecb",
        "pboc",
        "监管",
        "regulator",
        "政府",
    ],
    "ETF 与基金": ["etf", "基金", "fund"],
    "机构投资者": [
        "机构",
        "institution",
        "asset manager",
        "hedge fund",
        "投行",
        "bank",
    ],
    "产业资本与公司": [
        "产业资本",
        "资本开支",
        "capex",
        "management",
        "管理层",
        "company",
        "公司",
    ],
    "散户与主题资金": ["散户", "retail", "主题资金", "thematic"],
}

COMMENTARY_MARKERS = [
    "表示",
    "认为",
    "预计",
    "指出",
    "称",
    "押注",
    "分析师",
    "首席经济学家",
    "评级",
    "预估",
    "expects",
    "said",
    "says",
    "analyst",
    "forecast",
]

ACTION_PATTERN = re.compile(
    r"^(?P<actor>.{2,60}?)(?P<action>宣布|发布|推出|启动|签署|完成|收购|投资|增持|减持|暂停|批准|实施|提交|降息|加息|"
    r"announced|launched|released|signed|acquired|invested|approved|implemented|filed|cut rates|raised rates)",
    re.IGNORECASE,
)


REACTION_KEYWORDS = [
    "上涨",
    "下跌",
    "走强",
    "走弱",
    "反弹",
    "回落",
    "流入",
    "流出",
    "增持",
    "减持",
    "波动",
    "surge",
    "rise",
    "gain",
    "rally",
    "fall",
    "drop",
    "decline",
    "inflow",
    "outflow",
    "volatility",
]


def _as_list(value: Any) -> list:
    return value if isinstance(value, list) else []


def _text(value: Any) -> str:
    return str(value or "").strip()


def _sentences(value: Any, limit: int = 5) -> list[str]:
    text = _text(value)
    if not text:
        return []
    parts = re.split(r"(?<=[。！？.!?])\s*", text)
    return [part.strip() for part in parts if part.strip()][:limit]


def _dedupe_text(items: list[str], limit: int | None = None) -> list[str]:
    output = []
    seen = set()
    for item in items:
        cleaned = _text(item)
        key = cleaned.lower()
        if not cleaned or key in seen:
            continue
        seen.add(key)
        output.append(cleaned)
        if limit is not None and len(output) >= limit:
            break
    return output


def _evidence_map(result: dict) -> dict[str, dict]:
    return {
        _text(item.get("id")): item
        for item in _as_list(result.get("evidence_pool"))
        if isinstance(item, dict) and _text(item.get("id"))
    }


def _source_from_evidence(item: dict) -> dict:
    return {
        "name": _text(item.get("source")) or "公开新闻",
        "title": _text(item.get("title")),
        "url": _text(item.get("url")),
        "published_at": _text(item.get("date")),
        "evidence_id": _text(item.get("id")),
    }


def _sources_for_items(items: list, result: dict, limit: int = 5) -> list[dict]:
    evidence = _evidence_map(result)
    sources = []
    seen = set()
    for item in items:
        if not isinstance(item, dict):
            continue
        evidence_ids = item.get("evidence_ids")
        if isinstance(evidence_ids, list):
            for evidence_id in evidence_ids:
                evidence_item = evidence.get(_text(evidence_id))
                if evidence_item:
                    source = _source_from_evidence(evidence_item)
                    key = source["evidence_id"] or source["url"] or source["title"]
                    if key and key not in seen:
                        seen.add(key)
                        sources.append(source)
        direct_url = _text(item.get("url"))
        direct_name = _text(item.get("source"))
        if direct_url or direct_name:
            source = {
                "name": direct_name or "公开新闻",
                "title": "",
                "url": direct_url,
                "published_at": "",
                "evidence_id": "",
            }
            key = direct_url or direct_name.lower()
            if key not in seen:
                seen.add(key)
                sources.append(source)
        if len(sources) >= limit:
            break
    return sources[:limit]


def _pool_sources(result: dict, limit: int = 5) -> list[dict]:
    return [
        _source_from_evidence(item)
        for item in _as_list(result.get("evidence_pool"))[:limit]
        if isinstance(item, dict)
    ]


def _card(
    card_id: str,
    title: str,
    short_title: str,
    summary: str,
    key_points: list[str],
    expanded_sections: list[dict],
    sources: list[dict],
    source_type: str,
    original_module_mapping: str,
) -> dict:
    return {
        "id": card_id,
        "title": title,
        "short_title": short_title,
        "card_summary": summary,
        "key_points": _dedupe_text(key_points),
        "expanded_sections": expanded_sections,
        "sources": sources,
        "source_type": source_type,
        "original_module_mapping": original_module_mapping,
    }


def _what_happened(result: dict) -> dict:
    summary = _text(result.get("event_summary"))
    points = _sentences(summary)
    return _card(
        "what_happened",
        "市场发生了什么？",
        "发生了什么",
        points[0] if points else "当前尚无可用事件摘要。",
        points,
        [{"id": "summary", "title": "完整事件摘要", "content": summary}]
        if summary
        else [],
        _pool_sources(result),
        "news_and_analysis",
        "event_summary",
    )


def _why_it_happened(result: dict) -> dict:
    items = [item for item in _as_list(result.get("logic_chain")) if isinstance(item, dict)]
    points = [
        "：".join(
            part
            for part in [_text(item.get("title")), _text(item.get("content"))]
            if part
        )
        for item in items
    ]
    sections = [
        {
            "id": _text(item.get("step")) or f"step_{index}",
            "title": _text(item.get("title")) or f"Step {index}",
            "content": _text(item.get("description")) or _text(item.get("content")),
        }
        for index, item in enumerate(items, start=1)
    ]
    return _card(
        "why_it_happened",
        "为什么会这样？",
        "为什么",
        "事件影响通过关键变量逐层传导。" if items else "当前尚无可用影响路径。",
        points,
        sections,
        _sources_for_items(items, result),
        "analysis_with_news_evidence",
        "logic_chain",
    )


def _news_text(item: dict) -> str:
    return " ".join(
        part
        for part in [_text(item.get("title")), _text(item.get("summary"))]
        if part
    )


def _extract_explicit_action(evidence: dict) -> tuple[str, str] | None:
    """Extract only explicit actor-action statements, excluding commentary."""
    candidates = [_text(evidence.get("title")), *_sentences(evidence.get("summary"), limit=5)]
    for candidate in candidates:
        lowered = candidate.lower()
        if not candidate or any(marker.lower() in lowered for marker in COMMENTARY_MARKERS):
            continue
        match = ACTION_PATTERN.search(candidate)
        if not match:
            continue
        actor = match.group("actor").strip(" ，,:：-—")
        if len(actor) < 2:
            continue
        return actor, candidate
    return None


def _who_is_acting(result: dict) -> dict:
    evidence_items = [
        item for item in _as_list(result.get("evidence_pool")) if isinstance(item, dict)
    ]
    matches = []
    matched_evidence = []
    for evidence in evidence_items:
        action = _extract_explicit_action(evidence)
        if action is None:
            continue
        actor, statement = action
        matches.append(f"{actor}：{statement}")
        matched_evidence.append(evidence)
    points = _dedupe_text(matches, limit=5)
    sections = [
        {
            "id": f"participant_{index}",
            "title": point.split("：", 1)[0],
            "content": point.split("：", 1)[-1],
        }
        for index, point in enumerate(points, start=1)
    ]
    return _card(
        "who_is_acting",
        "谁在行动？",
        "谁在行动",
        f"新闻证据中识别到 {len(points)} 条参与者行动线索。"
        if points
        else "当前新闻中未识别到明确行动主体。",
        points,
        sections,
        [_source_from_evidence(item) for item in matched_evidence[:5]],
        "news_extraction_v1",
        "evidence_pool",
    )


def _reaction_snippet(evidence: dict) -> str:
    title = _text(evidence.get("title"))
    summary = _text(evidence.get("summary"))
    for sentence in _sentences(summary, limit=8):
        lowered = sentence.lower()
        if any(keyword.lower() in lowered for keyword in REACTION_KEYWORDS):
            return sentence
    return title


def _market_reaction(result: dict) -> dict:
    evidence_items = [
        item for item in _as_list(result.get("evidence_pool")) if isinstance(item, dict)
    ]
    matched = [
        item
        for item in evidence_items
        if any(keyword.lower() in _news_text(item).lower() for keyword in REACTION_KEYWORDS)
    ]
    points = _dedupe_text([_reaction_snippet(item) for item in matched], limit=5)
    sections = [
        {
            "id": f"reaction_{index}",
            "title": _text(item.get("title")) or f"市场反应 {index}",
            "content": _reaction_snippet(item),
        }
        for index, item in enumerate(matched[:5], start=1)
    ]
    return _card(
        "market_reaction",
        "市场如何反应？",
        "市场反应",
        f"新闻证据中识别到 {len(points)} 条市场反应线索。"
        if points
        else "当前新闻证据未提供明确市场反应。",
        points,
        sections,
        [_source_from_evidence(item) for item in matched[:5]],
        "news_extraction_v1",
        "evidence_pool",
    )


def _logic_card(
    result: dict,
    source_field: str,
    card_id: str,
    title: str,
    short_title: str,
    empty_summary: str,
) -> dict:
    items = [item for item in _as_list(result.get(source_field)) if isinstance(item, dict)]
    item_points = []
    seen = set()
    for item in items:
        point = (
            _text(item.get("point"))
            or _text(item.get("risk"))
            or _text(item.get("name"))
        )
        key = point.lower()
        if not point or key in seen:
            continue
        seen.add(key)
        item_points.append((item, point))
    points = [point for _, point in item_points]
    sections = [
        {
            "id": f"{card_id}_{index}",
            "title": point,
            "content": _text(item.get("detail"))
            or _text(item.get("reason"))
            or _text(item.get("explanation")),
        }
        for index, (item, point) in enumerate(item_points, start=1)
    ]
    return _card(
        card_id,
        title,
        short_title,
        points[0] if points else empty_summary,
        points,
        sections,
        _sources_for_items(items, result),
        "analysis_with_news_evidence",
        source_field,
    )


def _what_to_watch(result: dict) -> dict:
    items = [item for item in _as_list(result.get("next_watch")) if isinstance(item, dict)]
    item_points = []
    seen = set()
    for item in items:
        point = _text(item.get("item")) or _text(item.get("title"))
        key = point.lower()
        if not point or key in seen:
            continue
        seen.add(key)
        item_points.append((item, point))
    points = [point for _, point in item_points]
    sections = [
        {
            "id": f"watch_{index}",
            "title": point,
            "content": _text(item.get("description")) or _text(item.get("why")),
        }
        for index, (item, point) in enumerate(item_points, start=1)
    ]
    return _card(
        "what_to_watch",
        "后续应该关注什么？",
        "后续关注",
        points[0] if points else "当前尚无明确后续观察项。",
        points,
        sections,
        _sources_for_items(items, result),
        "analysis_with_news_evidence",
        "next_watch",
    )


def _building_card(
    card_id: str,
    title: str,
    short_title: str,
    original_module_mapping: str,
) -> dict:
    return _card(
        card_id,
        title,
        short_title,
        BUILDING_TEXT,
        [],
        [],
        [],
        "unavailable",
        original_module_mapping,
    )


def _historical_pattern_card(event_title: str) -> dict:
    data = get_historical_patterns(event_title)
    patterns = data.get("patterns", [])
    if not patterns:
        return _card(
            "historical_context",
            "过去发生过什么？",
            "历史参考",
            data.get("empty_message", "暂无匹配的历史模式。"),
            [],
            [],
            [],
            "rule_library_empty",
            "historical_patterns",
        )
    points = [
        f"{item.get('historical_event', '')}：{item.get('market_reaction', '')}"
        for item in patterns
    ]
    sections = [
        {
            "id": f"historical_pattern_{index}",
            "title": item.get("historical_event", ""),
            "content": (
                f"触发因素：{item.get('trigger', '')}\n"
                f"市场反应：{item.get('market_reaction', '')}\n"
                f"当前相似点：{item.get('current_similarity', '')}"
            ),
            "historical_event": item.get("historical_event", ""),
            "trigger": item.get("trigger", ""),
            "market_reaction": item.get("market_reaction", ""),
            "current_similarity": item.get("current_similarity", ""),
        }
        for index, item in enumerate(patterns, start=1)
    ]
    return _card(
        "historical_context",
        "过去发生过什么？",
        "历史参考",
        patterns[0].get("historical_event", ""),
        points,
        sections,
        [],
        "rule_library",
        "historical_patterns",
    )


def _watch_metrics_card(event_title: str) -> dict:
    data = get_watch_metrics(event_title)
    metrics = data.get("metrics", [])
    if not metrics:
        return _card(
            "noteworthy_data",
            "哪些数据值得关注？",
            "关注数据",
            data.get("empty_message", "暂无匹配的关注指标。"),
            [],
            [],
            [],
            "rule_library_empty",
            "watch_metrics",
        )
    points = [f"{item.get('metric', '')}：{item.get('reason', '')}" for item in metrics]
    sections = [
        {
            "id": f"watch_metric_{index}",
            "title": item.get("metric", ""),
            "content": item.get("reason", ""),
            "metric": item.get("metric", ""),
            "reason": item.get("reason", ""),
        }
        for index, item in enumerate(metrics, start=1)
    ]
    return _card(
        "noteworthy_data",
        "哪些数据值得关注？",
        "关注数据",
        f"建议重点观察 {len(metrics)} 项相关数据。",
        points,
        sections,
        [],
        "rule_library",
        "watch_metrics",
    )


def build_event_v2_card_pool(event_result: dict, event_title: str = "") -> dict:
    """Return the V2 card pool without mutating the legacy Event result."""
    result = event_result if isinstance(event_result, dict) else {}
    cards = [
        _what_happened(result),
        _why_it_happened(result),
        _who_is_acting(result),
        _market_reaction(result),
        _logic_card(
            result,
            "bull_case",
            "supporting_evidence",
            "支持这个观点的依据？",
            "支持依据",
            "当前尚无可用支持依据。",
        ),
        _logic_card(
            result,
            "bear_case",
            "cautious_evidence",
            "为什么需要谨慎？",
            "谨慎依据",
            "当前尚无可用谨慎依据。",
        ),
        _historical_pattern_card(event_title),
        _logic_card(
            result,
            "risk_radar",
            "risk_location",
            "最大的风险在哪里？",
            "风险所在",
            "当前尚无可用风险依据。",
        ),
        _watch_metrics_card(event_title),
        _what_to_watch(result),
    ]
    return {
        "schema_version": SCHEMA_VERSION,
        "event": _text(event_title),
        "cards": cards,
    }
