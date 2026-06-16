import streamlit as st

from ui.components import render_event_section_title


def render_guide_flow():
    steps = [
        ("市场事件", "理解影响路径"),
        ("企业财报", "理解经营变化"),
        ("个人记录", "沉淀自己的思考"),
        ("长期积累", "形成判断框架"),
    ]
    st.markdown('<div class="ifin-reasoning-wrap">', unsafe_allow_html=True)
    for index, (title, body) in enumerate(steps, start=1):
        st.markdown(
            f"""
            <div class="ifin-reasoning-card">
                <span class="ifin-step-badge">Step {index}</span>
                <div class="ifin-reasoning-title">{title}</div>
                <div class="ifin-reasoning-content">{body}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)


def render_guide_feature_cards():
    cards = [
        {
            "title": "事件分析",
            "body": "理解新闻、政策与市场反应之间的关系。关注影响路径，而不是结论。",
            "tone": "ifin-work-card-blue",
        },
        {
            "title": "财报分析",
            "body": "理解企业发生了什么变化。关注经营质量、风险信号与行业位置。",
            "tone": "ifin-work-card-green",
        },
        {
            "title": "个人记录",
            "body": "记录自己的疑问、观察与思考。市场没有标准答案。",
            "tone": "ifin-work-card-blue",
        },
    ]
    cols = st.columns(3)
    for column, card in zip(cols, cards):
        with column:
            st.markdown(
                f"""
                <div class="ifin-work-card {card["tone"]}">
                    <div class="ifin-work-title">{card["title"]}</div>
                    <div class="ifin-work-body">{card["body"]}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_guide():
    st.markdown(
        """
        <div class="ifin-hero-v2">
            <div class="ifin-kicker">Guide</div>
            <h1>什么是 iFin</h1>
            <p class="ifin-hero-subtitle">iFin 不预测市场。</p>
            <div class="ifin-hero-note">它帮助你从事件、财报与个人记录中建立自己的判断。</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="ifin-insight-card">
            <div class="ifin-card-body">
                每天都有大量新闻、财报与观点出现。但信息并不等于理解。
                iFin 希望帮助用户整理信息、理解变化、记录思考，最终形成属于自己的认知框架。
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    render_event_section_title("iFin 如何帮助你理解市场")
    render_guide_flow()

    render_event_section_title("iFin 提供什么")
    render_guide_feature_cards()

    render_event_section_title("产品理念")
    st.markdown(
        """
        <div class="ifin-insight-card">
            <div class="ifin-insight-text">
                市场充满噪音。<br><br>
                iFin 希望帮助你：理解变化、记录思考、建立认知，而不是预测市场。
            </div>
            <div class="ifin-view-source">Read the market,<br>not predict it.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
