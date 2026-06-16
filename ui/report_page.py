from datetime import datetime

import streamlit as st

from services.report_service import run_report_analysis
from ui.components import REPORT_DEMO, get_report_analysis_result, render_event_section_title


def render_report_summary():
    render_event_section_title("本期发生了什么")
    result = get_report_analysis_result()
    summary = (result or {}).get("what_happened") or REPORT_DEMO["summary"]
    st.markdown(
        f"""
        <div class="ifin-insight-card">
            <div class="ifin-insight-label">30 秒理解本期核心变化</div>
            <div class="ifin-card-body">{summary}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_report_changes():
    render_event_section_title("相比上一期变化")
    result = get_report_analysis_result()
    items = (result or {}).get("changes") or REPORT_DEMO["changes"]
    cols = st.columns(min(len(items), 4) or 1)
    for column, item in zip(cols, items):
        metric = item.get("metric") or "关键指标"
        direction = item.get("direction") or "暂无趋势"
        magnitude = item.get("magnitude") or ""
        trend_text = f"{direction} · {magnitude}" if magnitude else direction
        explanation = item.get("explanation") or "暂无解释。"
        with column:
            st.markdown(
                f"""
                <div class="ifin-report-card">
                    <div class="ifin-card-title">{metric}</div>
                    <span class="ifin-change-direction">{trend_text}</span>
                    <div class="ifin-card-body">解释：{explanation}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_report_outlook_tracking():
    render_event_section_title("上期展望兑现情况")
    result = get_report_analysis_result()
    items = (result or {}).get("expectation_check") or REPORT_DEMO["outlook_tracking"]
    for item in items:
        status = item.get("status") or "暂无判断"
        quote = item.get("quote") or item.get("prior_expectation") or "暂无上期展望。"
        source = item.get("source") or "示例数据"
        current_result = item.get("result") or item.get("current_result") or "暂无本期结果。"
        evidence = item.get("evidence") or "暂无依据。"
        st.markdown(
            f"""
            <div class="ifin-report-card">
                <span class="ifin-fulfillment">{status}</span>
                <div class="ifin-card-title">上期展望原文：{quote}</div>
                <div class="ifin-card-meta">来源：{source}</div>
                <div class="ifin-card-body">本期结果：{current_result}</div>
                <div class="ifin-card-body">兑现依据：{evidence}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_report_risks():
    render_event_section_title("风险信号")
    result = get_report_analysis_result()
    items = (result or {}).get("risk_signals") or REPORT_DEMO["risk_signals"]
    cols = st.columns(min(len(items), 2) or 1)
    for column, item in zip(cols, items):
        level = item.get("level") or "中"
        level_class = "ifin-risk-mid" if level == "中" else "ifin-risk-high"
        name = item.get("name") or "风险信号"
        signal = item.get("signal") or "暂无当前信号。"
        case = item.get("case") or "暂无相似案例。"
        explanation = item.get("explanation") or "暂无解释。"
        with column:
            st.markdown(
                f"""
                <div class="ifin-risk-card">
                    <span class="ifin-risk-level {level_class}">{level}风险</span>
                    <div class="ifin-card-title">{name}</div>
                    <div class="ifin-card-body">当前信号：{signal}</div>
                    <div class="ifin-risk-history">相似企业 / 行业案例：{case}</div>
                    <div class="ifin-card-body">风险解释：{explanation}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_report_industry_position():
    render_event_section_title("行业位置分析")
    result = get_report_analysis_result()
    items = (result or {}).get("industry_position") or REPORT_DEMO["industry_position"]
    cols = st.columns(min(len(items), 3) or 1)
    for column, item in zip(cols, items):
        metric = item.get("metric") or item.get("dimension") or "行业位置"
        company = item.get("company") or REPORT_DEMO["company"]
        industry = item.get("industry") or item.get("industry_reference") or "暂无行业参考"
        position = item.get("position") or "暂无位置"
        explanation = item.get("explanation") or "暂无解释。"
        with column:
            st.markdown(
                f"""
                <div class="ifin-status-card">
                    <div class="ifin-card-title">{metric}</div>
                    <div class="ifin-number-value">{company}</div>
                    <div class="ifin-card-meta">行业参考：{industry}</div>
                    <span class="ifin-mini-badge ifin-blue-badge">{position}</span>
                    <div class="ifin-card-body">{explanation}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_report_watch_next():
    render_event_section_title("下一步关注")
    result = get_report_analysis_result()
    items = (result or {}).get("next_watch") or REPORT_DEMO["watch_next"]
    cols = st.columns(min(len(items), 3) or 1)
    for column, item in zip(cols, items):
        priority = item.get("priority") or "中优先级"
        title = item.get("item") or item.get("name") or "关注事项"
        why = item.get("why") or item.get("reason") or "暂无说明。"
        with column:
            st.markdown(
                f"""
                <div class="ifin-status-card">
                    <span class="ifin-mini-badge ifin-blue-badge">{priority}</span>
                    <div class="ifin-card-title">{title}</div>
                    <div class="ifin-card-body">为什么重要：{why}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_report_notes():
    render_event_section_title("我的笔记")
    st.caption("记录你的理解、疑问、观察或灵感。这里没有标准答案。")
    result = get_report_analysis_result()
    st.session_state.setdefault("report_note_content", "")
    note_content = st.text_area(
        "我的笔记",
        value=st.session_state.report_note_content,
        placeholder="例如：广告恢复速度超出预期，但 AI 投入能否转化为收入仍需要观察。我更关注下一季度利润率变化。",
        label_visibility="collapsed",
        height=220,
    )
    if st.button("保存到记录", width="stretch"):
        now = datetime.now()
        st.session_state.report_note_content = note_content
        risk_items = (result or {}).get("risk_signals") or REPORT_DEMO["risk_signals"]
        saved_report_note = {
            "date": now.strftime("%Y-%m-%d"),
            "event": f'{REPORT_DEMO["company"]} {REPORT_DEMO["selected_period"]} 财报',
            "note": note_content,
            "source_page": "Reports",
            "report_period": REPORT_DEMO["selected_period"],
            "company": st.session_state.get("current_report_company", REPORT_DEMO["company"]),
            "event_summary": (result or {}).get("what_happened") or REPORT_DEMO["summary"],
            "risk_radar": [item.get("name", "风险信号") for item in risk_items],
            "ifin_insight": "",
            "focus_tags": ["财报", "互联网", "利润率", "AI投入"],
            "created_at": now.strftime("%Y.%m.%d"),
            "updated_at": now.strftime("%Y.%m.%d"),
        }
        st.session_state.saved_insights.append(saved_report_note)
        st.success("已保存到记录")


def render_financial_analysis():
    st.markdown(
        """
        <div class="ifin-report-input">
            <div class="ifin-kicker">Reports V1</div>
            <h1>财报分析</h1>
            <p class="ifin-hero-subtitle">从连续报告中理解企业变化</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    company_input = st.text_input(
        "公司 / 股票搜索",
        placeholder=REPORT_DEMO["ticker_placeholder"],
    )
    selected_period = st.selectbox(
        f'{REPORT_DEMO["company"]} 可选财报',
        REPORT_DEMO["periods"],
        index=REPORT_DEMO["periods"].index(REPORT_DEMO["selected_period"]),
    )
    report_text = st.text_area(
        "报告文本",
        placeholder="粘贴财报文本、管理层讨论或你想分析的报告片段。",
        height=120,
    )
    if st.button("开始分析", key="report-run-analysis", width="stretch"):
        company = company_input.strip() or REPORT_DEMO["company"]
        st.session_state.current_report_company = company
        st.session_state.report_analysis_result = run_report_analysis(company, report_text)
    st.caption(f"当前展示：{REPORT_DEMO['company']} {selected_period} 示例数据，暂不接入实时数据源。")

    render_report_summary()
    render_report_changes()
    render_report_outlook_tracking()
    render_report_risks()
    render_report_industry_position()
    render_report_watch_next()
    render_report_notes()
