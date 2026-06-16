"""Rule-based Event Analysis query interpretation.

This module normalizes vague user inputs before news retrieval. It does not use
an LLM and does not call external APIs.
"""

from __future__ import annotations


def _unique(items: list[str]) -> list[str]:
    seen = set()
    result = []
    for item in items:
        normalized = item.strip()
        if normalized and normalized.lower() not in seen:
            seen.add(normalized.lower())
            result.append(normalized)
    return result


def _base_response(raw_query: str, normalized_query: str) -> dict:
    return {
        "raw_query": raw_query,
        "normalized_query": normalized_query,
        "primary_intent": "vague_query",
        "intent_label": "模糊查询",
        "assumption": f"暂将“{normalized_query or raw_query}”理解为一个需要进一步明确的市场主题。",
        "candidate_topics": [],
        "search_query": normalized_query,
        "search_keywords": _unique([normalized_query]),
    }


def _set_result(
    result: dict,
    primary_intent: str,
    intent_label: str,
    assumption: str,
    candidate_topics: list[dict[str, str]],
    keywords: list[str],
) -> dict:
    result["primary_intent"] = primary_intent
    result["intent_label"] = intent_label
    result["assumption"] = assumption
    result["candidate_topics"] = candidate_topics
    result["search_keywords"] = _unique([result["normalized_query"], *keywords])
    result["search_query"] = " ".join(result["search_keywords"])
    return result


def interpret_event_query(query: str) -> dict:
    """Interpret a user event query into retrieval intent and stable keywords."""
    raw_query = query or ""
    normalized_query = " ".join(raw_query.strip().split())
    result = _base_response(raw_query, normalized_query)
    lower_query = normalized_query.lower()

    if not normalized_query:
        return result

    if "黄金" in normalized_query or "gold" in lower_query:
        keywords = [
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
            "央行购金",
            "central bank gold buying",
        ]
        topics = [
            {"label": "黄金价格持续上涨", "query": "黄金价格持续上涨 gold price safe haven real yield dollar"},
            {"label": "黄金股与有色金属板块走强", "query": "黄金股 有色金属板块走强 gold miners precious metals"},
            {"label": "美元指数与实际利率变化", "query": "美元指数 实际利率 美债收益率 gold real yield dollar"},
            {"label": "央行购金与避险需求", "query": "央行购金 黄金 避险需求 central bank gold buying safe haven"},
            {"label": "黄金供需与贵金属板块", "query": "黄金供需 贵金属 precious metals gold supply demand"},
        ]
        return _set_result(
            result,
            "asset_trend",
            "资产走势",
            f"暂将“{normalized_query}”理解为黄金资产与相关板块的市场动向。",
            topics,
            keywords,
        )

    if "美债" in normalized_query or any(
        term in lower_query for term in ["treasury", "bond yield", "us yield"]
    ):
        keywords = [
            "美债",
            "美债收益率",
            "Treasury yield",
            "bond yield",
            "real yield",
            "Fed",
            "interest rate",
            "美元",
        ]
        topics = [
            {"label": "10年期美债收益率变化", "query": "10年期美债收益率 Treasury yield interest rate"},
            {"label": "实际利率与美元指数", "query": "实际利率 美元指数 real yield dollar"},
            {"label": "美联储政策预期", "query": "美联储 Fed FOMC interest rate expectation"},
            {"label": "风险资产估值压力", "query": "美债收益率 风险资产 估值压力 treasury yield valuation"},
        ]
        return _set_result(
            result,
            "macro_topic",
            "宏观主题",
            f"暂将“{normalized_query}”理解为美债收益率、利率预期与风险资产估值相关的宏观主题。",
            topics,
            keywords,
        )

    if any(term in normalized_query for term in ["美联储", "降息", "加息", "利率"]) or any(
        term in lower_query for term in ["fed", "fomc", "rate cut", "interest rate"]
    ):
        keywords = ["美联储", "Fed", "Federal Reserve", "FOMC", "降息", "加息", "interest rate", "rate cut"]
        topics = [
            {"label": "美联储政策路径", "query": "美联储 Fed FOMC interest rate policy"},
            {"label": "降息 / 加息预期", "query": "降息 加息 rate cut interest rate expectation"},
            {"label": "美元与美债收益率", "query": "美元 美债收益率 dollar treasury yield"},
            {"label": "风险偏好变化", "query": "risk appetite liquidity Fed rate"},
        ]
        return _set_result(
            result,
            "macro_event",
            "宏观事件",
            f"暂将“{normalized_query}”理解为美联储政策与利率预期相关的宏观事件。",
            topics,
            keywords,
        )

    if any(term in normalized_query for term in ["AI", "人工智能", "芯片", "半导体", "英伟达"]) or any(
        term in lower_query for term in ["ai", "nvidia", "chip", "semiconductor"]
    ):
        keywords = ["AI", "人工智能", "芯片", "半导体", "NVIDIA", "Nvidia", "semiconductor", "chip", "export control"]
        topics = [
            {"label": "AI 产业链", "query": "AI 人工智能 semiconductor chip"},
            {"label": "芯片 / 半导体", "query": "芯片 半导体 semiconductor chip"},
            {"label": "英伟达相关事件", "query": "NVIDIA Nvidia AI chip earnings"},
            {"label": "出口限制 / 管制", "query": "AI chip export restriction export control"},
        ]
        return _set_result(
            result,
            "sector_trend",
            "行业板块",
            f"暂将“{normalized_query}”理解为 AI、芯片与半导体产业链的市场动向。",
            topics,
            keywords,
        )

    if any(term in normalized_query for term in ["地产", "房地产", "楼市"]):
        keywords = ["地产", "房地产", "楼市", "property", "real estate", "housing market", "mortgage"]
        topics = [
            {"label": "地产政策", "query": "房地产 地产政策 property policy"},
            {"label": "楼市销售", "query": "楼市 房地产销售 housing market sales"},
            {"label": "房企信用风险", "query": "房企 债务 信用风险 property developer debt"},
        ]
        return _set_result(
            result,
            "sector_trend",
            "行业板块",
            f"暂将“{normalized_query}”理解为房地产与楼市相关板块的市场动向。",
            topics,
            keywords,
        )

    if any(term in normalized_query for term in ["财报", "业绩", "营收", "利润"]) or any(
        term in lower_query for term in ["earnings", "revenue", "profit"]
    ):
        keywords = ["财报", "业绩", "营收", "利润", "earnings", "revenue", "profit", "guidance"]
        topics = [
            {"label": "财报核心数据", "query": "earnings revenue profit guidance"},
            {"label": "管理层展望", "query": "management guidance earnings outlook"},
            {"label": "盈利质量", "query": "profit margin cash flow earnings quality"},
        ]
        return _set_result(
            result,
            "earnings_event",
            "财报事件",
            f"暂将“{normalized_query}”理解为财报、业绩与经营变化相关事件。",
            topics,
            keywords,
        )

    if any(term in normalized_query for term in ["政策", "刺激", "出口限制", "出口管制"]) or any(
        term in lower_query for term in ["regulation", "export control", "export restriction", "stimulus"]
    ):
        keywords = ["政策", "刺激", "regulation", "stimulus", "出口限制", "出口管制", "export control", "export restriction"]
        topics = [
            {"label": "政策变化", "query": "政策 regulation policy change"},
            {"label": "刺激政策", "query": "刺激政策 stimulus policy"},
            {"label": "出口限制 / 管制", "query": "出口限制 出口管制 export control export restriction"},
        ]
        return _set_result(
            result,
            "policy_event",
            "政策事件",
            f"暂将“{normalized_query}”理解为政策变化或监管约束相关事件。",
            topics,
            keywords,
        )

    return result


if __name__ == "__main__":
    import json

    for item in ["黄金", "美联储", "AI", "地产", "Nvidia earnings"]:
        print(json.dumps(interpret_event_query(item), ensure_ascii=False, indent=2))
