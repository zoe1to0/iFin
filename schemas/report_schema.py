"""Standard output schema for Reports / Financial Analysis.

This is a lightweight Python representation for future LLM/RAG integration.
It is not tied to any API client.
"""

REPORT_ANALYSIS_FIELDS = [
    "what_happened",
    "changes",
    "expectation_check",
    "risk_signals",
    "industry_position",
    "next_watch",
    "note",
]

REPORT_ANALYSIS_SCHEMA = {
    "what_happened": {
        "type": "string",
        "description": "A concise explanation of the core changes in the current report.",
    },
    "changes": {
        "type": "array",
        "description": "Changes versus the previous period, including direction, magnitude, and explanation.",
    },
    "expectation_check": {
        "type": "array",
        "description": "Whether prior management outlook was fulfilled, with source and evidence.",
    },
    "risk_signals": {
        "type": "array",
        "description": "Risk names, levels, current signals, comparable cases, and explanations.",
    },
    "industry_position": {
        "type": "array",
        "description": "Company performance compared with industry references.",
    },
    "next_watch": {
        "type": "array",
        "description": "What to watch next, priority, and why each item matters.",
    },
    "note": {
        "type": "string",
        "description": "Optional user-facing note field for future saved records.",
    },
}
