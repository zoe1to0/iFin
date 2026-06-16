"""Static MVP data for the iFin Streamlit prototype."""

INTEREST_TAGS = [
    "AI",
    "半导体",
    "黄金",
    "新能源",
    "美股",
    "港股",
    "医药",
    "消费",
    "宏观经济",
    "加密资产",
]

HOT_TOPICS = [
    {
        "title": "AI sector pullback",
        "kind": "Event",
        "summary": "Market readings differ on valuation, earnings expectations, and enterprise purchase cycles.",
        "tags": ["AI", "Semiconductors", "US equities"],
        "updated_at": "2026-06-03 09:30",
        "target_page": "Event Analysis",
    },
    {
        "title": "Example Tech Q2 report update",
        "kind": "Report",
        "summary": "Revenue continues to grow, while growth pace and risk disclosures show new changes.",
        "tags": ["Earnings", "Technology", "US equities"],
        "updated_at": "2026-06-03 08:50",
        "target_page": "Financial Analysis",
    },
    {
        "title": "US yield move reshapes rate-sensitive assets",
        "kind": "Event",
        "summary": "The same macro signal is being interpreted differently across growth stocks, gold, and dollar assets.",
        "tags": ["Macro", "Rates", "Risk watch"],
        "updated_at": "2026-06-03 07:40",
        "target_page": "Event Analysis",
    },
]

SEARCH_RESULTS = [
    {
        "query_type": "News / event",
        "title": "AI sector pullback",
        "description": "Open a structured event reading with source differences, data explanation, and risk watch.",
        "target_page": "Event Analysis",
    },
    {
        "query_type": "Financial report",
        "title": "Example Tech Q2 report update",
        "description": "Open a financial statement reading focused on changes, data context, and risk observations.",
        "target_page": "Financial Analysis",
    },
    {
        "query_type": "Company / stock",
        "title": "Related company reading entries",
        "description": "Review connected events, reports, and key data entries before forming your own view.",
        "target_page": "Home",
    },
]

EVENT_ANALYSIS = {
    "title": "AI sector pullback",
    "fields": {
        "Involved areas": "AI / Semiconductors / US equities",
        "Updated at": "2026-06-03",
        "Event type": "Market volatility / Earnings expectations / Valuation discussion",
    },
    "overview": (
        "Recent AI-related stocks have pulled back. Market participants are not only asking whether the "
        "AI industry is still growing, but also whether current growth is enough to support existing valuations."
    ),
    "information_gaps": [
        {
            "view": "Some institutions view the decline as a short-term pullback because AI demand remains firm.",
            "source": "Example Source A / Financial media",
            "tag": "More constructive / Demand logic",
        },
        {
            "view": "Other comments argue that AI sector valuation has already reflected a large part of future growth.",
            "source": "Example Source B / Market commentary",
            "tag": "More cautious / Valuation logic",
        },
        {
            "view": "Industry observers note that changes in enterprise purchasing cycles may affect near-term earnings expectations.",
            "source": "Example Source C / Industry research",
            "tag": "Neutral / Fundamental logic",
        },
    ],
    "core_gap": (
        "The main information gap is not whether the AI industry is growing. It is whether current growth "
        "is strong enough to support valuations that already assume a favorable future."
    ),
    "data_explanation": [
        {
            "Metric": "Related technology index",
            "Current reading": "Down X% over the past week",
            "Position": "In a relatively large three-month pullback range",
            "Possible meaning": "Short-term sentiment has cooled, but this does not directly equal fundamental deterioration.",
        },
        {
            "Metric": "Representative company volatility",
            "Current reading": "Single-day decline of X%",
            "Position": "Among the larger one-day moves of the past year",
            "Possible meaning": "The market is sensitive to changes in near-term expectations.",
        },
        {
            "Metric": "Sector relative performance",
            "Current reading": "AI sector underperformed the broader market",
            "Position": "Weakness is concentrated in high-valuation growth areas",
            "Possible meaning": "The move is more sector-specific than a broad market decline.",
        },
    ],
    "major_changes": [
        {
            "change": "10-year US Treasury yield moved higher",
            "meaning": "The market may be repricing the future rate path.",
            "impact": ["Technology stocks", "Growth stocks", "Dollar assets", "Gold"],
        },
        {
            "change": "AI valuation debate became more explicit",
            "meaning": "Investors may separate demand strength from valuation tolerance more carefully.",
            "impact": ["High-growth equities", "Semiconductor suppliers", "Software infrastructure"],
        },
    ],
    "risk_watch": [
        "Whether follow-up earnings reports verify growth expectations.",
        "Whether rate expectations continue to change.",
        "Whether sector fund flows continue to weaken.",
        "Whether the market shows broader risk appetite decline.",
    ],
}

FINANCIAL_ANALYSIS = {
    "company": "Example Company quarterly report",
    "fields": {
        "Company": "Example Company",
        "Report period": "2026 Q2",
        "Published at": "2026-XX-XX",
        "Report type": "Quarterly report",
    },
    "core_data": [
        {"label": "Revenue", "value": "+X% YoY", "trend": "Growth slowed"},
        {"label": "Net income", "value": "+X% YoY", "trend": "Stable"},
        {"label": "Gross margin", "value": "X%", "trend": "Slight pressure"},
        {"label": "Cash flow", "value": "X", "trend": "Improved"},
    ],
    "trend_summary": (
        "Compared with the previous period, revenue continued to grow, but the growth pace slowed. "
        "Profit margin remained relatively stable, while R&D investment increased."
    ),
    "new_items": (
        "This period newly mentions overseas regulation, supply-chain costs, and demand changes as risk factors."
    ),
    "focus_items": [
        {
            "title": "Revenue growth slowed",
            "explanation": "The company is still growing, but the lower pace means future demand durability deserves attention.",
            "quote": "Example excerpt from the report...",
            "source": "Company report, page X",
        },
        {
            "title": "R&D spending increased",
            "explanation": "Higher R&D may indicate continued technical expansion, while also weighing on near-term profit.",
            "quote": "Example excerpt from the report...",
            "source": "Company report, page X",
        },
        {
            "title": "New risk disclosure appeared",
            "explanation": "New risk language often means the company is making some uncertainty more explicit.",
            "quote": "Example excerpt from the report...",
            "source": "Company report, page X",
        },
    ],
    "data_explanation": [
        {
            "Metric": "Gross margin",
            "Current value": "X%",
            "Compared with previous period": "Slightly lower",
            "Possible meaning": "Pricing or cost pressure may be present.",
            "Needs watching": "Whether margin pressure continues next period.",
        },
        {
            "Metric": "Cash flow",
            "Current value": "X",
            "Compared with previous period": "Improved",
            "Possible meaning": "Operating discipline may be improving.",
            "Needs watching": "Whether the improvement is recurring.",
        },
        {
            "Metric": "R&D spending",
            "Current value": "X",
            "Compared with previous period": "Higher",
            "Possible meaning": "The company is investing in future capability.",
            "Needs watching": "Whether spending converts into revenue quality.",
        },
    ],
    "risk_watch": [
        "Whether growth continues to slow.",
        "Whether gross margin remains under pressure.",
        "Whether cash flow stays stable.",
        "Whether management adjusts future guidance.",
        "Whether newly disclosed risks continue next period.",
    ],
}

NOTE_ATTITUDES = [
    "Constructive",
    "Not constructive",
    "Wait and see",
    "Questioning",
    "Continue watching",
    "Worth attention",
]

PROFILE_DATA = {
    "watchlist": ["AI", "Semiconductors", "Gold", "Nvidia", "Tesla", "Federal Reserve"],
    "notes": [
        {
            "target": "AI sector pullback",
            "source_page": "Event Analysis",
            "attitude": "Continue watching",
            "content": "Different sources read valuation and demand differently. Follow-up earnings need to verify growth expectations.",
            "created_at": "2026-06-03",
        },
        {
            "target": "Example Company quarterly report",
            "source_page": "Financial Analysis",
            "attitude": "Questioning",
            "content": "Revenue is still growing, but the slower pace and new risk disclosure should be read together.",
            "created_at": "2026-06-03",
        },
    ],
    "history": [
        "Viewed: AI sector pullback event analysis",
        "Searched: semiconductor valuation",
        "Viewed: Example Company quarterly report",
    ],
}

GUIDE_ITEMS = [
    "Choose interest tags, or skip and start from hot market entries.",
    "Search stocks, industries, news, financial reports, or market keywords.",
    "Use Event Analysis to compare information differences across sources.",
    "Use Financial Analysis to read key changes, data explanations, and risk observations.",
    "Use personal notes to record your own attitude, questions, and follow-up points.",
    "Manage watchlist items and notes in Profile.",
]

SETTINGS_OPTIONS = [
    {"label": "Default reading mode", "value": "Balanced"},
    {"label": "Source display", "value": "Show source beside each view"},
    {"label": "Risk language", "value": "Neutral"},
    {"label": "Data connection", "value": "Mock data only"},
]
