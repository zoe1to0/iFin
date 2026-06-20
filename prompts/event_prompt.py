"""Prompt builder for future Event Analysis LLM integration.

This module does not call any LLM API. It only prepares a prompt string.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

if str(Path(__file__).resolve().parents[1]) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from prompts.system_prompt import SYSTEM_PROMPT


EVENT_OUTPUT_SCHEMA = {
    "event_summary": "string",
    "market_position": [
        {
            "name": "string",
            "position": "string",
            "direction": "上升 / 下降 / 横盘 / 不确定",
            "percentile": "string",
            "peer_position": "string",
            "data_note": "string",
            "current": "string",
            "change_1d": "string",
            "change_1m": "string",
            "change_3m": "string",
            "change_1y": "string",
            "percentile_1y": "string",
            "as_of": "string",
            "period": "string",
            "source": "string",
            "is_mock": "boolean",
            "explanation": "string",
        }
    ],
    "key_data": [
        {
            "label": "string",
            "value": "string",
            "unit": "string",
            "period": "string",
            "insight": "string",
            "source": "string",
            "confidence": "estimated / cited / unavailable",
        }
    ],
    "logic_chain": [
        {
            "step": "string",
            "title": "string",
            "content": "string",
            "description": "string",
            "evidence_ids": ["string"],
        }
    ],
    "bull_case": [
        {
            "point": "string",
            "detail": "string",
            "evidence_ids": ["string"],
            "source": "string",
            "url": "string",
            "source_type": "string",
        }
    ],
    "bear_case": [
        {
            "point": "string",
            "detail": "string",
            "evidence_ids": ["string"],
            "source": "string",
            "url": "string",
            "source_type": "string",
        }
    ],
    "historical_cases": [
        {
            "year": "string",
            "title": "string",
            "market_reaction": "string",
            "risk": "string",
            "similarity": "string",
            "limitation": "string",
            "evidence_ids": ["string"],
            "source": "string",
            "url": "string",
        }
    ],
    "risk_radar": [
        {
            "risk": "string",
            "reason": "string",
            "linked_data": "string",
            "historical_reference": "string",
            "evidence_ids": ["string"],
            "source": "string",
            "url": "string",
        }
    ],
    "insight": "string",
    "next_watch": [
        {
            "item": "string",
            "query": "string",
            "description": "string",
            "evidence_ids": ["string"],
            "source": "string",
            "url": "string",
        }
    ],
    "evidence_pool": [
        {
            "id": "string",
            "title": "string",
            "source": "string",
            "date": "string",
            "url": "string",
            "summary": "string",
        }
    ],
}


def build_event_prompt(event_data: dict) -> str:
    """Build a structured event-analysis prompt from retrieved event data."""
    if not isinstance(event_data, dict):
        event_data = {
            "event": str(event_data),
            "titles": [],
            "context": "",
        }

    event = event_data.get("event", "")
    interpreted_intent = event_data.get("interpreted_intent", {}) or {}
    topic_info = event_data.get("topic_info", {}) or {}
    primary_intent = interpreted_intent.get("primary_intent", "")
    assumption = interpreted_intent.get("assumption", "")
    search_query = interpreted_intent.get("search_query", "")
    candidate_topics = interpreted_intent.get("candidate_topics", []) or []
    titles = event_data.get("titles", []) or []
    context = event_data.get("context", "")
    market_data = event_data.get("market_data", {}) or {}
    evidence_pool = event_data.get("evidence_pool", []) or []
    evidence_status = event_data.get("evidence_status", "insufficient")
    news_count = event_data.get("news_count", len(titles))
    prompt_rules = topic_info.get("prompt_rules", []) or []
    topic_info_text = (
        json.dumps(topic_info, ensure_ascii=False, indent=2)
        if topic_info
        else "{}"
    )
    candidate_topics_text = (
        "\n".join(
            f"- {item.get('label', '')}: {item.get('query', '')}"
            for item in candidate_topics
            if isinstance(item, dict)
        )
        or "- evidence_insufficient"
    )
    titles_text = "\n".join(f"- {title}" for title in titles) or "- evidence_insufficient"
    market_data_text = (
        json.dumps(market_data, ensure_ascii=False, indent=2)
        if market_data
        else "暂未接入实时行情数据"
    )
    evidence_pool_text = (
        json.dumps(evidence_pool, ensure_ascii=False, indent=2)
        if evidence_pool
        else "[]"
    )
    prompt_rules_text = (
        "\n".join(f"- {rule}" for rule in prompt_rules if isinstance(rule, str))
        or "- Use general iFin event-analysis principles."
    )

    return f"""
{SYSTEM_PROMPT.strip()}

Event name:
{event}

User raw input:
{event}

System interpretation:
{assumption or "evidence_insufficient"}

Primary intent:
{primary_intent or "evidence_insufficient"}

Topic info:
{topic_info_text}

Candidate topics:
{candidate_topics_text}

Search query:
{search_query or event or "evidence_insufficient"}

News titles:
{titles_text}

News context:
{context or "evidence_insufficient"}

Market data context:
{market_data_text}

Evidence pool:
{evidence_pool_text}

Evidence status:
{evidence_status}

Accepted news count:
{news_count}

Topic-specific prompt rules:
{prompt_rules_text}

Instructions:
- Use the Event name, News titles, and News context above as the primary evidence.
- Use Topic info to choose the correct analysis lens.
- Use the System interpretation and Primary intent to avoid over-interpreting vague inputs.
- Do not treat a vague asset or theme word as a precise event.
- Apply the Topic-specific prompt rules above before writing the final JSON.
- Broad keywords must be analyzed as a theme, sector, or asset trend, not as a single event.
- If data_pack only indicates planned future data access, do not present it as real data.
- logic_chain must be a clear research chain, not a long paragraph.
- Every logic_chain item must include step, title, content, description, and evidence_ids.
- Use exactly this chain direction for logic_chain: event/theme -> key variable -> market reaction -> asset impact.
- Choose logic_chain titles from topic_info.logic_chain_template when available.
- For logic_chain evidence_ids, reference Evidence pool items only when a specific step is directly supported by retrieved news; otherwise use [].
- For broad keywords, write event_summary as a recent market-movement overview: what current information suggests, related drivers, what evidence is still missing, and why this is not investment advice.
- Do not force a precise event narrative when the retrieved news does not support one.
- If the query is an asset/theme such as "黄金", analyze it as asset trend + related sectors + macro drivers.
- For vague queries, include the current default understanding and other possible directions in the structured analysis.
- Prioritize analysis grounded in the retrieved News context.
- Treat Evidence status as a hard evidence boundary, not as optional metadata.
- When Evidence status is "insufficient" or Accepted news count is 0, never write "公开新闻显示", "市场消息显示", "新闻显示", or imply that an event has occurred based on retrieved reporting.
- With insufficient evidence, event_summary may only state that verifiable news evidence is currently unavailable, identify the data normally needed to analyze the topic, and list information that must be added or verified.
- With insufficient evidence, bull_case and bear_case must be explicitly conditional research hypotheses, not claims about events that have occurred.
- With insufficient evidence, do not claim that any actor has acted and do not claim a market reaction. Use empty evidence_ids and natural evidence-gap wording.
- With insufficient evidence, source and url must be empty strings. Do not use generic pseudo-sources such as "公开新闻语境" or "市场消息".
- If the News context is empty or does not support a claim, explain the evidence gap in natural Chinese instead of exposing "evidence_insufficient" to the user.
- Strictly separate Environment Variables from Event Variables.
- Environment Variables belong in market_position only: tradable market proxies, prices, returns, percentile, market trend, and broader risk environment.
- Event Variables belong in key_data only: fundamental drivers, business metrics, policy variables, supply-demand variables, and macro variables directly linked to the event.
- key_data must never copy market_position. Do not put NVDA, QQQ, BOTZ, AMD, GLD, DXY, US10Y, SOXX, BTC, ETF prices, or other tradable proxy prices in key_data unless the item is explicitly a fundamental/event variable.
- If no stable data source exists for an Event Variable, output it with confidence "unavailable", value "尚未接入稳定数据源", source "待接入主题变量数据源", and a concise insight explaining why it matters.
- For AI themes, key_data examples include Cloud CAPEX, GPU demand, Data center investment, AI revenue growth, and Semiconductor supply constraint.
- For precious-metal themes, key_data examples include ETF fund flow, Central bank gold purchases, Real yield, Inflation data, and Dollar trend.
- For market_position, do not invent historical percentile, peer ranking, prices, yields, or calculated market data.
- For market_position, prioritize Market data context when it is available.
- If Market data context is provided, reflect current, change_1d, change_1m, change_3m, change_1y, percentile_1y, as_of, period, source, and is_mock when relevant.
- Only market_data items with "is_mock": false may be used as factual market data.
- If a market_data item has "is_mock": true, treat it only as an internal unavailable-data marker and do not use it as evidence.
- Use only market_data items listed in Topic info / Market data context as factual market context, and only when is_mock is false.
- When market_data is unavailable or is_mock is true, do not write fake prices, returns, percentiles, rankings, or dates.
- In data_note or explanation, clearly state the time basis, for example "以 2026-06-15 可得数据为基准" when the data source provides that date.
- Do not invent price, change percentage, percentile, ranking, source, or as_of time.
- If market_data.is_mock is true, write "示例数据，待真实数据源验证" in data_note or explanation.
- If no real market_data is available, write "暂未接入实时行情数据" instead of stiff wording such as "证据不足".
- If market_position lacks real quantitative evidence, use natural states such as "待行情数据接入", "新闻语境判断", and "暂不计算历史分位".
- For market_position names, keep concrete dimensions such as "黄金现货价格", "黄金股板块", "美元与实际利率", or other relevant market dimensions.
- For market_position explanation, explain why the current view is news-context based rather than calculated from real-time market data.
- For market_position data_note, state "当前为新闻语境判断，非实时行情计算" unless real source evidence is present.
- Do not generate fake percentile numbers such as "past 3-year top 20%" unless the news context explicitly supports them.
- For bull_case, bear_case, risk_radar, historical_cases, and next_watch, provide source, url, and detail when available from the news context.
- For bull_case, bear_case, risk_radar, historical_cases, and next_watch, reference Evidence pool items with evidence_ids when a judgment is based on specific news.
- If a judgment comes from news_1, write "evidence_ids": ["news_1"].
- If there is no direct matching evidence, write "evidence_ids": [].
- Never invent evidence_ids that do not exist in the Evidence pool.
- source and url should prioritize the Evidence pool; do not invent media names or URLs.
- If no specific source is available, use natural Chinese such as "公开新闻语境", "新闻语境 + 模型归纳", or "需后续数据源补强"; do not output "evidence_insufficient".
- Explain the event and its possible market expectation path.
- Present supportive and cautious interpretations.
- Highlight uncertainty and risk sources.
- Do not provide buy, sell, hold, target price, timing, or position advice.
- Do not predict stock prices or investment returns.
- Do not expose "evidence_insufficient" in user-facing text. Use concise natural Chinese to describe the data gap.
- Do not invent specific data, dates, prices, yields, percentages, or returns.
- Return valid strict JSON only.
- Do not include markdown.
- Do not wrap the response in a code fence.
- Do not return string arrays.
- Do not return semi-structured text.
- Every array item must be an object with exactly the fields shown in the schema.
- Do not add fields outside the expected JSON schema.

Expected JSON schema:
{json.dumps(EVENT_OUTPUT_SCHEMA, ensure_ascii=False, indent=2)}
""".strip()


if __name__ == "__main__":
    sample_event_data = {
        "event": "AI",
        "titles": [
            "AI 投资周期继续影响科技板块估值",
            "企业加大人工智能基础设施投入",
        ],
        "context": "Recent news suggests investors are watching AI infrastructure spending and valuation pressure.",
    }
    print(build_event_prompt(sample_event_data))
