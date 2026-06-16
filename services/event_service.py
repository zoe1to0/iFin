"""Mock Event Analysis pipeline.

Pipeline:
User Input -> Prompt Builder -> Mock LLM Response -> Parser -> Structured Dict

This module does not call any real LLM API.
"""

import json
import re
from html import unescape

from parsers.event_parser import parse_event_response
from prompts.event_prompt import build_event_prompt
from services.event_query_interpreter import interpret_event_query
from services.market_data_service import MarketDataService
from services.news_pipeline import search_event_news
from services.theme_packages import DATA_PACK_EXPLANATIONS, get_theme_package
from services.topic_router import route_topic

try:
    from services.llm_service import LLMService, PLACEHOLDER_MESSAGE
except ImportError:
    LLMService = None
    PLACEHOLDER_MESSAGE = "LLM integration not enabled yet"


HTML_TAG_PATTERN = re.compile(r"</?(div|span|p|br)\b[^>]*>", re.IGNORECASE)


def _clean_html_text(value: str) -> str:
    return HTML_TAG_PATTERN.sub("", unescape(value or "")).strip()


def _clean_html_tags(value):
    if isinstance(value, str):
        return _clean_html_text(value)
    if isinstance(value, list):
        return [_clean_html_tags(item) for item in value]
    if isinstance(value, dict):
        return {key: _clean_html_tags(item) for key, item in value.items()}
    return value


def _build_market_data_context(
    user_input: str,
    search_query: str,
    interpretation: dict,
    topic_info: dict,
) -> dict:
    """Resolve a topic package data_pack into normalized market data."""
    _ = interpretation
    query_text = f"{user_input or ''} {search_query or ''}".lower()
    service = MarketDataService()
    data_pack = list(topic_info.get("data_pack", []) or [])

    if topic_info.get("topic_type") == "company" and any(
        keyword in query_text for keyword in ["nvda", "nvidia", "英伟达"]
    ):
        data_pack = ["nvda"]

    data_resolvers = {
        "gold": service.get_gold_data,
        "dxy": service.get_dxy_data,
        "us10y": service.get_us10y_data,
        "gld": service.get_gold_etf_data,
        "nvda": lambda: service.get_equity_or_etf_data("NVDA", "英伟达"),
        "qqq": lambda: service.get_equity_or_etf_data("QQQ", "纳斯达克100 ETF"),
        "ai_etf": lambda: (
            service.get_equity_or_etf_data("BOTZ", "AI相关ETF")
            if not service.get_equity_or_etf_data("BOTZ", "AI相关ETF").get("is_mock")
            else service.get_equity_or_etf_data("AIQ", "AI相关ETF")
        ),
        "amd": lambda: service.get_equity_or_etf_data("AMD", "AMD"),
        "soxx": lambda: service.get_equity_or_etf_data("SOXX", "半导体ETF"),
        "tsm": lambda: service.get_equity_or_etf_data("TSM", "台积电"),
        "sp500": lambda: service.get_equity_or_etf_data("^GSPC", "标普500"),
        "vix": lambda: service.get_equity_or_etf_data("^VIX", "VIX"),
        "btc": lambda: service.get_equity_or_etf_data("BTC-USD", "比特币"),
        "eth": lambda: service.get_equity_or_etf_data("ETH-USD", "以太坊"),
        "wti": lambda: service.get_equity_or_etf_data("CL=F", "WTI原油"),
        "brent": lambda: service.get_equity_or_etf_data("BZ=F", "Brent原油"),
    }

    market_data_context = {}
    for key in data_pack:
        resolver = data_resolvers.get(key)
        if resolver is None:
            continue
        try:
            market_data_context[key] = resolver()
        except Exception:
            continue
    return market_data_context


def _summarize_market_data(market_data_context: dict) -> tuple[str, str, bool]:
    """Return as_of, source, and availability summary for result metadata."""
    if not market_data_context:
        return "", "", False
    as_of_values = []
    source_values = []
    has_real_data = False
    for data in market_data_context.values():
        if not isinstance(data, dict):
            continue
        if data.get("is_mock"):
            continue
        has_real_data = True
        if data.get("as_of"):
            as_of_values.append(str(data["as_of"]))
        if data.get("source"):
            source_values.append(str(data["source"]))
    return (
        " / ".join(dict.fromkeys(as_of_values)),
        " / ".join(dict.fromkeys(source_values)),
        has_real_data,
    )


def _real_market_data_items(market_data_context: dict | None) -> list[dict]:
    """Flatten real market data items for UI rendering."""
    if not isinstance(market_data_context, dict):
        return []
    return [
        item
        for item in market_data_context.values()
        if isinstance(item, dict) and item.get("is_mock") is False
    ]


def _build_evidence_pool(news_result: dict) -> list[dict]:
    """Build a lightweight news evidence pool from retrieved news."""
    if not isinstance(news_result, dict):
        return []

    raw_items = news_result.get("items") or []
    if not raw_items:
        titles = news_result.get("titles", []) or []
        sources = news_result.get("sources", []) or []
        raw_items = []
        for index, title in enumerate(titles):
            source_item = sources[index] if index < len(sources) else {}
            raw_items.append(
                {
                    "title": title,
                    "source": source_item.get("source", "") if isinstance(source_item, dict) else "",
                    "date": source_item.get("date", "") if isinstance(source_item, dict) else "",
                    "url": source_item.get("url", "") if isinstance(source_item, dict) else "",
                    "summary": "",
                }
            )

    evidence_pool = []
    for index, item in enumerate(raw_items, start=1):
        if not isinstance(item, dict):
            continue
        evidence_pool.append(
            {
                "id": f"news_{index}",
                "title": item.get("title", ""),
                "source": item.get("source", ""),
                "date": item.get("date", ""),
                "url": item.get("url", ""),
                "summary": item.get("summary", ""),
            }
        )
    return _clean_html_tags(evidence_pool)


def _apply_market_data_to_analysis(result: dict, market_data_context: dict) -> dict:
    """Attach normalized market data to market_position and key_data fields."""
    if not market_data_context:
        return result

    market_items = [
        (key, data)
        for key, data in market_data_context.items()
        if isinstance(data, dict)
    ]
    result["market_position"] = [
        {
            "name": data.get("label") or key.upper(),
            "position": "待行情数据接入" if data.get("is_mock") else "已接入行情数据",
            "direction": "不确定",
            "percentile": data.get("percentile_1y", "暂不计算历史分位"),
            "peer_position": "待数据接入",
            "current": data.get("current", ""),
            "change_1d": data.get("change_1d", ""),
            "change_1m": data.get("change_1m", ""),
            "change_3m": data.get("change_3m", ""),
            "change_1y": data.get("change_1y", ""),
            "percentile_1y": data.get("percentile_1y", ""),
            "as_of": data.get("as_of", ""),
            "period": data.get("period", ""),
            "source": data.get("source", ""),
            "is_mock": data.get("is_mock", False),
            "data_note": (
                "实时行情暂未接入，本项仅为内部状态。"
                if data.get("is_mock")
                else f"以 {data.get('as_of', '可得数据')} 可得数据为基准。"
            ),
            "explanation": DATA_PACK_EXPLANATIONS.get(
                key,
                "该指标用于观察当前主题下的核心行情变量。",
            ),
        }
        for key, data in market_items
    ]

    result["key_data"] = [
        {
            "name": data.get("label") or key.upper(),
            "trend": "待真实数据源验证" if data.get("is_mock") else "已接入行情数据",
            "explanation": DATA_PACK_EXPLANATIONS.get(
                key,
                "用于观察当前主题下的核心行情变量。",
            ),
            "current": data.get("current", ""),
            "change_1d": data.get("change_1d", ""),
            "change_1m": data.get("change_1m", ""),
            "change_3m": data.get("change_3m", ""),
            "change_1y": data.get("change_1y", ""),
            "percentile_1y": data.get("percentile_1y", ""),
            "as_of": data.get("as_of", ""),
            "period": data.get("period", ""),
            "source": data.get("source", ""),
            "is_mock": data.get("is_mock", True),
            "data_note": (
                "实时行情暂未接入，本项仅为内部状态。"
                if data.get("is_mock")
                else f"以 {data.get('as_of', '可得数据')} 可得数据为基准。"
            ),
        }
        for key, data in market_items
    ]
    return result


def _build_topic_logic_chain(user_input: str, topic_info: dict | None = None) -> list[dict]:
    """Build a topic-aware impact chain for mock fallback output."""
    topic_info = topic_info or {}
    package = get_theme_package(topic_info.get("topic_type", "general"))
    selected_chain = topic_info.get("logic_chain_template") or package.get(
        "logic_chain_template",
        [],
    )
    return [
        {
            "step": f"Step {index}",
            "title": item.get("title", "推导步骤"),
            "content": item.get("content") or (user_input if index == 1 else item.get("title", "")),
            "description": item.get("description", ""),
            "evidence_ids": [],
        }
        for index, item in enumerate(selected_chain, start=1)
        if isinstance(item, dict)
    ]


def _mock_event_llm_response(
    user_input: str,
    prompt: str,
    interpretation: dict | None = None,
    topic_info: dict | None = None,
) -> str:
    """Return a JSON string shaped like a future LLM response."""
    _ = prompt
    interpretation = interpretation or {}
    logic_chain = _build_topic_logic_chain(user_input, topic_info)
    if interpretation.get("primary_intent") == "asset_trend" and (
        "黄金" in user_input or "gold" in user_input.lower()
    ):
        mock_response = {
            "event_summary": (
                "当前输入更适合作为黄金资产动向来理解，而不是单一事件。公开新闻语境下，黄金通常需要同时观察"
                "实际利率、美元指数、避险情绪、央行购金和黄金股板块表现。由于尚未接入实时行情和历史分位数据，"
                "本次分析只用于梳理驱动因素与后续观察方向，不构成投资建议。"
            ),
            "market_position": [
                {
                    "name": "黄金现货价格",
                    "position": "新闻语境判断",
                    "direction": "不确定",
                    "percentile": "暂不计算历史分位",
                    "peer_position": "待行情数据接入",
                    "data_note": "当前为新闻语境判断，非实时行情计算",
                    "explanation": "未接入实时金价和历史区间数据，因此只根据相关新闻语境判断黄金是否处在被关注的位置。",
                },
                {
                    "name": "黄金股 / 有色金属板块",
                    "position": "新闻语境判断",
                    "direction": "不确定",
                    "percentile": "暂不计算历史分位",
                    "peer_position": "待行情数据接入",
                    "data_note": "当前为新闻语境判断，非实时行情计算",
                    "explanation": "黄金股往往同时受金价、成本、汇率和风险偏好影响，需要后续接入板块行情再判断强弱。",
                },
                {
                    "name": "美元与实际利率",
                    "position": "关键观察变量",
                    "direction": "不确定",
                    "percentile": "暂不计算历史分位",
                    "peer_position": "待宏观数据接入",
                    "data_note": "当前为新闻语境判断，非实时行情计算",
                    "explanation": "黄金对实际利率和美元变化较敏感，但当前未计算实时利率区间，因此只作为传导变量观察。",
                },
            ],
            "key_data": [
                {
                    "name": "新闻检索线索",
                    "trend": "需要继续验证",
                    "explanation": "当前结果主要来自新闻检索与主题解释，尚未接入实时行情、成交量和历史分位。",
                }
            ],
            "logic_chain": logic_chain,
            "historical_cases": [
                {
                    "year": "历史阶段",
                    "title": "避险需求上升时期的黄金关注度提升",
                    "market_reaction": "黄金通常会被作为避险资产重新定价，但不同阶段驱动因素可能不同。",
                    "risk": "如果美元或实际利率重新走强，黄金叙事可能受到压制。",
                    "similarity": "都涉及避险、利率和美元变量的共同影响。",
                    "limitation": "缺少当前实时行情和完整历史样本，不能简单类比。",
                    "source": "需后续数据源补强",
                    "url": "",
                }
            ],
            "bull_case": [
                {
                    "point": "如果实际利率下行或避险需求升温，黄金关注度可能继续保持。",
                    "detail": "黄金的吸引力常与资金成本、美元强弱和避险情绪相关，需要继续观察这些变量是否同向支持。",
                    "source": "公开新闻语境",
                    "url": "",
                    "source_type": "",
                }
            ],
            "bear_case": [
                {
                    "point": "如果美元走强或实际利率上行，黄金可能面临解释压力。",
                    "detail": "黄金不产生现金流，对利率和美元变化较敏感；如果宏观变量反向变化，市场叙事可能降温。",
                    "source": "公开新闻语境",
                    "url": "",
                    "source_type": "",
                }
            ],
            "risk_radar": [
                {
                    "risk": "数据不足风险",
                    "level": "中",
                    "reason": "尚未接入实时金价、美元指数、实际利率和黄金股板块数据。",
                    "linked_data": "黄金价格、美元指数、实际利率、黄金股板块表现",
                    "historical_reference": "需要后续数据源补强。",
                    "source": "新闻语境 + 模型归纳",
                    "url": "",
                }
            ],
            "insight": "黄金不是单一新闻事件，而是一组宏观变量、避险情绪和相关板块共同作用下的资产主题。",
            "next_watch": [
                {
                    "item": "美元指数与实际利率变化",
                    "query": "美元指数 实际利率 黄金 gold real yield dollar",
                    "description": "黄金价格往往同时受实际利率和美元指数影响，继续观察有助于判断上涨来自趋势延续还是短期避险。",
                    "source": "公开新闻语境",
                    "url": "",
                },
                {
                    "item": "央行购金与避险需求",
                    "query": "央行购金 黄金 避险需求 central bank gold buying safe haven",
                    "description": "央行购金和避险情绪会改变市场对黄金需求的理解，适合与价格走势一起观察。",
                    "source": "公开新闻语境",
                    "url": "",
                },
                {
                    "item": "黄金股与有色金属板块",
                    "query": "黄金股 有色金属 黄金价格 gold miners precious metals",
                    "description": "黄金股可能放大金价变化，也会受到成本、汇率和风险偏好的影响。",
                    "source": "公开新闻语境",
                    "url": "",
                },
            ],
        }
        return json.dumps(mock_response, ensure_ascii=False)

    mock_response = {
        "event_summary": (
            f"事件：{user_input}。该事件的核心在于市场需要重新理解政策、数据或预期变化"
            "如何影响风险偏好与资产定价。"
        ),
        "market_position": [
            {
                "indicator": "风险偏好",
                "position": "中性偏高",
                "explanation": "市场处在对政策信号较敏感的位置。",
            }
        ],
        "key_data": [
            {
                "name": "关键利率 / 预期变量",
                "trend": "evidence_insufficient",
                "explanation": "当前为 mock pipeline，尚未接入真实数据源。",
            }
        ],
        "logic_chain": logic_chain,
        "historical_cases": [],
        "bull_case": [
            {
                "point": "如果后续数据支持更温和的政策路径，市场情绪可能获得一定支撑。",
                "source": "mock_source",
                "source_type": "mock",
            }
        ],
        "bear_case": [
            {
                "point": "如果证据不足或数据反复，市场可能修正此前预期。",
                "source": "mock_source",
                "source_type": "mock",
            }
        ],
        "risk_radar": [
            {
                "name": "证据不足风险",
                "level": "中",
                "source": "evidence_insufficient",
                "reason": "尚未接入真实新闻、行情或宏观数据。",
            }
        ],
        "insight": "先理解事件如何改变预期，再观察这种预期是否被后续证据验证。",
        "next_watch": [
            {
                "item": "后续数据与官方表述",
                "priority": "高",
                "why": "用于判断当前市场解读是否有证据支撑。",
            }
        ],
    }
    return json.dumps(mock_response, ensure_ascii=False)


def _has_meaningful_analysis(data: dict) -> bool:
    """Return True when parsed LLM data contains content worth rendering."""
    if not isinstance(data, dict):
        return False
    required_fields = [
        "event_summary",
        "logic_chain",
        "bull_case",
        "bear_case",
        "risk_radar",
        "insight",
        "next_watch",
    ]
    non_empty_count = sum(1 for field in required_fields if data.get(field))
    return non_empty_count >= 4


def _safe_news_result(user_input: str) -> dict:
    """Return event news context, or a safe empty result if retrieval fails."""
    try:
        news_result = search_event_news(user_input)
        if isinstance(news_result, dict):
            return news_result
    except Exception:
        pass
    return {
        "event": user_input,
        "news_count": 0,
        "sources": [],
        "titles": [],
        "context": "",
        "items": [],
    }


def _attach_debug_fields(
    result: dict,
    titles: list,
    context: str,
    interpretation: dict,
    market_data_context: dict | None = None,
    topic_info: dict | None = None,
) -> dict:
    """Attach internal news debug metadata to the parsed analysis result."""
    market_data_as_of, market_data_source, has_market_data = _summarize_market_data(
        market_data_context or {}
    )
    result["_news_count"] = len(titles)
    result["_news_context_length"] = len(context)
    result["_intent"] = interpretation.get("primary_intent", "")
    result["_intent_label"] = interpretation.get("intent_label", "")
    result["_assumption"] = interpretation.get("assumption", "")
    result["_candidate_topics"] = interpretation.get("candidate_topics", [])
    result["_search_query"] = interpretation.get("search_query", "")
    result["_market_data_as_of"] = market_data_as_of
    result["_market_data_source"] = market_data_source
    result["_has_market_data"] = has_market_data
    result["_market_data"] = market_data_context or {}
    result["_real_market_data"] = _real_market_data_items(market_data_context)
    topic_info = topic_info or {}
    result["_topic_type"] = topic_info.get("topic_type", "")
    result["_topic_label"] = topic_info.get("topic_label", "")
    result["_data_pack"] = topic_info.get("data_pack", [])
    result["_suggested_queries"] = topic_info.get("suggested_queries", [])
    return result


def run_event_analysis(
    user_input: str,
    use_real_llm: bool = False,
) -> dict:
    """Run Event Analysis and return validated data with mock fallback."""
    interpretation = interpret_event_query(user_input)
    topic_info = route_topic(user_input)
    topic_search_terms = " ".join(topic_info.get("search_expansion", []) or [])
    search_query = " ".join(
        item
        for item in [
            interpretation.get("search_query", user_input),
            topic_search_terms,
        ]
        if item
    )
    market_data_context = _build_market_data_context(
        user_input=user_input,
        search_query=search_query,
        interpretation=interpretation,
        topic_info=topic_info,
    )
    news_result = _safe_news_result(search_query)
    titles = news_result.get("titles", []) or []
    context = news_result.get("context", "") or ""
    evidence_pool = _build_evidence_pool(news_result)
    event_data = {
        "event": user_input,
        "interpreted_intent": interpretation,
        "topic_info": topic_info,
        "titles": titles,
        "context": context,
        "market_data": market_data_context,
        "evidence_pool": evidence_pool,
    }
    prompt = build_event_prompt(event_data)
    if use_real_llm and LLMService is not None:
        try:
            raw_llm_response = LLMService().analyze_event(prompt)
            if raw_llm_response and raw_llm_response != PLACEHOLDER_MESSAGE:
                parsed_llm_response = parse_event_response(raw_llm_response)
                if _has_meaningful_analysis(parsed_llm_response):
                    parsed_llm_response = _apply_market_data_to_analysis(
                        parsed_llm_response,
                        market_data_context,
                    )
                    parsed_llm_response["evidence_pool"] = evidence_pool
                    parsed_llm_response["_source"] = "llm"
                    return _attach_debug_fields(
                        parsed_llm_response,
                        titles,
                        context,
                        interpretation,
                        market_data_context,
                        topic_info,
                    )
        except Exception:
            pass

    raw_response = _mock_event_llm_response(
        user_input=user_input,
        prompt=prompt,
        interpretation=interpretation,
        topic_info=topic_info,
    )
    parsed_mock_response = parse_event_response(raw_response)
    parsed_mock_response = _apply_market_data_to_analysis(
        parsed_mock_response,
        market_data_context,
    )
    parsed_mock_response["evidence_pool"] = evidence_pool
    parsed_mock_response["_source"] = "mock"
    return _attach_debug_fields(
        parsed_mock_response,
        titles,
        context,
        interpretation,
        market_data_context,
        topic_info,
    )
