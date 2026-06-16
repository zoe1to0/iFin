"""Standard output schema for Event Analysis.

This is a lightweight Python representation for future LLM/RAG integration.
It is not tied to any API client.
"""

EVENT_ANALYSIS_FIELDS = [
    "event_summary",
    "market_position",
    "key_data",
    "logic_chain",
    "historical_cases",
    "bull_case",
    "bear_case",
    "risk_radar",
    "insight",
    "next_watch",
    "evidence_pool",
]

EVENT_ANALYSIS_SCHEMA = {
    "event_summary": {
        "type": "string",
        "description": "A concise explanation of what happened and why it matters.",
    },
    "market_position": {
        "type": "array",
        "description": "Environment variables such as tradable market proxies, price, return, percentile, and trend.",
    },
    "key_data": {
        "type": "array",
        "description": "Event variables such as fundamental drivers, business metrics, policy variables, supply-demand variables, and macro drivers.",
    },
    "logic_chain": {
        "type": "array",
        "description": "Step-by-step impact path from event to market implications.",
    },
    "historical_cases": {
        "type": "array",
        "description": "Historical reference cases and how markets reacted then.",
    },
    "bull_case": {
        "type": "array",
        "description": "Supportive interpretation logic with sources where available.",
    },
    "bear_case": {
        "type": "array",
        "description": "Cautious interpretation logic with sources where available.",
    },
    "risk_radar": {
        "type": "array",
        "description": "Risk names, levels, reasons, and historical references.",
    },
    "insight": {
        "type": "string",
        "description": "One cognitive anchor that helps the user remember the core logic.",
    },
    "next_watch": {
        "type": "array",
        "description": "What to watch next, priority, and why each item matters.",
    },
    "evidence_pool": {
        "type": "array",
        "description": "Lightweight news evidence pool used by analysis cards.",
    },
}
