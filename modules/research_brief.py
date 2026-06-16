def generate_brief(text):
    text_lower = text.lower()

    if "risk" in text_lower or "decline" in text_lower or "loss" in text_lower or "volatility" in text_lower:
        risk_signal = "中~高风险"
    elif "growth" in text_lower or "profit" in text_lower or "strong" in text_lower:
        risk_signal = "低~中风险"
    else:
        risk_signal = "中风险"

    summary = text[:180]

    if "nvidia" in text_lower or "ai chip" in text_lower or "semiconductor" in text_lower:
        market_insight = "AI demand may support optimism in the semiconductor sector, while competition and valuation pressure should still be watched."
    elif "tesla" in text_lower or "ev" in text_lower or "electric vehicle" in text_lower:
        market_insight = "The key issue is whether growth expectations can offset EV competition, pricing pressure, and profitability concerns."
    elif "bank" in text_lower or "credit" in text_lower or "loan" in text_lower:
        market_insight = "This information may affect market views on credit risk, liquidity conditions, and financial stability."
    elif "inflation" in text_lower or "interest rate" in text_lower or "fed" in text_lower:
        market_insight = "Macro uncertainty may influence investor expectations around interest rates, risk appetite, and asset valuation."
    else:
        market_insight = "This news may influence investor sentiment, market expectations, and future confidence around the company or sector."

    brief = f"""
### 新闻摘要
{summary}...

### 市场洞察
{market_insight}

### 风险信号
{risk_signal}

### iFin观点

iFin 希望帮助用户以更平静、更有秩序的方式理解金融信息，而不是被市场情绪牵引。
"""

    return brief