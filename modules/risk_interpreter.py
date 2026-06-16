def interpret_risk(text):
    text_lower = text.lower()

    high_risk_words = ["risk", "decline", "loss", "volatility", "lawsuit", "debt", "default"]
    medium_risk_words = ["competition", "pressure", "uncertainty", "concern", "slowdown"]
    low_risk_words = ["growth", "profit", "strong", "demand", "optimism"]

    high_count = sum(word in text_lower for word in high_risk_words)
    medium_count = sum(word in text_lower for word in medium_risk_words)
    low_count = sum(word in text_lower for word in low_risk_words)

    if high_count >= 2:
        risk_level = "中~高风险"
        explanation = "文本中出现多个高风险信号，可能反映市场不确定性、财务压力或负面事件。"
    elif high_count == 1 or medium_count >= 2:
        risk_level = "中风险"
        explanation = "文本中存在一定风险提示，投资者可能需要关注竞争、波动或未来不确定性。"
    elif low_count >= 1:
        risk_level = "低~中风险"
        explanation = "文本中包含增长、需求或盈利相关的积极信号，但仍需结合市场环境判断。"
    else:
        risk_level = "中风险"
        explanation = "文本未显示明显极端风险信号，因此暂时判断为中性风险。"

    return {
    "risk_level": risk_level,
    "risk_text": explanation
}