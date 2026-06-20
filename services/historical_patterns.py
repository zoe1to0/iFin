"""Deterministic historical-pattern library for Event V2 cards."""

from __future__ import annotations

from copy import deepcopy


HISTORICAL_PATTERNS: dict[str, list[dict[str, str]]] = {
    "gold": [
        {
            "historical_event": "2020年全球流动性宽松与避险需求上升",
            "trigger": "主要央行快速宽松、实际利率下行，市场避险需求增加。",
            "market_reaction": "黄金价格与黄金ETF关注度上升，黄金股表现出现分化。",
            "current_similarity": "当前同样需要同时观察实际利率、美元与避险需求，而不能只看单一价格变化。",
        }
    ],
    "oil": [
        {
            "historical_event": "2022年地缘冲突引发能源供应担忧",
            "trigger": "供应中断预期、制裁与低库存共同改变原油供需判断。",
            "market_reaction": "油价和能源股波动显著放大，通胀预期同步受到影响。",
            "current_similarity": "当前若出现地缘扰动或OPEC+政策变化，也需要区分短期供应冲击与实际需求趋势。",
        }
    ],
    "bitcoin": [
        {
            "historical_event": "2022年全球流动性收紧与加密市场去杠杆",
            "trigger": "主要央行加息、风险偏好下降，行业内部杠杆与信用事件集中暴露。",
            "market_reaction": "比特币与其他风险资产同步承压，波动率和清算规模上升。",
            "current_similarity": "当前仍需把美元流动性、ETF资金流和杠杆水平放在同一框架中观察。",
        }
    ],
    "fed_rate_cut": [
        {
            "historical_event": "2019年美联储预防式降息",
            "trigger": "全球增长放缓、贸易不确定性上升，但美国经济尚未进入明显衰退。",
            "market_reaction": "利率预期、美元与成长资产估值重新定价，市场对降息原因存在分歧。",
            "current_similarity": "当前同样需要区分降息是为了预防风险，还是为了应对已经恶化的经济数据。",
        }
    ],
    "cpi": [
        {
            "historical_event": "2021至2022年美国通胀持续高于预期",
            "trigger": "供应链约束、商品价格、住房和服务成本共同推高通胀。",
            "market_reaction": "美债收益率与加息预期上升，高估值资产承受更大折现压力。",
            "current_similarity": "当前CPI仍需拆分核心通胀、住房和服务分项，判断通胀是否具有持续性。",
        }
    ],
    "nonfarm": [
        {
            "historical_event": "2023年美国就业数据逐步降温但保持韧性",
            "trigger": "新增就业放缓、工资增速回落，同时失业率仍处相对低位。",
            "market_reaction": "市场在软着陆与利率维持更久之间反复调整预期。",
            "current_similarity": "当前非农也不能只看新增就业，需要结合工资、失业率和劳动参与率判断。",
        }
    ],
    "nvidia": [
        {
            "historical_event": "2023年生成式AI需求推动英伟达业绩预期重估",
            "trigger": "云厂商扩大AI资本开支，数据中心GPU需求与管理层指引明显增强。",
            "market_reaction": "市场快速上调收入和盈利预期，同时对供应约束与估值敏感度提高。",
            "current_similarity": "当前仍需验证云厂商CAPEX、GPU供给和AI需求能否持续转化为收入。",
        }
    ],
    "ai_chip": [
        {
            "historical_event": "2023至2024年AI基础设施资本开支加速",
            "trigger": "大型云厂商扩建算力基础设施，先进GPU、HBM和先进封装需求上升。",
            "market_reaction": "AI芯片与供应链估值上升，但产业链不同环节表现明显分化。",
            "current_similarity": "当前仍需区分真实订单增长、供给瓶颈与估值扩张三种驱动。",
        }
    ],
    "new_energy_vehicle": [
        {
            "historical_event": "2023至2024年新能源汽车价格竞争加剧",
            "trigger": "行业产能扩张、渗透率提升放缓，车企通过降价争夺市场份额。",
            "market_reaction": "销量与市场关注度上升，但整车和供应链利润率承压。",
            "current_similarity": "当前同样需要同时观察销量、折扣、库存与单车盈利，避免只看交付量。",
        }
    ],
}


def resolve_historical_topic(query: str) -> str:
    """Resolve a supported historical-pattern key with specific topics first."""
    text = (query or "").lower()
    rules = [
        (["英伟达", "nvidia", "nvda"], "nvidia"),
        (["ai芯片", "ai chip"], "ai_chip"),
        (["新能源车", "电动车", "electric vehicle", "ev market"], "new_energy_vehicle"),
        (["美国cpi", "cpi", "通胀数据", "consumer price"], "cpi"),
        (["美国非农", "非农", "nfp", "nonfarm", "payrolls"], "nonfarm"),
        (["美联储降息", "fed rate cut", "rate cut"], "fed_rate_cut"),
        (["黄金", "gold", "xau"], "gold"),
        (["原油", "布油", "wti", "brent", "crude oil"], "oil"),
        (["比特币", "bitcoin", "btc"], "bitcoin"),
    ]
    for keywords, topic in rules:
        if any(keyword in text for keyword in keywords):
            return topic
    return ""


def get_historical_patterns(query: str) -> dict:
    """Return normalized historical patterns or an explicit empty state."""
    topic = resolve_historical_topic(query)
    patterns = deepcopy(HISTORICAL_PATTERNS.get(topic, []))
    return {
        "topic": topic,
        "status": "available" if patterns else "empty",
        "patterns": patterns,
        "empty_message": "" if patterns else "暂无匹配的历史模式。",
    }

