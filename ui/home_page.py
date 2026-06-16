import streamlit as st

from ui.components import (
    HOME_FOCUS_ITEMS,
    HOME_GROWTH_STATS,
    HOME_INSIGHTS,
    HOME_WATCH_TAGS,
    render_header,
)


def render_home_work_card(title, body, button_label, target_page, tone):
    tone_class = "ifin-work-card-green" if tone == "green" else "ifin-work-card-blue"
    st.markdown(
        f"""
        <div class="ifin-work-card {tone_class}">
            <div class="ifin-work-title">{title}</div>
            <div class="ifin-work-body">{body}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button(button_label, key=f"home-jump-{target_page}", width="stretch"):
        st.session_state.page = target_page
        st.rerun()


def render_focus_row(title, tag):
    st.markdown(
        f"""
        <div class="ifin-list-row">
            <div class="ifin-row-title">{title}</div>
            <span class="ifin-mini-badge ifin-blue-badge">{tag}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_insight_row(item):
    badge_class = "ifin-green-badge" if item["type"] == "财务分析" else "ifin-blue-badge"
    st.markdown(
        f"""
        <div class="ifin-list-row">
            <div>
                <div class="ifin-row-title">{item["title"]}</div>
                <div class="ifin-row-meta">{item["date"]}</div>
            </div>
            <span class="ifin-mini-badge {badge_class}">{item["type"]}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_home_stat(item):
    st.markdown(
        f"""
        <div class="ifin-stat-card">
            <div class="ifin-stat-label">{item["label"]}</div>
            <div class="ifin-stat-value">{item["value"]}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_home():
    render_header(
        "今天，你想从哪里开始阅读市场？",
        "把复杂的金融信息，转化为清晰的认知与洞察。",
    )

    entry_col, report_col = st.columns(2)
    with entry_col:
        render_home_work_card(
            "分析市场事件",
            "理解新闻、政策变化与市场反应，拆解事件背后的影响路径与风险。",
            "开始分析 →",
            "Event Analysis",
            "blue",
        )
    with report_col:
        render_home_work_card(
            "分析财务报告",
            "解读财报数据，识别关键指标、经营质量与潜在风险信号。",
            "开始分析 →",
            "Financial Analysis",
            "green",
        )

    left_col, right_col = st.columns([1.05, 1])
    with left_col:
        st.markdown('<div class="ifin-section-title">今日市场焦点</div>', unsafe_allow_html=True)
        for item in HOME_FOCUS_ITEMS:
            render_focus_row(item["title"], item["tag"])

    with right_col:
        st.markdown('<div class="ifin-section-title">最近的洞察</div>', unsafe_allow_html=True)
        for item in HOME_INSIGHTS:
            render_insight_row(item)

    watch_col, search_col = st.columns([1.5, 1])
    with watch_col:
        st.markdown('<div class="ifin-section-title">我的关注领域</div>', unsafe_allow_html=True)
        tags_html = "".join(f'<span class="ifin-watch-tag">{tag}</span>' for tag in HOME_WATCH_TAGS)
        st.markdown(f'<div class="ifin-watch-tags">{tags_html}</div>', unsafe_allow_html=True)
        st.button("添加关注 +", width="content")

    with search_col:
        st.markdown('<div class="ifin-section-title">快速检索</div>', unsafe_allow_html=True)
        st.text_input(
            "快速检索",
            placeholder="输入股票、行业、新闻、财报或市场关键词",
            label_visibility="collapsed",
        )

    st.markdown('<div class="ifin-section-title">认知成长</div>', unsafe_allow_html=True)
    stat_cols = st.columns(4)
    for column, item in zip(stat_cols, HOME_GROWTH_STATS):
        with column:
            render_home_stat(item)
