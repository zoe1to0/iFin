"""Mock Reports pipeline.

Pipeline:
User Input -> Prompt Builder -> Mock LLM Response -> Parser -> Structured Dict

This module does not call any real LLM API.
"""

import json

from parsers.report_parser import parse_report_response
from prompts.report_prompt import build_report_prompt


def _mock_report_llm_response(company: str, report_text: str, prompt: str) -> str:
    """Return a JSON string shaped like a future LLM response."""
    _ = prompt
    mock_response = {
        "what_happened": (
            f"{company} 的报告文本显示需要关注本期经营变化、利润质量、现金流和风险信号。"
            "当前为 mock pipeline，尚未接入真实财报解析。"
        ),
        "changes": [
            {
                "metric": "收入 / 利润 / 现金流",
                "direction": "evidence_insufficient",
                "explanation": "需要真实报告数据才能判断环比或同比变化。",
            }
        ],
        "expectation_check": [
            {
                "prior_expectation": "evidence_insufficient",
                "current_result": "evidence_insufficient",
                "status": "无法判断",
                "evidence": "mock pipeline 未读取真实上期展望。",
            }
        ],
        "risk_signals": [
            {
                "name": "证据不足风险",
                "level": "中",
                "signal": "尚未接入真实报告结构化数据。",
                "explanation": "如果缺少报告证据，不应编造经营变化或风险结论。",
            }
        ],
        "industry_position": [
            {
                "dimension": "行业位置",
                "company": company,
                "industry_reference": "evidence_insufficient",
                "explanation": "需要真实行业参考数据才能判断相对位置。",
            }
        ],
        "next_watch": [
            {
                "item": "下一期经营指标与管理层表述",
                "priority": "高",
                "why": "用于验证本期经营变化是否持续。",
            }
        ],
        "note": report_text[:160],
    }
    return json.dumps(mock_response, ensure_ascii=False)


def run_report_analysis(company: str, report_text: str) -> dict:
    """Run the mock Reports pipeline and return validated data."""
    prompt = build_report_prompt(company=company, report_text=report_text)
    raw_response = _mock_report_llm_response(
        company=company,
        report_text=report_text,
        prompt=prompt,
    )
    return parse_report_response(raw_response)
