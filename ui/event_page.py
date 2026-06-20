from datetime import datetime
from html import escape
from html import unescape
import re
from urllib.parse import urlparse

import streamlit as st

from services.event_query_interpreter import interpret_event_query
from services.event_service import run_event_analysis
from ui.components import (
    EVENT_DEMO,
    get_event_analysis_result,
    render_event_section_title,
)


EMPTY_STRUCTURED_TEXT = "暂无结构化数据"
ANALYSIS_EMPTY_TEXT = "暂无结构化分析结果"
SOFT_UNCERTAINTY_TEXT = "当前公开信息不足，暂不做强判断。"
DATA_SUPPORT_TEXT = "暂无足够数据支持。"
MORE_EVIDENCE_TEXT = "需要更多新闻或数据验证。"
MARKET_DATA_PENDING_TEXT = "待数据接入"
MARKET_DATA_NOTE_TEXT = "当前为新闻语境判断，非实时行情计算"
DEFAULT_SOURCE_TEXT = "来源：公开新闻"
KNOWN_SOURCE_NAMES = {
    "finance.yahoo": "Yahoo Finance",
    "yahoo finance": "Yahoo Finance",
    "cnbc": "CNBC",
    "marketwatch": "MarketWatch",
    "akshare": "AkShare",
    "caixin": "财新",
    "财新": "财新",
    "wall street journal": "Wall Street Journal",
    "wsj": "Wall Street Journal",
    "reuters": "Reuters",
    "bloomberg": "Bloomberg",
}
INTERNAL_PLACEHOLDERS = {
    "",
    "none",
    "null",
    "evidence_insufficient",
    "暂无数据",
    "证据不足",
    "暂无解释",
    "暂无解释。",
    "暂无历史参考",
    "暂无历史参考。",
    "暂无结构化数据",
    "暂无结构化分析结果",
}
HTML_TAG_PATTERN = re.compile(r"</?(div|span|p|br)\b[^>]*>", re.IGNORECASE)


def clean_html_text(value):
    return HTML_TAG_PATTERN.sub("", unescape(str(value or ""))).strip()


def safe_get_list(value):
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, (str, dict)):
        return [value]
    return []


def safe_text(value, fallback=EMPTY_STRUCTURED_TEXT):
    if value is None:
        return fallback
    text = clean_html_text(value)
    return text or fallback


def display_text(value, fallback=SOFT_UNCERTAINTY_TEXT):
    text = safe_text(value, fallback)
    if text.strip().lower() in INTERNAL_PLACEHOLDERS:
        return fallback
    return text


def format_market_data_note(item):
    if not isinstance(item, dict):
        return ""
    return ""


def filter_visible_market_items(items):
    visible_items = []
    for item in safe_get_list(items):
        if isinstance(item, dict) and item.get("is_mock") is True:
            continue
        visible_items.append(item)
    return visible_items


def has_hidden_mock_market_items(items):
    return any(
        isinstance(item, dict) and item.get("is_mock") is True
        for item in safe_get_list(items)
    )


def get_real_market_data_items(result):
    if not isinstance(result, dict):
        return []
    real_items = safe_get_list(result.get("_real_market_data"))
    if real_items:
        return filter_visible_market_items(real_items)
    market_data = result.get("_market_data")
    if isinstance(market_data, dict):
        return filter_visible_market_items(list(market_data.values()))
    return []


def format_market_label(label):
    label_text = display_text(label, "市场指标")
    label_map = {
        "NVDA": "英伟达",
        "NVIDIA": "英伟达",
        "英伟达": "英伟达",
        "QQQ": "纳斯达克100 ETF",
        "SOXX": "半导体ETF",
        "BOTZ": "AI相关ETF",
        "AIQ": "AI相关ETF",
        "AMD": "AMD",
        "TSM": "台积电",
        "台积电": "台积电",
        "AI相关ETF": "AI相关ETF",
        "纳斯达克100 ETF": "纳斯达克100 ETF",
        "半导体ETF": "半导体ETF",
    }
    if label_text in label_map:
        return label_map[label_text]
    if label_text == "黄金价格代理":
        return "黄金（AU9999）"
    return label_text


def infer_market_unit(label, source=""):
    text = f"{label or ''} {source or ''}"
    if "黄金" in text and "ETF" not in text:
        return "元/克"
    if "美债" in text or "收益率" in text or "US10Y" in text or "^TNX" in text:
        return "%"
    if "美元指数" in text or "DXY" in text:
        return "点"
    if any(keyword in text for keyword in ["ETF", "GLD", "英伟达", "AMD", "台积电", "NVDA", "TSM"]):
        return "美元"
    return ""


def format_value_with_unit(value, unit):
    text = display_text(value, "待数据接入")
    if not unit or text == "待数据接入" or text.endswith(unit):
        return text
    return f"{text} {unit}"


def format_percent_text(value, fallback="待数据接入"):
    text = display_text(value, fallback)
    if text == fallback:
        return text
    try:
        number = float(text.replace("%", "").strip())
        return f"{number:.2f}%"
    except ValueError:
        return text


def percentile_insight(value):
    text = display_text(value, "")
    try:
        number = float(text.replace("%", "").strip())
    except ValueError:
        return "暂未形成历史分位判断"
    if number >= 80:
        return "接近过去一年高位区间"
    if number <= 20:
        return "接近过去一年低位区间"
    return "位于过去一年中部区域"


def format_market_source(source):
    text = display_text(source, "待数据接入")
    if "AkShare" in text:
        return "AkShare"
    if "Yahoo Finance" in text:
        return text
    return text


def _card_text(value, fallback=""):
    return escape(display_text(value, fallback), quote=True)


def _market_meta_html(lines):
    return "".join(
        f'<div class="ifin-market-card-meta">{escape(str(line), quote=True)}</div>'
        for line in lines
        if line
    )


def render_market_data_card(item, show_badge=False):
    title = _card_text(item.get("title"), "市场指标")
    current_value = _card_text(item.get("current_value"), "待数据接入")
    insight = _card_text(item.get("insight"), "")
    body = _card_text(item.get("body"), "")
    badge = _card_text(item.get("badge"), "已接入行情数据") if show_badge else ""
    trend = _card_text(item.get("trend"), "")
    progress_value = item.get("progress_value")

    meta_lines = [
        item.get("change_line_1"),
        item.get("change_line_2"),
        item.get("percentile_line"),
        *safe_get_list(item.get("extra_meta")),
        item.get("as_of_line"),
        item.get("source_line"),
        item.get("data_note"),
    ]
    badge_html = f'<span class="ifin-market-card-badge">{badge}</span>' if badge else ""
    trend_html = f'<span class="ifin-market-card-trend">{trend}</span>' if trend else ""
    insight_html = f'<div class="ifin-market-card-body">Insight：{insight}</div>' if insight else ""
    body_html = f'<div class="ifin-market-card-body">{body}</div>' if body else ""
    progress_html = ""
    if isinstance(progress_value, (int, float)):
        position = max(0, min(float(progress_value), 100))
        progress_html = f"""
            <div class="ifin-market-track">
                <span class="ifin-market-dot" style="left: {position}%;"></span>
            </div>
            <div class="ifin-market-track-labels"><span>低</span><span>高</span></div>
        """

    st.markdown(
        f"""
        <div class="ifin-market-card">
            <div class="ifin-market-card-head">
                <div class="ifin-market-card-title">{title}</div>
                {badge_html}
            </div>
            <div class="ifin-market-card-value">{current_value}</div>
            {trend_html}
            {progress_html}
            {body_html}
            {insight_html}
            <div class="ifin-market-card-meta-wrap">
                {_market_meta_html(meta_lines)}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_real_market_data_cards(items):
    cols = st.columns(min(len(items), 4) or 1)
    for column, item in zip(cols, items):
        with column:
            raw_label = item.get("label") or item.get("name")
            label = format_market_label(raw_label)
            source = format_market_source(item.get("source"))
            unit = infer_market_unit(label, source)
            current = format_value_with_unit(item.get("current"), unit)
            change_1d = format_percent_text(item.get("change_1d"))
            change_1m = format_percent_text(item.get("change_1m"))
            change_3m = format_percent_text(item.get("change_3m"))
            change_1y = format_percent_text(item.get("change_1y"))
            percentile_1y = format_percent_text(item.get("percentile_1y"), "暂不计算历史分位")
            insight = percentile_insight(percentile_1y)
            as_of = display_text(item.get("as_of"), "待数据接入")
            data_note = ""
            if as_of != "待数据接入":
                data_note = f"以 {as_of} 可得数据为基准。"
            render_market_data_card(
                {
                    "title": label,
                    "current_value": current,
                    "insight": insight,
                    "change_line_1": f"1日：{change_1d} · 1月：{change_1m}",
                    "change_line_2": f"3月：{change_3m} · 1年：{change_1y}",
                    "percentile_line": f"1年历史分位：{percentile_1y}",
                    "as_of_line": f"时间基准：{as_of}",
                    "source_line": f"数据来源：{source}",
                    "data_note": data_note,
                },
                show_badge=True,
            )


def _clean_url(value):
    text = safe_text(value, "")
    if not text or text.strip().lower() in INTERNAL_PLACEHOLDERS:
        return ""
    parsed = urlparse(text)
    if parsed.scheme in {"http", "https"} and parsed.netloc:
        return text
    return ""


def _source_from_url(url):
    parsed = urlparse(url)
    domain = parsed.netloc.lower().removeprefix("www.")
    for keyword, name in KNOWN_SOURCE_NAMES.items():
        if keyword in domain:
            return name
    if not domain:
        return ""
    parts = domain.split(".")
    return parts[-2].title() if len(parts) >= 2 else domain.title()


def _looks_like_article_title(text):
    if len(text) > 32:
        return True
    title_markers = ["：", ":", "，", ",", "；", ";", "。", "?", "？", "！", "!"]
    return any(marker in text for marker in title_markers)


def normalize_source_name(item):
    if not isinstance(item, dict):
        return ""

    url = _clean_url(item.get("url") or item.get("link") or item.get("source_url") or item.get("source"))
    source = safe_text(
        item.get("source")
        or item.get("publisher")
        or item.get("platform")
        or item.get("media"),
        "",
    )
    source_lower = source.lower()

    for keyword, name in KNOWN_SOURCE_NAMES.items():
        if keyword in source_lower:
            return name

    if url:
        return _source_from_url(url)

    if source and source_lower not in INTERNAL_PLACEHOLDERS and not _looks_like_article_title(source):
        return source

    return ""


def format_source_line(item, fallback=DEFAULT_SOURCE_TEXT):
    if not isinstance(item, dict):
        return fallback

    url = _clean_url(item.get("url") or item.get("link") or item.get("source_url") or item.get("source"))
    source_name = normalize_source_name(item)
    if not source_name and not url:
        return fallback

    label = f"来源：{escape(source_name or '新闻检索')}"
    if url:
        return f'{label} · <a href="{escape(url)}" target="_blank" rel="noopener noreferrer">查看原文</a>'
    return label


def get_evidence_pool(result=None):
    result = result if isinstance(result, dict) else get_event_analysis_result()
    return safe_get_list((result or {}).get("evidence_pool"))


def get_evidence_items(item, result=None):
    if not isinstance(item, dict):
        return []
    evidence_ids = item.get("evidence_ids", [])
    if not isinstance(evidence_ids, list):
        return []
    evidence_map = {
        evidence.get("id"): evidence
        for evidence in get_evidence_pool(result)
        if isinstance(evidence, dict)
    }
    return [
        evidence_map[evidence_id]
        for evidence_id in evidence_ids
        if evidence_id in evidence_map
    ]


def render_evidence_references(item, result=None):
    evidence_items = get_evidence_items(item, result)
    if not evidence_items:
        st.caption("当前判断主要来自新闻语境与模型归纳，暂无直接引用来源。")
        return

    for evidence in evidence_items:
        title = display_text(evidence.get("title"), "新闻标题待补充")
        source = display_text(evidence.get("source"), "公开新闻")
        date = display_text(evidence.get("date"), "日期待确认")
        summary = display_text(evidence.get("summary"), "暂无摘要")
        source_line = format_source_line(evidence, f"来源：{source}")
        st.markdown(f"**{source}** · {date}")
        st.write(title)
        st.caption(summary)
        st.markdown(source_line, unsafe_allow_html=True)


def render_event_evidence_pool():
    result = get_event_analysis_result()
    evidence_pool = get_evidence_pool(result)
    if not evidence_pool:
        return

    with st.expander("本次使用的新闻来源", expanded=False):
        for evidence in evidence_pool:
            if not isinstance(evidence, dict):
                continue
            title = display_text(evidence.get("title"), "新闻标题待补充")
            source = display_text(evidence.get("source"), "公开新闻")
            date = display_text(evidence.get("date"), "日期待确认")
            source_line = format_source_line(evidence, f"来源：{source}")
            st.markdown(f"**{source}** · {date}")
            st.write(title)
            st.markdown(source_line, unsafe_allow_html=True)


def has_low_evidence(result):
    if not isinstance(result, dict):
        return False
    if result.get("_news_count") == 0:
        return True

    core_fields = [
        "event_summary",
        "market_position",
        "key_data",
        "logic_chain",
        "bull_case",
        "bear_case",
        "risk_radar",
        "insight",
        "next_watch",
    ]
    insufficient_count = 0
    for field in core_fields:
        value = result.get(field)
        if isinstance(value, str) and value.strip().lower() == "evidence_insufficient":
            insufficient_count += 1
        elif isinstance(value, list):
            field_text = " ".join(str(item) for item in value).lower()
            if "evidence_insufficient" in field_text:
                insufficient_count += 1
    return insufficient_count >= 3


def render_simple_text_card(text, card_class="ifin-status-card"):
    st.markdown(
        f"""
        <div class="{card_class}">
            <div class="ifin-card-body">{display_text(text)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def safe_item_text(item, preferred_key="point", fallback=EMPTY_STRUCTURED_TEXT):
    if isinstance(item, str):
        return display_text(item, fallback)
    if isinstance(item, dict):
        return display_text(
            item.get(preferred_key)
            or item.get("name")
            or item.get("title")
            or item.get("content")
            or item.get("explanation"),
            fallback,
        )
    return fallback


def render_view_points_safe(title, points, badge_class):
    result = get_event_analysis_result()
    st.markdown(f"#### {title}")
    for item in safe_get_list(points):
        if isinstance(item, str):
            point = display_text(item)
            detail = "当前依据主要来自公开新闻语境，仍需要更多信息验证。"
        elif isinstance(item, dict):
            point = display_text(item.get("point") or item.get("content") or item.get("title"))
            detail = display_text(
                item.get("detail")
                or item.get("evidence_summary")
                or item.get("basis")
                or item.get("summary")
                or item.get("explanation"),
                "当前依据主要来自公开新闻语境，仍需要更多信息验证。",
            )
        else:
            point = SOFT_UNCERTAINTY_TEXT
            detail = "当前依据主要来自公开新闻语境，仍需要更多信息验证。"

        source_line = format_source_line(item, "来源：公开新闻语境")

        st.markdown(
            f"""
            <div class="ifin-view-card">
                <span class="ifin-mini-badge {badge_class}">{title}</span>
                <div class="ifin-card-body">{point}</div>
                <div class="ifin-view-source">{source_line}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        with st.expander("查看依据", expanded=False):
            st.write(detail)
            render_evidence_references(item, result)
            if not get_evidence_items(item, result):
                st.markdown(source_line, unsafe_allow_html=True)


def render_event_summary():
    render_event_section_title("事件摘要")
    result = get_event_analysis_result()
    summary = display_text((result or {}).get("event_summary"), ANALYSIS_EMPTY_TEXT)
    st.markdown(
        f"""
        <div class="ifin-insight-card">
            <div class="ifin-insight-label">iFin 对事件的简洁解释</div>
            <div class="ifin-card-body">{summary}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if has_low_evidence(result):
        st.info("当前检索到的公开信息有限，本次分析更适合作为问题梳理，而不是结论判断。")


def render_market_context():
    render_event_section_title("市场位置")
    result = get_event_analysis_result()
    market_position_items = (result or {}).get("market_position_items")
    if market_position_items:
        items = safe_get_list(market_position_items)
    else:
        raw_items = safe_get_list((result or {}).get("market_position"))
        items = filter_visible_market_items(raw_items)
        if not items and has_hidden_mock_market_items(raw_items):
            st.info("实时行情暂未接入，本次分析主要基于新闻语境与模型归纳。")
            return
    items = items or [ANALYSIS_EMPTY_TEXT]
    cols = st.columns(min(len(items), 4) or 1)
    for column, item in zip(cols, items):
        with column:
            if isinstance(item, str):
                render_simple_text_card(item)
                continue
            if not isinstance(item, dict):
                render_simple_text_card(EMPTY_STRUCTURED_TEXT)
                continue

            name = display_text(item.get("name") or item.get("indicator"), "市场指标")
            state = display_text(item.get("state") or item.get("position"), "新闻语境判断")
            position = item.get("position_value") or item.get("position_score") or item.get("position_percent") or item.get("position")
            if not isinstance(position, (int, float)):
                position = 50
            direction = display_text(item.get("direction"), "不确定")
            percentile = display_text(item.get("percentile"), "暂不计算历史分位")
            if percentile.strip().lower() in INTERNAL_PLACEHOLDERS:
                percentile = "暂不计算历史分位"
            peer_position = display_text(item.get("peer_position"), MARKET_DATA_PENDING_TEXT)
            data_note = display_text(item.get("data_note"), MARKET_DATA_NOTE_TEXT)
            note = display_text(item.get("note") or item.get("explanation"), MORE_EVIDENCE_TEXT)
            current = display_text(item.get("current"), "当前水平：待数据接入")
            change_1d = display_text(item.get("change_1d"), "待数据接入")
            change_1m = display_text(item.get("change_1m"), "待数据接入")
            change_3m = display_text(item.get("change_3m"), "待数据接入")
            change_1y = display_text(item.get("change_1y"), "待数据接入")
            percentile_1y = display_text(item.get("percentile_1y"), "暂不计算历史分位")
            as_of = display_text(item.get("as_of"), "待数据接入")
            source = display_text(item.get("source"), "待数据接入")
            mock_note = format_market_data_note(item)
            extra_lines = [
                f"变化方向：{direction}",
                f"历史分位：{percentile}",
                f"同类/行业位置：{peer_position}",
                mock_note,
            ]
            render_market_data_card(
                {
                    "title": name,
                    "current_value": state,
                    "body": f"当前水平：{current}。{note}",
                    "progress_value": position,
                    "change_line_1": f"1日：{change_1d} · 1月：{change_1m}",
                    "change_line_2": f"3月：{change_3m} · 1年：{change_1y}",
                    "percentile_line": f"1年历史分位：{percentile_1y}",
                    "extra_meta": extra_lines,
                    "as_of_line": f"时间基准：{as_of}",
                    "source_line": f"数据来源：{source}",
                    "data_note": data_note,
                }
            )


def key_data_unavailable(items):
    if not items:
        return True
    for item in safe_get_list(items):
        if not isinstance(item, dict):
            return False
        confidence = str(item.get("confidence", "")).lower()
        value = str(item.get("value", ""))
        source = str(item.get("source", ""))
        if confidence not in {"unavailable", "estimated"}:
            return False
        if "尚未接入" not in value and "待接入" not in source:
            return False
    return True


def render_key_data_empty_state(items=None):
    labels = []
    for item in safe_get_list(items):
        if isinstance(item, dict):
            label = display_text(item.get("label") or item.get("name"), "")
            if label:
                labels.append(label)
    if not labels:
        labels = ["政策变量", "需求变量", "供给变量", "宏观变量"]
    label_text = "、".join(labels[:6])
    st.markdown(
        f"""
        <div class="ifin-key-empty-card">
            <div class="ifin-market-card-title">关键事件变量</div>
            <div class="ifin-market-card-body">
                该主题的关键事件变量包括：{escape(label_text, quote=True)}。
                当前版本尚未接入稳定数据源，因此暂不展示伪量化数据。
            </div>
            <div class="ifin-market-card-meta">数据状态：待接入主题变量数据源</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_key_numbers():
    render_event_section_title("关键数据")
    result = get_event_analysis_result()
    items = safe_get_list((result or {}).get("key_data_items"))
    if not items:
        render_key_data_empty_state()
        return
    if key_data_unavailable(items):
        render_key_data_empty_state(items)
        return
    cols = st.columns(min(len(items), 4) or 1)
    for column, item in zip(cols, items):
        with column:
            if isinstance(item, str):
                render_simple_text_card(item, "ifin-number-card")
                continue
            if not isinstance(item, dict):
                render_simple_text_card(EMPTY_STRUCTURED_TEXT, "ifin-number-card")
                continue

            name = display_text(item.get("label") or item.get("name") or item.get("metric"), "关键数据")
            unit = display_text(item.get("unit"), "")
            raw_value = display_text(item.get("value"), DATA_SUPPORT_TEXT)
            value = f"{raw_value} {unit}".strip()
            trend = display_text(item.get("confidence") or item.get("trend"), "暂无趋势")
            if trend == "evidence_insufficient":
                trend = "暂无足够数据支持。"
            note = display_text(item.get("insight") or item.get("note") or item.get("explanation"), MORE_EVIDENCE_TEXT)
            period = display_text(item.get("period"), "待数据接入")
            source = display_text(item.get("source"), "待接入主题变量数据源")
            render_market_data_card(
                {
                    "title": name,
                    "current_value": value,
                    "trend": trend,
                    "body": note,
                    "extra_meta": [f"统计区间：{period}"],
                    "source_line": f"数据来源：{source}",
                    "data_note": "事件变量数据不同于行情代理资产，不使用 NVDA / QQQ 等市场价格替代。",
                }
            )


def render_impact_chain():
    render_event_section_title("影响推导")
    st.markdown('<div class="ifin-section-subtitle">事件/主题 → 变量 → 市场 → 资产</div>', unsafe_allow_html=True)
    result = get_event_analysis_result()
    items = safe_get_list((result or {}).get("logic_chain"))
    if not items:
        render_simple_text_card(ANALYSIS_EMPTY_TEXT)
        return

    for index, item in enumerate(items, start=1):
        if isinstance(item, str):
            item = {
                "step": f"Step {index}",
                "title": f"Step {index}",
                "content": item,
                "description": "",
                "evidence_ids": [],
            }
        elif not isinstance(item, dict):
            item = {
                "step": f"Step {index}",
                "title": "推导步骤",
                "content": EMPTY_STRUCTURED_TEXT,
                "description": "",
                "evidence_ids": [],
            }

        step = display_text(item.get("step") or f"Step {index}", f"Step {index}")
        title = display_text(item.get("title") or item.get("content"), "推导步骤")
        content = display_text(item.get("content") or title, title)
        description = display_text(item.get("description") or item.get("explanation"), MORE_EVIDENCE_TEXT)
        with st.expander(f"{step} · {title}", expanded=index == 1):
            st.markdown(f"**{content}**")
            st.write(description)
            if get_evidence_items(item, result):
                render_evidence_references(item, result)
            else:
                st.caption("暂无直接引用来源")


def render_historical_reference():
    render_event_section_title("历史相似事件")
    result = get_event_analysis_result()
    items = safe_get_list((result or {}).get("historical_cases")) or EVENT_DEMO["historical_reference"]
    cols = st.columns(min(len(items), 2) or 1)
    for column, item in zip(cols, items):
        with column:
            if isinstance(item, str):
                render_simple_text_card(item, "ifin-history-card")
                continue
            if not isinstance(item, dict):
                render_simple_text_card(EMPTY_STRUCTURED_TEXT, "ifin-history-card")
                continue

            time = display_text(item.get("year") or item.get("time"), "时间待确认")
            title = display_text(item.get("title") or item.get("event"), "历史参考")
            reaction = display_text(item.get("market_reaction") or item.get("reaction"), MORE_EVIDENCE_TEXT)
            risk = display_text(item.get("risk"), MORE_EVIDENCE_TEXT)
            similarity = display_text(item.get("similarity") or item.get("similar_points"), "类似点需要结合更多历史数据验证。")
            limitation = display_text(item.get("limitation") or item.get("limits"), "历史案例仅供理解传导路径，不代表未来会重复。")
            source_line = format_source_line(item, "历史参考：需后续数据源补强")
            st.markdown(
                f"""
                <div class="ifin-history-card">
                    <div class="ifin-card-title">{title}</div>
                    <div class="ifin-card-body">市场反应：{reaction}</div>
                    <div class="ifin-card-body">主要风险：{risk}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.caption(time)
            with st.expander("查看历史参考", expanded=False):
                st.write(f"年份：{time}")
                st.write(f"事件名称：{title}")
                st.write(f"市场反应：{reaction}")
                st.write(f"主要风险：{risk}")
                st.write(f"类似点：{similarity}")
                st.write(f"局限性：{limitation}")
                render_evidence_references(item, result)
                if not get_evidence_items(item, result):
                    st.markdown(source_line, unsafe_allow_html=True)


def render_risk_radar():
    render_event_section_title("风险雷达")
    result = get_event_analysis_result()
    items = safe_get_list((result or {}).get("risk_radar")) or [ANALYSIS_EMPTY_TEXT]
    cols = st.columns(min(len(items), 3) or 1)
    for column, item in zip(cols, items):
        with column:
            if isinstance(item, str):
                render_simple_text_card(item, "ifin-risk-card")
                continue
            if not isinstance(item, dict):
                render_simple_text_card(EMPTY_STRUCTURED_TEXT, "ifin-risk-card")
                continue

            name = display_text(item.get("name") or item.get("risk"), "风险信号")
            level = display_text(item.get("level"), "中")
            reason = display_text(item.get("reason") or item.get("explanation"), MORE_EVIDENCE_TEXT)
            history = display_text(item.get("historical_reference"), "")
            linked_data = display_text(item.get("linked_data") or item.get("data"), "暂无足够数据支持。")
            source_line = format_source_line(item, "来源：新闻语境 + 模型归纳")
            level_class = "ifin-risk-high" if level == "高" else "ifin-risk-mid"
            st.markdown(
                f"""
                <div class="ifin-risk-card">
                    <span class="ifin-risk-level {level_class}">{level}风险</span>
                    <div class="ifin-card-title">{name}</div>
                    <div class="ifin-card-body">{reason}</div>
                    <div class="ifin-risk-history">{source_line}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            with st.expander("查看风险依据", expanded=False):
                st.write(f"风险原因：{reason}")
                st.write(f"关联数据：{linked_data}")
                st.write(f"历史参考：{history or '需要更多历史数据验证。'}")
                render_evidence_references(item, result)
                if not get_evidence_items(item, result):
                    st.markdown(source_line, unsafe_allow_html=True)


def render_bull_vs_bear():
    render_event_section_title("支持逻辑 / 担忧逻辑")
    result = get_event_analysis_result()
    bull_points = safe_get_list((result or {}).get("bull_case")) or [ANALYSIS_EMPTY_TEXT]
    bear_points = safe_get_list((result or {}).get("bear_case")) or [ANALYSIS_EMPTY_TEXT]
    bull_col, bear_col = st.columns(2)
    with bull_col:
        render_view_points_safe("支持逻辑", bull_points, "ifin-green-badge")
    with bear_col:
        render_view_points_safe("担忧逻辑", bear_points, "ifin-blue-badge")


def render_ifin_insight():
    render_event_section_title("iFin Insight / 认知锚点")
    result = get_event_analysis_result()
    insight = display_text((result or {}).get("insight"), ANALYSIS_EMPTY_TEXT)
    st.markdown(
        f"""
        <div class="ifin-insight-card">
            <div class="ifin-insight-label">本次事件最值得记住的一件事</div>
            <div class="ifin-insight-text">{insight}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_watch_next():
    render_event_section_title("继续探索")
    result = get_event_analysis_result()
    items = safe_get_list((result or {}).get("next_watch"))
    if not items:
        render_simple_text_card("暂无更多探索方向")
        return

    cols = st.columns(min(len(items), 5) or 1)
    for index, (column, item) in enumerate(zip(cols, items), start=1):
        with column:
            if isinstance(item, str):
                title = display_text(item, "探索方向")
                explanation = "这个方向可以帮助继续观察事件背后的驱动因素。"
                item_query = title
                source_line = ""
            elif isinstance(item, dict):
                title = display_text(item.get("item") or item.get("title") or item.get("name"), "探索方向")
                explanation = display_text(
                    item.get("description")
                    or item.get("why")
                    or item.get("reason")
                    or item.get("explanation"),
                    "这个方向可以帮助继续观察事件背后的驱动因素。",
                )
                item_query = display_text(
                    item.get("query")
                    or item.get("item")
                    or item.get("title")
                    or title,
                    title,
                )
                source_line = format_source_line(item, "")
                if st.button(title, key=f"event_next_watch_title_{index}", width="stretch"):
                    st.session_state["pending_event_input"] = item_query
                    st.session_state["event_explore_notice"] = f"已填入：{title}，可以点击“开始分析”继续。"
                    st.rerun()
                st.markdown(
                    f"""
                    <div class="ifin-status-card">
                        <div class="ifin-card-body">{explanation}</div>
                        {f'<div class="ifin-view-source">{source_line}</div>' if source_line else ''}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                with st.expander("查看依据", expanded=False):
                    st.write(explanation)
                    render_evidence_references(item, result)
                    if not get_evidence_items(item, result) and source_line:
                        st.markdown(source_line, unsafe_allow_html=True)
                continue
            else:
                title = "探索方向"
                explanation = EMPTY_STRUCTURED_TEXT
                item_query = title
                source_line = ""

            if st.button(title, key=f"event_next_watch_title_{index}", width="stretch"):
                st.session_state["pending_event_input"] = item_query
                st.session_state["event_explore_notice"] = f"已填入：{title}，可以点击“开始分析”继续。"
                st.rerun()
            st.markdown(
                f"""
                <div class="ifin-status-card">
                    <div class="ifin-card-body">{explanation}</div>
                    {f'<div class="ifin-view-source">{source_line}</div>' if source_line else ''}
                </div>
                """,
                unsafe_allow_html=True,
            )
            with st.expander("查看依据", expanded=False):
                st.write(explanation)
                render_evidence_references(item, result)
                if not get_evidence_items(item, result) and source_line:
                    st.markdown(source_line, unsafe_allow_html=True)


def render_event_notes():
    render_event_section_title("我的笔记")
    st.caption("记录你的理解、疑问、情绪、灵感或后续观察。这里没有标准答案。")
    result = get_event_analysis_result()
    st.session_state.setdefault("note_content", "")
    st.session_state.setdefault("saved_insight", {})
    note_content = st.text_area(
        "我的笔记",
        value=st.session_state.note_content,
        placeholder="例如：我现在还不确定这次利率信号会持续多久，但感觉市场已经提前反映了一部分乐观预期。",
        label_visibility="collapsed",
        height=220,
    )
    if st.button("保存到认知档案", width="stretch"):
        st.session_state.note_content = note_content
        support_items = safe_get_list((result or {}).get("bull_case")) or [ANALYSIS_EMPTY_TEXT]
        concern_items = safe_get_list((result or {}).get("bear_case")) or [ANALYSIS_EMPTY_TEXT]
        risk_items = safe_get_list((result or {}).get("risk_radar")) or [ANALYSIS_EMPTY_TEXT]
        saved_insight = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "event": st.session_state.current_event_title,
            "event_summary": (result or {}).get("event_summary") or ANALYSIS_EMPTY_TEXT,
            "support_logic": [safe_item_text(item, "point", "暂无内容") for item in support_items],
            "concern_logic": [safe_item_text(item, "point", "暂无内容") for item in concern_items],
            "risk_radar": [safe_item_text(item, "name", "风险信号") for item in risk_items],
            "ifin_insight": (result or {}).get("insight") or ANALYSIS_EMPTY_TEXT,
            "note": note_content,
            "focus_tags": [],
            "source_page": "Event Analysis",
            "created_at": datetime.now().strftime("%Y.%m.%d"),
            "updated_at": "",
        }
        st.session_state.saved_insight = saved_insight
        st.session_state.saved_insights.append(saved_insight)
        st.success("已保存到认知档案")

    if st.session_state.saved_insight:
        st.markdown(
            f"""
            <div class="ifin-note">
                <div class="ifin-card-title">已保存到认知档案</div>
                <div class="ifin-card-body">{st.session_state.saved_insight["note"]}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.caption(
            f"{st.session_state.saved_insight['date']} · "
            f"{st.session_state.saved_insight['source_page']}"
        )


def render_event_beta_disclaimer():
    st.markdown(
        """
        <div class="ifin-note">
            <div class="ifin-card-title">iFin Beta</div>
            <div class="ifin-card-body">
                本页面基于公开信息、新闻检索与模型生成分析，仅用于学习、研究和产品体验，不构成任何投资建议。
                市场信息可能存在延迟、缺失或解释偏差，请结合官方公告与专业判断使用。
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


RESEARCH_DECK_ITEMS = [
    {"id": "views", "title": "观点矛盾"},
    {"id": "history", "title": "历史镜像"},
    {"id": "variables", "title": "关键变量"},
    {"id": "risk", "title": "风险来源"},
    {"id": "transmission", "title": "影响路径"},
    {"id": "watch", "title": "后续观察"},
]


def _first_dict(items):
    return next((item for item in safe_get_list(items) if isinstance(item, dict)), {})


def _research_source_preview(item, result):
    sources = []
    for evidence in get_evidence_items(item, result):
        source = display_text(evidence.get("source"), "")
        if source and source not in sources:
            sources.append(source)
    direct_source = normalize_source_name(item)
    if direct_source and direct_source not in sources:
        sources.append(direct_source)
    return sources[:2] or ["公开新闻语境"]


def build_research_card(selected_id, result):
    result = result or {}
    if selected_id == "views":
        support = _first_dict(result.get("bull_case"))
        concern = _first_dict(result.get("bear_case"))
        support_text = safe_item_text(support, "point", "支持逻辑仍需更多证据验证。")
        concern_text = safe_item_text(concern, "point", "谨慎逻辑仍需更多证据验证。")
        sources = _research_source_preview(support, result)
        sources.extend(
            source
            for source in _research_source_preview(concern, result)
            if source not in sources
        )
        return {
            "title": "观点矛盾",
            "core": "市场同时存在不同解释，关键在于哪些变量会被后续证据验证。",
            "support": support_text,
            "caution": concern_text,
            "sources": sources[:2],
        }
    if selected_id == "history":
        item = _first_dict(result.get("historical_cases"))
        return {
            "title": "历史镜像",
            "core": display_text(
                item.get("similarity") or item.get("market_reaction"),
                "历史案例可以提供参照，但不代表当前市场会重复同一路径。",
            ),
            "support": display_text(item.get("title"), "历史参考仍待补充"),
            "caution": display_text(item.get("limitation") or item.get("risk"), "历史环境存在差异。"),
            "sources": _research_source_preview(item, result),
        }
    if selected_id == "variables":
        items = safe_get_list(result.get("key_data_items"))
        labels = [
            display_text(item.get("label") or item.get("name"), "")
            for item in items
            if isinstance(item, dict)
        ]
        labels = [label for label in labels if label]
        return {
            "title": "关键变量",
            "core": "当前主题需要通过核心事件变量验证，而不是用行情代理替代基本面证据。",
            "support": "重点观察：" + ("、".join(labels[:3]) or "政策、需求与供给变量"),
            "caution": "部分变量尚未接入稳定数据源。",
            "sources": ["主题变量数据源待接入"],
        }
    if selected_id == "risk":
        item = _first_dict(result.get("risk_radar"))
        return {
            "title": "风险来源",
            "core": safe_item_text(item, "risk", "当前风险需要结合新闻和数据继续验证。"),
            "support": display_text(item.get("reason"), "风险触发条件仍需观察。"),
            "caution": display_text(item.get("historical_reference"), "历史参考仍需补强。"),
            "sources": _research_source_preview(item, result),
        }
    if selected_id == "transmission":
        steps = [item for item in safe_get_list(result.get("logic_chain")) if isinstance(item, dict)]
        first = steps[0] if steps else {}
        last = steps[-1] if steps else {}
        return {
            "title": "影响路径",
            "core": "从事件触发到资产影响，重点是中间变量如何改变市场预期。",
            "support": display_text(first.get("content") or first.get("description"), "事件起点待确认。"),
            "caution": display_text(last.get("content") or last.get("description"), "最终影响仍存在不确定性。"),
            "sources": _research_source_preview(first, result),
        }
    item = _first_dict(result.get("next_watch"))
    return {
        "title": "后续观察",
        "core": safe_item_text(item, "item", "后续需要持续观察新的公开信息。"),
        "support": display_text(item.get("description") or item.get("why"), "用于验证当前市场解释是否持续。"),
        "caution": "观察方向不代表确定结论。",
        "sources": _research_source_preview(item, result),
    }


def select_mobile_research_evidence():
    selected_id = st.session_state.get("event_mobile_evidence")
    if selected_id:
        st.session_state.event_selected_evidence = selected_id
        st.session_state.event_full_analysis_open = False
        st.session_state.event_research_card_animate = True


def render_research_deck():
    st.markdown('<div class="ifin-prototype-label">RESEARCH DECK</div>', unsafe_allow_html=True)
    selected_id = st.session_state.get("event_selected_evidence", "")
    with st.container(key="event_deck_desktop"):
        for deck_item in RESEARCH_DECK_ITEMS:
            with st.container(key=f"event_deck_material_{deck_item['id']}"):
                if selected_id == deck_item["id"]:
                    st.markdown(
                        '<span class="ifin-deck-selected-marker"></span>',
                        unsafe_allow_html=True,
                    )
                if st.button(
                    deck_item["title"],
                    key=f"event_deck_{deck_item['id']}",
                    width="stretch",
                ):
                    st.session_state.event_selected_evidence = deck_item["id"]
                    st.session_state.event_full_analysis_open = False
                    st.session_state.event_research_card_animate = True
                    st.rerun()

    st.radio(
        "Research Deck",
        [item["id"] for item in RESEARCH_DECK_ITEMS],
        format_func=lambda value: next(
            item["title"] for item in RESEARCH_DECK_ITEMS if item["id"] == value
        ),
        index=None,
        horizontal=True,
        key="event_mobile_evidence",
        on_change=select_mobile_research_evidence,
        label_visibility="collapsed",
    )


def render_research_card(selected_id, result):
    card = build_research_card(selected_id, result)
    sources = " · ".join(card["sources"])
    enter_class = (
        " ifin-research-card-enter"
        if st.session_state.get("event_research_card_animate")
        else ""
    )
    st.markdown(
        f"""
        <div class="ifin-research-card{enter_class}">
            <div class="ifin-prototype-label">RESEARCH CARD</div>
            <div class="ifin-research-title">{escape(card['title'], quote=True)}</div>
            <div class="ifin-research-core">{escape(card['core'], quote=True)}</div>
            <div class="ifin-research-contrast">
                <div><strong>支持观察</strong><br>{escape(card['support'], quote=True)}</div>
                <div><strong>谨慎观察</strong><br>{escape(card['caution'], quote=True)}</div>
            </div>
            <div class="ifin-research-source">来源预览：{escape(sources, quote=True)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.session_state.event_research_card_animate = False
    button_label = "收起完整分析" if st.session_state.get("event_full_analysis_open") else "查看完整分析"
    if st.button(button_label, key="event_toggle_full_analysis", width="stretch"):
        st.session_state.event_full_analysis_open = not st.session_state.get(
            "event_full_analysis_open",
            False,
        )
        st.rerun()


def render_market_snapshot(result, compact=False):
    market_items = safe_get_list(
        (result or {}).get("market_position_items")
        or (result or {}).get("market_position")
    )
    first_market = _first_dict(market_items)
    key_items = safe_get_list((result or {}).get("key_data_items"))
    etf_item = next(
        (
            item
            for item in key_items
            if isinstance(item, dict) and "etf" in str(item.get("label", "")).lower()
        ),
        {},
    )
    position = display_text(
        first_market.get("percentile_1y") or first_market.get("position"),
        "待数据接入",
    )
    price = display_text(first_market.get("current"), "待数据接入")
    etf_flow = display_text(etf_item.get("value"), "待数据接入")
    real_yield = next(
        (
            display_text(item.get("value"), "待数据接入")
            for item in key_items
            if isinstance(item, dict) and "yield" in str(item.get("label", "")).lower()
        ),
        "待数据接入",
    )
    freshness = display_text(
        (result or {}).get("_market_data_as_of"),
        "Latest available",
    )
    compact_class = " ifin-snapshot-compact" if compact else ""
    st.markdown(
        f"""
        <div class="ifin-market-snapshot{compact_class}">
            <div class="ifin-prototype-label">MARKET SNAPSHOT</div>
            <div class="ifin-snapshot-grid">
                <div><span>Market Position</span><strong>{escape(position, quote=True)}</strong></div>
                <div><span>Price</span><strong>{escape(price, quote=True)}</strong></div>
                <div><span>ETF Flow</span><strong>{escape(etf_flow, quote=True)}</strong></div>
                <div><span>Real Yield</span><strong>{escape(real_yield, quote=True)}</strong></div>
            </div>
            <div class="ifin-research-source">Freshness：{escape(freshness, quote=True)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_selected_full_analysis(selected_id):
    st.markdown('<div class="ifin-full-analysis-anchor"></div>', unsafe_allow_html=True)
    if selected_id == "views":
        render_bull_vs_bear()
    elif selected_id == "history":
        render_historical_reference()
    elif selected_id == "variables":
        render_key_numbers()
    elif selected_id == "risk":
        render_risk_radar()
    elif selected_id == "transmission":
        render_impact_chain()
    else:
        render_watch_next()
    render_event_evidence_pool()
    render_ifin_insight()


def render_event_analysis():
    if "pending_event_input" in st.session_state:
        st.session_state["event_input"] = st.session_state.pop("pending_event_input")
    st.session_state.setdefault("event_selected_evidence", "")
    st.session_state.setdefault("event_full_analysis_open", False)
    st.session_state.setdefault("event_research_card_animate", False)

    st.markdown('<div class="ifin-prototype-search-label">SEARCH</div>', unsafe_allow_html=True)
    event_text = st.text_input(
        "Search",
        placeholder="搜索事件、主题、公司或市场问题",
        key="event_input",
        label_visibility="collapsed",
    )
    if st.session_state.get("event_explore_notice"):
        st.info(st.session_state.pop("event_explore_notice"))
    search_control, analysis_control = st.columns([3, 1])
    with search_control:
        use_real_llm = st.checkbox("使用真实 LLM 分析", value=False)
    with analysis_control:
        start_analysis = st.button("开始分析", width="stretch")

    current_result = get_event_analysis_result()
    typed_input = event_text.strip()
    input_interpretation = interpret_event_query(typed_input) if typed_input else {}
    routed_topics = safe_get_list((current_result or {}).get("_suggested_queries"))
    topic_label = (current_result or {}).get("_topic_label")
    assumption = input_interpretation.get("assumption") or (current_result or {}).get("_assumption")
    candidate_topics = safe_get_list(
        routed_topics
        or input_interpretation.get("candidate_topics")
        or (current_result or {}).get("_candidate_topics")
    )
    if topic_label:
        st.caption(f"当前主题：{topic_label}")
    elif assumption:
        st.caption(f"当前理解：{assumption}")
    if candidate_topics:
        st.caption("你也可以继续探索：")
        topic_columns = st.columns(min(len(candidate_topics), 4) or 1)
        for index, topic in enumerate(candidate_topics):
            if isinstance(topic, dict):
                label = display_text(topic.get("label"), "")
                query = display_text(topic.get("query") or topic.get("label"), label or "探索方向")
            else:
                label = display_text(topic, "")
                query = label
            if not label:
                continue
            with topic_columns[index % len(topic_columns)]:
                if st.button(label, key=f"event_candidate_topic_{index}", width="stretch"):
                    st.session_state["pending_event_input"] = query
                    st.session_state["event_explore_notice"] = f"已填入：{label}，可以点击“开始分析”继续。"
                    st.rerun()
    if start_analysis:
        analysis_input = event_text.strip() or EVENT_DEMO["examples"][0]
        st.session_state.current_event_title = analysis_input
        st.session_state.event_analysis_result = run_event_analysis(
            analysis_input,
            use_real_llm=use_real_llm,
        )
        st.session_state.event_analysis_mode = "Real LLM" if use_real_llm else "Mock Pipeline"
        st.session_state.event_demo_ready = True
        st.session_state.event_selected_evidence = ""
        st.session_state.event_full_analysis_open = False
        st.rerun()

    if event_text:
        st.session_state.current_event_title = event_text.strip()
    else:
        st.session_state.current_event_title = EVENT_DEMO["examples"][0]

    result = get_event_analysis_result()
    topic_title = display_text(st.session_state.current_event_title, "Gold")
    freshness = display_text((result or {}).get("_market_data_as_of"), "Latest available")
    current_understanding = display_text(
        (result or {}).get("event_summary"),
        "当前理解仍在形成，选择一个研究角度开始调取依据。",
    )
    st.markdown(
        f"""
        <div class="ifin-prototype-topic-header">
            <div>
                <div class="ifin-prototype-topic">{escape(topic_title, quote=True)}</div>
                <div class="ifin-prototype-understanding">
                    <strong>Current Understanding</strong><br>
                    {escape(current_understanding, quote=True)}
                </div>
            </div>
            <div class="ifin-prototype-freshness">Updated {escape(freshness, quote=True)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if has_low_evidence(result):
        st.info("当前公开信息有限，本次结果更适合作为研究角度梳理。")

    selected_id = st.session_state.get("event_selected_evidence", "")
    if selected_id:
        deck_column, card_column, snapshot_column = st.columns([1, 3, 1], gap="medium")
        with deck_column:
            render_research_deck()
        with card_column:
            render_research_card(selected_id, result)
        with snapshot_column:
            render_market_snapshot(result, compact=True)
    else:
        deck_column, snapshot_column = st.columns([1, 4], gap="medium")
        with deck_column:
            render_research_deck()
        with snapshot_column:
            st.markdown(
                """
                <div class="ifin-prototype-empty-focus">
                    Select one research angle from the deck to pull it into focus.
                </div>
                """,
                unsafe_allow_html=True,
            )
            render_market_snapshot(result, compact=False)

    if selected_id and st.session_state.get("event_full_analysis_open"):
        render_selected_full_analysis(selected_id)

    with st.expander("My Note · Optional", expanded=False):
        judgment = st.radio(
            "Current view",
            ["Skip", "Bullish", "Bearish", "Watch"],
            horizontal=True,
            key="event_prototype_judgment",
        )
        if judgment != "Skip":
            st.multiselect(
                "Which evidence influenced your thinking?",
                [item["title"] for item in RESEARCH_DECK_ITEMS],
                key="event_prototype_influences",
                placeholder="Optional",
            )
        render_event_notes()
    render_event_beta_disclaimer()
