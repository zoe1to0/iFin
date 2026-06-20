"""Rule-based Company Research Deck adapter.

Maps collected evidence into ten stable cards without retrieval, LLM calls,
or unsupported company conclusions.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass, field
from typing import Any, Callable

try:
    from services.company_evidence import (
        CompanyEvidencePool,
        Evidence,
        create_mock_company_evidence,
    )
except ModuleNotFoundError:  # Support direct local execution from services/.
    from company_evidence import CompanyEvidencePool, Evidence, create_mock_company_evidence


@dataclass(frozen=True)
class CompanyCard:
    """One stable Company Research Deck card."""

    id: str
    title: str
    card_summary: str = ""
    key_points: list[str] = field(default_factory=list)
    expanded_sections: list[dict[str, Any]] = field(default_factory=list)
    evidence_ids: list[str] = field(default_factory=list)
    report_period: str = ""
    confidence: str = "insufficient"
    empty_state: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _contains_terms(record: Evidence, terms: tuple[str, ...]) -> bool:
    text = f"{record.title} {record.quote}".casefold()
    return any(term.casefold() in text for term in terms)


def _types(records: list[Evidence], allowed: set[str]) -> list[Evidence]:
    return [item for item in records if item.type.casefold() in allowed]


def _current_state(records: list[Evidence]) -> list[Evidence]:
    return _types(records, {"filing", "financial_statement", "company_ir", "market_data"})


def _report_facts(records: list[Evidence]) -> list[Evidence]:
    return _types(records, {"filing", "financial_statement"})


def _period_comparison(records: list[Evidence]) -> list[Evidence]:
    candidates = _report_facts(records)
    periods = {item.report_period for item in candidates if item.report_period}
    return candidates if len(periods) >= 2 else []


def _business_drivers(records: list[Evidence]) -> list[Evidence]:
    return _types(records, {"company_ir", "financial_statement"})


def _guidance_check(records: list[Evidence]) -> list[Evidence]:
    terms = ("guidance", "outlook", "指引", "展望")
    candidates = [item for item in records if _contains_terms(item, terms)]
    periods = {item.report_period for item in candidates if item.report_period}
    return candidates if len(periods) >= 2 else []


def _market_view(records: list[Evidence]) -> list[Evidence]:
    return _types(records, {"news", "market_data"})


def _risks(records: list[Evidence]) -> list[Evidence]:
    terms = ("risk", "uncertainty", "风险", "不确定")
    return [item for item in records if _contains_terms(item, terms)]


def _industry_position(records: list[Evidence]) -> list[Evidence]:
    return _types(records, {"industry_data"})


def _company_progress(records: list[Evidence]) -> list[Evidence]:
    return _types(records, {"company_announcement", "official_regulator"})


def _future_watch(records: list[Evidence]) -> list[Evidence]:
    terms = ("guidance", "outlook", "calendar", "scheduled", "指引", "展望", "日期")
    return [item for item in records if _contains_terms(item, terms)]


CARD_DEFINITIONS: tuple[dict[str, Any], ...] = (
    {"id": "current_state", "title": "公司当前状态", "selector": _current_state},
    {"id": "current_report", "title": "本期财报说了什么", "selector": _report_facts},
    {"id": "period_change", "title": "相比上一期变化", "selector": _period_comparison},
    {"id": "business_drivers", "title": "哪些业务驱动变化", "selector": _business_drivers},
    {"id": "guidance_check", "title": "上期展望兑现了吗", "selector": _guidance_check},
    {"id": "market_view", "title": "市场怎么看", "selector": _market_view},
    {"id": "risks", "title": "问题与风险", "selector": _risks},
    {"id": "industry_position", "title": "行业位置与竞争环境", "selector": _industry_position},
    {"id": "company_progress", "title": "公司发展进程", "selector": _company_progress},
    {"id": "future_watch", "title": "未来关注什么", "selector": _future_watch},
)


def _normalize_pool(
    pool: CompanyEvidencePool | Mapping[str, Any] | Sequence[Any],
) -> list[Evidence]:
    if isinstance(pool, CompanyEvidencePool):
        raw_records: Sequence[Any] = pool.evidence
    elif isinstance(pool, Mapping):
        raw_records = pool.get("evidence", []) or []
    elif isinstance(pool, Sequence) and not isinstance(pool, (str, bytes)):
        raw_records = pool
    else:
        raw_records = []

    records: list[Evidence] = []
    seen_ids: set[str] = set()
    for item in raw_records:
        if isinstance(item, Evidence):
            record = item
        elif isinstance(item, Mapping):
            record = Evidence.from_mapping(item)
        else:
            continue
        if record.id and record.id not in seen_ids:
            seen_ids.add(record.id)
            records.append(record)
    return records


def _report_period(value: Any, records: list[Evidence]) -> str:
    if isinstance(value, Mapping):
        explicit = str(value.get("period_id") or value.get("report_period") or "").strip()
    else:
        explicit = str(value or "").strip()
    if explicit:
        return explicit
    periods = [item.report_period for item in records if item.report_period]
    return Counter(periods).most_common(1)[0][0] if periods else ""


def _confidence(records: list[Evidence]) -> str:
    if not records:
        return "insufficient"
    labels = {item.confidence.casefold() for item in records}
    for label in ("unverified", "secondary", "derived"):
        if label in labels:
            return label
    return "primary"


def _sections(records: list[Evidence]) -> list[dict[str, Any]]:
    return [
        {
            "evidence_id": item.id,
            "title": item.title,
            "quote": item.quote,
            "source": item.source,
            "page": item.page,
            "url": item.url,
            "published_at": item.published_at,
        }
        for item in records
    ]


def _build_card(
    definition: Mapping[str, Any],
    records: list[Evidence],
    report_period: str,
    display_name: str,
) -> CompanyCard:
    selector: Callable[[list[Evidence]], list[Evidence]] = definition["selector"]
    selected = selector(records)
    if not selected:
        return CompanyCard(
            id=str(definition["id"]),
            title=str(definition["title"]),
            report_period=report_period,
        )

    if any(item.confidence.casefold() == "unverified" for item in selected):
        summary = "示例证据，仅用于结构验证。"
    else:
        subject = display_name or "该公司"
        summary = f"{subject} 已关联 {len(selected)} 条可追溯证据，供该研究问题展开使用。"

    return CompanyCard(
        id=str(definition["id"]),
        title=str(definition["title"]),
        card_summary=summary,
        key_points=[item.title for item in selected[:3] if item.title],
        expanded_sections=_sections(selected),
        evidence_ids=[item.id for item in selected],
        report_period=report_period,
        confidence=_confidence(selected),
        empty_state=False,
    )


def build_company_card_pool(
    company_profile: Mapping[str, Any] | None,
    market_snapshot: Mapping[str, Any] | None,
    evidence_pool: CompanyEvidencePool | Mapping[str, Any] | Sequence[Any],
    report_period: Any = None,
) -> list[dict[str, Any]]:
    """Build all ten cards while preserving evidence and empty-state rules."""
    del market_snapshot  # Values require market_data evidence IDs before card use.
    records = _normalize_pool(evidence_pool)
    period = _report_period(report_period, records)
    display_name = str((company_profile or {}).get("display_name", "")).strip()
    return [
        _build_card(definition, records, period, display_name).to_dict()
        for definition in CARD_DEFINITIONS
    ]


if __name__ == "__main__":
    import json

    fixtures = [
        ("US_NVDA", {"company_id": "US_NVDA", "display_name": "NVIDIA"}),
        ("HK_0700", {"company_id": "HK_0700", "display_name": "腾讯"}),
    ]
    for company_id, profile in fixtures:
        cards = build_company_card_pool(
            profile,
            {},
            create_mock_company_evidence(company_id),
        )
        output = {
            "company_id": company_id,
            "card_count": len(cards),
            "empty_cards": sum(card["empty_state"] for card in cards),
            "evidence_linked_cards": sum(bool(card["evidence_ids"]) for card in cards),
            "cards": [
                {
                    "title": card["title"],
                    "empty_state": card["empty_state"],
                    "evidence_ids": card["evidence_ids"],
                }
                for card in cards
            ],
        }
        print(f"\n=== {company_id} ===")
        print(json.dumps(output, ensure_ascii=False, indent=2))
