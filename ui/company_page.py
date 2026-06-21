"""Company V2 MVP workspace UI."""

from __future__ import annotations

from datetime import datetime
from html import escape
from typing import Any

import streamlit as st

from services.company_service import run_company_analysis


MARKET_LABELS = {
    "price": "当前价格",
    "open": "今开",
    "high": "最高",
    "low": "最低",
    "volume": "成交量",
    "market_cap": "市值",
    "pe_ratio": "市盈率",
}


def _text(value: Any) -> str:
    return escape(str(value or ""), quote=True)


def _format_number(value: Any, field: str) -> str:
    if value is None:
        return ""
    try:
        number = float(value)
    except (TypeError, ValueError):
        return str(value)
    if field in {"volume", "market_cap"}:
        for divisor, suffix in ((1_000_000_000_000, "T"), (1_000_000_000, "B"), (1_000_000, "M")):
            if abs(number) >= divisor:
                return f"{number / divisor:.2f}{suffix}"
        return f"{number:,.0f}"
    return f"{number:,.2f}"


def _render_company_header(profile: dict[str, Any]) -> None:
    st.markdown(
        f"""
        <div class="ifin-prototype-topic-header">
            <div>
                <div class="ifin-prototype-label">COMPANY RESEARCH WORKSPACE</div>
                <div class="ifin-prototype-topic">{_text(profile.get('display_name'))}</div>
                <div class="ifin-prototype-understanding">
                    {_text(profile.get('ticker'))} · {_text(profile.get('exchange'))}
                </div>
            </div>
            <div class="ifin-prototype-freshness">Company V2 MVP</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_market_layer(snapshot: dict[str, Any]) -> None:
    st.markdown('<div class="ifin-prototype-label">COMPANY MARKET LAYER</div>', unsafe_allow_html=True)
    status = snapshot.get("data_status", "unavailable")
    values = [
        (field, snapshot.get(field))
        for field in MARKET_LABELS
        if snapshot.get(field) is not None
    ]
    if status == "unavailable" or not values:
        st.markdown(
            """
            <div class="ifin-market-snapshot">
                <div class="ifin-research-title">市场快照</div>
                <div class="ifin-research-core">实时行情暂未接入或当前不可用。</div>
                <div class="ifin-research-source">缺失数据不会被估算或使用示例值填充。</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    metric_html = "".join(
        (
            "<div>"
            f"<span>{_text(MARKET_LABELS[field])}</span>"
            f"<strong>{_text(_format_number(value, field))}</strong>"
            "</div>"
        )
        for field, value in values
    )
    updated_at = snapshot.get("updated_at") or "时间基准暂不可用"
    source = snapshot.get("source") or "数据来源暂不可用"
    st.markdown(
        f"""
        <div class="ifin-market-snapshot">
            <div class="ifin-research-title">市场快照</div>
            <div class="ifin-snapshot-grid">{metric_html}</div>
            <div class="ifin-research-source">
                截至：{_text(updated_at)} · 来源：{_text(source)}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_evidence_sections(sections: list[dict[str, Any]]) -> str:
    rendered = []
    for section in sections:
        title = _text(section.get("title") or "证据记录")
        quote = _text(section.get("quote") or "暂无可展示摘录")
        source = _text(section.get("source") or "来源暂不可用")
        page = _text(section.get("page"))
        published = _text(section.get("published_at"))
        url = str(section.get("url") or "").strip()
        meta = " · ".join(item for item in [source, published, f"第 {page} 页" if page else ""] if item)
        link = (
            f'<a href="{escape(url, quote=True)}" target="_blank">查看原文</a>'
            if url
            else ""
        )
        rendered.append(
            f"""
            <div class="ifin-research-contrast">
                <div>
                    <strong>{title}</strong><br>{quote}
                    <div class="ifin-research-source">{meta} {link}</div>
                </div>
            </div>
            """
        )
    return "".join(rendered)


def _render_company_card(card: dict[str, Any]) -> None:
    title = _text(card.get("title") or "研究问题")
    if card.get("empty_state", True):
        st.markdown(
            f"""
            <div class="ifin-research-card">
                <div class="ifin-prototype-label">RESEARCH QUESTION</div>
                <div class="ifin-research-title">{title}</div>
                <div class="ifin-research-core">当前证据不足，暂不生成分析。</div>
                <div class="ifin-research-source">等待可追溯的财报、公告或新闻证据。</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    summary = _text(card.get("card_summary"))
    points = [str(item) for item in card.get("key_points", []) if str(item).strip()]
    point_html = "".join(f"<li>{_text(point)}</li>" for point in points)
    evidence_ids = [str(item) for item in card.get("evidence_ids", []) if str(item).strip()]
    sections = [item for item in card.get("expanded_sections", []) if isinstance(item, dict)]
    st.markdown(
        f"""
        <div class="ifin-research-card">
            <div class="ifin-prototype-label">RESEARCH QUESTION · {_text(card.get('confidence'))}</div>
            <div class="ifin-research-title">{title}</div>
            <div class="ifin-research-core">{summary}</div>
            <ul class="ifin-card-body">{point_html}</ul>
            <details>
                <summary>查看证据详情</summary>
                {_render_evidence_sections(sections)}
            </details>
            <div class="ifin-research-source">
                Evidence IDs：{_text(' · '.join(evidence_ids))}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_research_deck(cards: list[dict[str, Any]]) -> None:
    st.markdown('<div class="ifin-prototype-label">COMPANY RESEARCH DECK</div>', unsafe_allow_html=True)
    columns = st.columns(2, gap="medium")
    for index, card in enumerate(cards):
        with columns[index % 2]:
            _render_company_card(card)


def _render_notes(profile: dict[str, Any], query: str) -> None:
    company_id = str(profile.get("company_id") or "company")
    note_key = f"company_note_{company_id}"
    with st.expander("我的笔记 · 可选", expanded=False):
        note = st.text_area(
            "记录你的理解、疑问或后续观察",
            key=note_key,
            height=180,
            placeholder="这里没有标准答案。记录此刻对公司的理解即可。",
        )
        if st.button("保存到认知档案", key=f"save_{note_key}"):
            now = datetime.now()
            st.session_state.setdefault("saved_insights", [])
            st.session_state.saved_insights.append(
                {
                    "date": now.strftime("%Y-%m-%d"),
                    "event": f"{profile.get('display_name', query)} 公司研究",
                    "note": note,
                    "source_page": "Company Research",
                    "company": profile.get("display_name", ""),
                    "company_id": company_id,
                    "created_at": now.strftime("%Y.%m.%d"),
                    "updated_at": now.strftime("%Y.%m.%d"),
                }
            )
            st.success("已保存到认知档案")


def render_company_page() -> None:
    """Render Company V2 MVP without legacy Report demo fallback."""
    st.markdown('<div class="ifin-prototype-search-label">SEARCH</div>', unsafe_allow_html=True)
    query = st.text_input(
        "Company Search",
        placeholder="输入公司名或股票代码，例如：NVDA / 英伟达 / 腾讯 / 0700.HK / AAPL",
        key="company_search_input",
        label_visibility="collapsed",
    )
    if st.button("研究这家公司", key="company_run_analysis", width="stretch"):
        clean_query = query.strip()
        if clean_query:
            st.session_state.company_analysis_result = run_company_analysis(clean_query)
            st.session_state.current_company_query = clean_query
        else:
            st.session_state.company_analysis_result = None
            st.session_state.current_company_query = ""

    result = st.session_state.get("company_analysis_result")
    if not result:
        st.info("输入公司名称或股票代码，开始建立公司研究视图。")
        return

    metadata = result.get("metadata") or {}
    if not metadata.get("resolved"):
        st.info("当前暂未收录该公司")
        return

    profile = result.get("company_profile") or {}
    _render_company_header(profile)
    st.info("当前为 Company V2 MVP，部分内容使用示例证据进行结构验证。")
    _render_market_layer(result.get("market_snapshot") or {})
    _render_research_deck(result.get("company_card_pool") or [])
    _render_notes(profile, st.session_state.get("current_company_query", query))
