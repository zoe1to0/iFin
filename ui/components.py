from datetime import datetime

import streamlit as st

from modules.mock_data import NOTE_ATTITUDES
from modules.ui_sections import render_note


HOME_FOCUS_ITEMS = [
    {"title": "美联储利率决议影响市场风险偏好", "tag": "宏观"},
    {"title": "AI 产业链估值波动加剧", "tag": "科技"},
    {"title": "新能源汽车价格竞争持续", "tag": "行业"},
    {"title": "银行板块关注净息差与资产质量", "tag": "银行"},
]

HOME_INSIGHTS = [
    {"title": "英伟达 Q4 财报分析", "date": "2026-06-08", "type": "财务分析"},
    {"title": "美国利率决议解读", "date": "2026-06-07", "type": "事件分析"},
    {"title": "AI 行业发展趋势与风险", "date": "2026-06-06", "type": "事件分析"},
    {"title": "苹果公司服务业务增长分析", "date": "2026-06-05", "type": "财务分析"},
]

HOME_WATCH_TAGS = ["人工智能", "半导体", "银行", "宏观经济", "新能源汽车", "消费电子"]

HOME_GROWTH_STATS = [
    {"label": "分析事件", "value": "12"},
    {"label": "研读报告", "value": "8"},
    {"label": "主要关注风险", "value": "估值风险"},
    {"label": "认知偏好", "value": "长期价值投资"},
]

PROFILE_DEMO_INSIGHTS = [
    {
        "date": "2026.06.12",
        "event": "美联储利率决议",
        "event_summary": "美联储释放更谨慎的政策信号，市场重新评估未来降息节奏。",
        "support_logic": ["市场可能提前反映降息预期，风险资产获得支撑。"],
        "concern_logic": ["通胀反复可能导致降息节奏慢于市场预期。"],
        "risk_radar": ["估值压力上升", "政策预期落空"],
        "ifin_insight": "市场正在重新校准未来流动性与估值之间的关系。",
        "note": "市场可能已经提前反映降息预期，但后续 CPI 和美债收益率仍然值得观察。",
        "focus_tags": ["流动性", "利率", "估值"],
        "source_page": "Event Analysis",
        "created_at": "2026.06.12",
        "updated_at": "2026.06.15",
    },
    {
        "date": "2026.06.08",
        "event": "AI 产业链估值波动",
        "event_summary": "AI 产业链出现估值波动，市场开始区分长期需求与短期定价压力。",
        "support_logic": ["AI 基础设施需求仍有长期支撑。"],
        "concern_logic": ["高估值资产对利率和盈利预期更敏感。"],
        "risk_radar": ["估值波动", "盈利兑现压力"],
        "ifin_insight": "真正需要观察的是增长预期能否持续转化为盈利质量。",
        "note": "短期波动不一定改变长期主题，但估值位置会影响市场对消息的反应强度。",
        "focus_tags": ["AI", "科技股", "风险偏好"],
        "source_page": "Event Analysis",
        "created_at": "2026.06.08",
        "updated_at": "",
    },
]

PROFILE_TOPIC_TAGS = ["流动性", "利率", "宏观", "科技股", "AI", "风险偏好"]

REPORT_DEMO = {
    "company": "腾讯控股",
    "ticker_placeholder": "输入公司名或股票代码，例如：腾讯 / 英伟达 / AAPL / 00700.HK",
    "periods": ["2025 Q1", "2024 Q4", "2024 Q3", "2024 Q2"],
    "selected_period": "2025 Q1",
    "summary": (
        "腾讯本季度广告业务恢复增长，游戏业务保持稳定，金融科技增速放缓。"
        "市场关注重点正在从收入恢复转向增长质量、利润率稳定性与 AI 投入效率。"
        "AI 投入仍在持续，但短期内能否转化为新增收入仍需要观察。"
    ),
    "changes": [
        {
            "metric": "收入",
            "direction": "增长",
            "magnitude": "12%",
            "explanation": "广告业务恢复与游戏收入稳定推动整体收入增长。",
        },
        {
            "metric": "利润",
            "direction": "回落",
            "magnitude": "3%",
            "explanation": "AI 与云基础设施投入增加，对短期利润率形成压力。",
        },
        {
            "metric": "现金流",
            "direction": "改善",
            "magnitude": "经营现金流稳定",
            "explanation": "经营活动现金流保持稳定，费用控制有所改善。",
        },
        {
            "metric": "管理层指引",
            "direction": "保持谨慎",
            "magnitude": "外部不确定性仍在",
            "explanation": "管理层强调外部宏观环境仍有不确定性。",
        },
    ],
    "outlook_tracking": [
        {
            "quote": "预计广告业务将持续恢复。",
            "source": "2024 Q4 财报 / 管理层业绩说明",
            "result": "广告收入同比增长 18%。",
            "status": "已兑现",
            "evidence": "本期广告收入恢复增长，且财报中明确说明广告需求改善。",
        },
        {
            "quote": "海外业务增长有望改善。",
            "source": "2024 Q4 财报 / 管理层展望",
            "result": "海外业务增速仅小幅回升。",
            "status": "部分兑现",
            "evidence": "本期财报显示海外业务有所改善，但增长幅度低于前期展望中的积极表述。",
        },
    ],
    "risk_signals": [
        {
            "name": "利润率承压",
            "level": "中",
            "signal": "AI 与云基础设施投入增加，短期费用压力上升。",
            "case": "Meta 在大规模 AI 与元宇宙投入阶段曾出现利润率阶段性承压。",
            "explanation": "当资本开支和研发投入先于收入兑现时，企业短期盈利能力可能受到压缩。",
        },
        {
            "name": "金融科技增速放缓",
            "level": "中",
            "signal": "金融科技业务增速低于广告和游戏业务。",
            "case": "部分支付与金融科技平台在监管趋严和消费放缓阶段出现收入增速下滑。",
            "explanation": "如果核心支付和金融服务增长放缓，可能影响整体收入结构稳定性。",
        },
    ],
    "industry_position": [
        {
            "metric": "收入增速",
            "company": "12%",
            "industry": "互联网平台行业平均 8%",
            "position": "行业前 20%",
            "explanation": "收入恢复速度高于行业平均水平。",
        },
        {
            "metric": "利润率",
            "company": "28%",
            "industry": "行业平均 22%",
            "position": "行业前 25%",
            "explanation": "盈利能力仍处于较强区间，但投入增加可能影响后续稳定性。",
        },
        {
            "metric": "现金流质量",
            "company": "经营现金流稳定",
            "industry": "多数同业现金流波动较大",
            "position": "行业前 30%",
            "explanation": "现金流韧性较好，有助于支持持续投入。",
        },
    ],
    "watch_next": [
        {
            "priority": "高优先级",
            "item": "广告收入增长",
            "why": "决定本期恢复趋势是否具备持续性。",
        },
        {
            "priority": "高优先级",
            "item": "AI 投入回报",
            "why": "影响未来利润率和新增收入空间。",
        },
        {
            "priority": "中优先级",
            "item": "游戏业务增长",
            "why": "游戏仍是重要利润来源，增长稳定性影响整体表现。",
        },
    ],
}

EVENT_DEMO = {
    "examples": [
        "美联储利率决议影响市场风险偏好",
        "英伟达发布财报",
        "中国地产刺激政策",
        "AI 芯片出口限制",
    ],
    "summary": (
        "美联储本次利率决议释放出更谨慎的政策信号，市场开始重新评估未来降息节奏。"
        "利率预期的变化会影响美元、美债收益率、资金成本和风险资产估值。"
        "当前市场关注的重点不只是本次利率是否变化，而是未来流动性路径是否会被重新定价。"
    ),
    "market_context": [
        {
            "name": "纳斯达克",
            "state": "高位",
            "position": 82,
            "range_note": "位于过去3年估值区间前20%",
            "note": "科技与成长资产对利率预期更敏感。",
        },
        {
            "name": "标普 500",
            "state": "高位",
            "position": 78,
            "range_note": "位于过去3年估值区间前25%",
            "note": "整体估值处在较受关注的位置。",
        },
        {
            "name": "VIX",
            "state": "低位",
            "position": 24,
            "range_note": "位于过去3年波动区间后30%",
            "note": "市场短期波动预期相对平稳。",
        },
        {
            "name": "10 年期美债收益率",
            "state": "中高位",
            "position": 68,
            "range_note": "位于过去3年利率区间前35%",
            "note": "影响资金成本与风险资产估值。",
        },
    ],
    "key_numbers": [
        {"name": "联邦基金利率", "value": "5.25%-5.50%", "trend": "→ 维持高位", "note": "当前政策利率仍处于较高区间。"},
        {"name": "核心 CPI", "value": "3.1%", "trend": "↓ 连续回落", "note": "通胀回落但仍高于长期目标。"},
        {"name": "失业率", "value": "4.1%", "trend": "↑ 小幅上升", "note": "就业市场开始出现边际降温。"},
        {"name": "10 年期美债收益率", "value": "4.5%", "trend": "↑ 小幅上升", "note": "影响风险资产估值与资金成本。"},
    ],
    "impact_reasoning": [
        {
            "step": "Step 1",
            "title": "事件起点",
            "content": "美联储利率决议",
            "description": "政策信号影响市场对未来利率路径的判断。",
        },
        {
            "step": "Step 2",
            "title": "核心变量",
            "content": "利率预期变化",
            "description": "市场重新评估未来降息节奏和资金成本。",
        },
        {
            "step": "Step 3",
            "title": "市场传导",
            "content": "美元指数 / 美债收益率 / 流动性预期",
            "description": "利率预期变化会传导到汇率、债券收益率和整体流动性环境。",
        },
        {
            "step": "Step 4",
            "title": "资产影响",
            "content": "科技股 / 成长股 / 新兴市场资产",
            "description": "这些资产对利率和流动性变化更敏感。",
        },
        {
            "step": "Step 5",
            "title": "风险结果",
            "content": "估值压力 / 风险偏好变化",
            "description": "当市场处于高位时，利率路径变化可能放大估值波动。",
        },
    ],
    "historical_reference": [
        {
            "time": "2023 年",
            "event": "美联储暂停加息预期升温",
            "reaction": "科技股和成长股短期获得支撑。",
            "risk": "通胀反复导致降息预期推迟。",
        },
        {
            "time": "2019 年",
            "event": "美联储转向宽松预期",
            "reaction": "风险资产估值修复。",
            "risk": "经济增长放缓压力仍未消失。",
        },
    ],
    "risk_radar": [
        {
            "name": "估值压力上升",
            "level": "高",
            "reason": "纳斯达克和标普 500 处于高位，如果利率预期重新上行，成长股估值可能承压。",
            "historical_reference": "2022 年利率快速上行阶段，成长股估值对折现率变化反应更明显。",
        },
        {
            "name": "政策预期落空",
            "level": "中",
            "reason": "市场可能已提前定价降息，如果后续通胀数据高于预期，预期可能被修正。",
            "historical_reference": "2023 年多次通胀反复曾推动市场延后降息预期。",
        },
        {
            "name": "流动性边际收紧",
            "level": "中",
            "reason": "高利率维持更久可能使资金转向债券、现金等防御性资产。",
            "historical_reference": "2018 年流动性收紧阶段，风险偏好曾出现阶段性降温。",
        },
    ],
    "ifin_insight": "这次事件最值得记住的不是一次利率决定，而是市场正在重新校准未来流动性与估值之间的关系。",
    "bull_points": [
        {
            "point": "市场可能提前反映降息预期，风险资产获得支撑。",
            "source": "Bloomberg 市场评论",
            "source_type": "媒体报道",
        },
        {
            "point": "如果企业盈利保持韧性，科技股估值仍有基本面支撑。",
            "source": "高盛策略报告",
            "source_type": "机构观点",
        },
        {
            "point": "AI 等长期主题仍可能支撑科技板块表现。",
            "source": "科技行业研究报告",
            "source_type": "行业研究",
        },
    ],
    "bear_points": [
        {
            "point": "通胀反复可能导致降息节奏慢于市场预期。",
            "source": "美联储会议纪要",
            "source_type": "官方文件",
        },
        {
            "point": "部分成长股估值已经提前反映乐观预期。",
            "source": "Morgan Stanley 市场展望",
            "source_type": "机构观点",
        },
        {
            "point": "高利率维持更久可能压制企业盈利和融资环境。",
            "source": "宏观策略周报",
            "source_type": "研究报告",
        },
    ],
    "watch_next": [
        {
            "priority": "高优先级",
            "item": "下一次 CPI 数据",
            "why": "决定市场是否继续交易降息预期。",
        },
        {
            "priority": "中优先级",
            "item": "非农就业数据",
            "why": "影响市场对经济韧性的判断。",
        },
        {
            "priority": "中优先级",
            "item": "美联储点阵图变化",
            "why": "反映政策制定者对未来利率路径的集体判断。",
        },
        {
            "priority": "高优先级",
            "item": "10 年期美债收益率",
            "why": "直接影响风险资产估值和资金成本。",
        },
        {
            "priority": "低优先级",
            "item": "科技股财报中的盈利指引",
            "why": "用于观察利率变化是否传导到企业预期。",
        },
    ],
}


def get_event_analysis_result():
    if "event_analysis_result" in st.session_state:
        return st.session_state.event_analysis_result
    return None


def get_report_analysis_result():
    if "report_analysis_result" in st.session_state:
        return st.session_state.report_analysis_result
    return None


def render_header(title, description):
    st.markdown(
        f"""
        <div class="ifin-hero-v2">
            <div class="ifin-kicker">Read the market, not predict it</div>
            <h1>{title}</h1>
            <p class="ifin-hero-subtitle">{description}</p>
            <div class="ifin-hero-note">iFin 帮助你理解市场，而不是预测市场。</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_note_box(target, source_page):
    st.markdown("### My Note")
    st.caption("Record your own reading, question, or follow-up point. This MVP stores notes in session state only.")
    attitude = st.radio(
        "Attitude",
        NOTE_ATTITUDES,
        horizontal=True,
        key=f"attitude-{source_page}",
    )
    content = st.text_area(
        "Note",
        placeholder="Write your understanding, questions, or follow-up observation points...",
        key=f"note-text-{source_page}",
    )
    if st.button("Save note", key=f"save-note-{source_page}"):
        if content.strip():
            st.session_state.saved_notes.insert(
                0,
                {
                    "target": target,
                    "source_page": source_page,
                    "attitude": attitude,
                    "content": content.strip(),
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                },
            )
            st.success("Note saved in this session.")
        else:
            st.warning("Please write a note before saving.")

    related_notes = [note for note in st.session_state.saved_notes if note["source_page"] == source_page]
    for note in related_notes[:2]:
        render_note(note)


def render_event_section_title(title):
    st.markdown(f'<div class="ifin-section-title">{title}</div>', unsafe_allow_html=True)


def render_view_points(title, points, badge_class):
    st.markdown(f"#### {title}")
    for item in points:
        st.markdown(
            f"""
            <div class="ifin-view-card">
                <span class="ifin-mini-badge {badge_class}">{title}</span>
                <div class="ifin-card-body">{item["point"]}</div>
                <div class="ifin-view-source">来源：{item["source"]} · {item["source_type"]}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
