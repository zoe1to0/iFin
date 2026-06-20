"""Deterministic watch-metric library for Event V2 cards."""

from __future__ import annotations

from copy import deepcopy

from services.historical_patterns import resolve_historical_topic


WATCH_METRICS: dict[str, list[dict[str, str]]] = {
    "gold": [
        {"metric": "DXY 美元指数", "reason": "美元强弱会影响黄金的相对定价与资金吸引力。"},
        {"metric": "美国10年期实际利率", "reason": "实际利率代表持有黄金的机会成本。"},
        {"metric": "黄金ETF净流入", "reason": "ETF资金流可辅助观察金融投资需求变化。"},
        {"metric": "央行购金", "reason": "央行需求是黄金中长期需求的重要组成部分。"},
    ],
    "oil": [
        {"metric": "EIA商业原油库存", "reason": "库存变化是短期供需平衡的重要观察指标。"},
        {"metric": "OPEC+产量", "reason": "产量政策会直接影响全球原油供应预期。"},
        {"metric": "Brent近远月价差", "reason": "期限结构可反映现货市场松紧程度。"},
        {"metric": "炼厂开工率", "reason": "炼厂需求影响原油去库存节奏。"},
    ],
    "bitcoin": [
        {"metric": "比特币现货ETF净流入", "reason": "ETF流量可辅助观察机构资金需求。"},
        {"metric": "稳定币总供应量", "reason": "稳定币供应是加密市场流动性的代理指标。"},
        {"metric": "永续合约资金费率", "reason": "资金费率可反映短期杠杆方向与拥挤程度。"},
        {"metric": "期货未平仓合约", "reason": "未平仓量快速上升可能增加清算风险。"},
    ],
    "fed_rate_cut": [
        {"metric": "核心PCE", "reason": "核心PCE是美联储判断通胀趋势的重要指标。"},
        {"metric": "失业率", "reason": "就业恶化程度会影响降息的必要性与节奏。"},
        {"metric": "美国2年期国债收益率", "reason": "短端收益率对政策利率预期更敏感。"},
        {"metric": "联邦基金利率期货", "reason": "期货隐含概率可观察市场对降息路径的定价。"},
    ],
    "cpi": [
        {"metric": "核心CPI环比", "reason": "环比变化更能反映近期基础通胀动能。"},
        {"metric": "住房分项", "reason": "住房成本在CPI中权重较高且变化通常滞后。"},
        {"metric": "核心服务通胀", "reason": "服务价格有助于判断通胀粘性。"},
        {"metric": "消费者通胀预期", "reason": "预期失锚可能影响工资和价格行为。"},
    ],
    "nonfarm": [
        {"metric": "新增非农就业", "reason": "反映企业整体招聘需求。"},
        {"metric": "失业率", "reason": "用于判断劳动力市场是否明显转弱。"},
        {"metric": "平均时薪同比", "reason": "工资增速与服务通胀压力相关。"},
        {"metric": "劳动参与率", "reason": "参与率帮助区分就业变化来自需求还是劳动力供给。"},
    ],
    "nvidia": [
        {"metric": "GPU出货量", "reason": "出货节奏直接影响数据中心收入兑现。"},
        {"metric": "HBM价格与供给", "reason": "HBM是高端AI加速卡的重要供应约束。"},
        {"metric": "云厂商CAPEX", "reason": "大型云厂商资本开支决定核心AI基础设施需求。"},
        {"metric": "AI推理需求", "reason": "推理工作负载决定AI算力需求能否从训练扩展到应用。"},
    ],
    "ai_chip": [
        {"metric": "云厂商AI CAPEX", "reason": "资本开支是AI芯片需求的重要领先指标。"},
        {"metric": "先进封装产能", "reason": "先进封装可能限制高端GPU实际交付能力。"},
        {"metric": "HBM价格与库存", "reason": "HBM供需影响AI芯片成本和出货节奏。"},
        {"metric": "出口管制范围", "reason": "政策变化会影响可服务市场与产品组合。"},
    ],
    "new_energy_vehicle": [
        {"metric": "月度销量与渗透率", "reason": "用于判断终端需求和行业景气度。"},
        {"metric": "终端折扣率", "reason": "折扣变化可反映价格竞争强度。"},
        {"metric": "动力电池价格", "reason": "电池成本影响整车成本与供应链利润。"},
        {"metric": "渠道库存", "reason": "库存上升可能意味着需求放缓或供给过剩。"},
    ],
}


def get_watch_metrics(query: str) -> dict:
    """Return normalized watch metrics or an explicit empty state."""
    topic = resolve_historical_topic(query)
    metrics = deepcopy(WATCH_METRICS.get(topic, []))
    return {
        "topic": topic,
        "status": "available" if metrics else "empty",
        "metrics": metrics,
        "empty_message": "" if metrics else "暂无匹配的关注指标。",
    }

