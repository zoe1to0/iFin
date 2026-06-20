"""Company Evidence Pool MVP.

This module defines the evidence boundary for future Company V2 research. The
included fixtures are structural mock records only and are never valid factual
evidence.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import asdict, dataclass, field
from typing import Any

try:
    from services.company_router import CompanyResolution, resolve_company
except ModuleNotFoundError:  # Support direct local execution from services/.
    from company_router import CompanyResolution, resolve_company


@dataclass(frozen=True)
class Evidence:
    """A traceable evidence record for future Company V2 cards."""

    id: str
    type: str
    company_id: str
    report_period: str = ""
    title: str = ""
    quote: str = ""
    page: str = ""
    source: str = ""
    url: str = ""
    published_at: str = ""
    confidence: str = "unverified"

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> "Evidence":
        """Create an evidence record from a schema-compatible mapping."""
        return cls(
            id=str(data.get("id", "")).strip(),
            type=str(data.get("type", "")).strip(),
            company_id=str(data.get("company_id", "")).strip(),
            report_period=str(data.get("report_period", "")).strip(),
            title=str(data.get("title", "")).strip(),
            quote=str(data.get("quote", "")).strip(),
            page=str(data.get("page", "")).strip(),
            source=str(data.get("source", "")).strip(),
            url=str(data.get("url", "")).strip(),
            published_at=str(data.get("published_at", "")).strip(),
            confidence=str(data.get("confidence", "unverified")).strip()
            or "unverified",
        )

    def to_dict(self) -> dict[str, str]:
        """Return a JSON-serializable evidence record."""
        return asdict(self)


@dataclass
class CompanyEvidencePool:
    """In-memory collection of evidence belonging to one company."""

    company_id: str
    evidence: list[Evidence] = field(default_factory=list)

    def add_evidence(self, item: Evidence | Mapping[str, Any]) -> Evidence:
        """Validate and append one evidence record."""
        record = item if isinstance(item, Evidence) else Evidence.from_mapping(item)
        if not record.id:
            raise ValueError("Evidence id is required.")
        if not record.type:
            raise ValueError("Evidence type is required.")
        if not record.company_id:
            raise ValueError("Evidence company_id is required.")
        if self.company_id and record.company_id != self.company_id:
            raise ValueError("Evidence company_id does not match this pool.")
        if any(existing.id == record.id for existing in self.evidence):
            raise ValueError(f"Duplicate evidence id: {record.id}")
        self.evidence.append(record)
        return record

    def get_by_type(self, evidence_type: str) -> list[Evidence]:
        """Return records matching an evidence type, case-insensitively."""
        normalized = str(evidence_type or "").strip().casefold()
        return [item for item in self.evidence if item.type.casefold() == normalized]

    def get_by_period(self, report_period: str) -> list[Evidence]:
        """Return records associated with an exact report-period identifier."""
        normalized = str(report_period or "").strip().casefold()
        return [
            item
            for item in self.evidence
            if item.report_period.casefold() == normalized
        ]

    def to_dict(self) -> dict[str, object]:
        """Return the pool in the future Company V2 payload shape."""
        return {
            "company_id": self.company_id,
            "evidence": [item.to_dict() for item in self.evidence],
        }


def _resolve_fixture_company(
    company: CompanyResolution | Mapping[str, Any] | str,
) -> str:
    if isinstance(company, CompanyResolution):
        return company.company_id if company.resolved else ""
    if isinstance(company, Mapping):
        if not company.get("resolved", True):
            return ""
        return str(company.get("company_id", "")).strip()

    raw_value = str(company or "").strip()
    if raw_value in {"US_NVDA", "HK_0700"}:
        return raw_value
    resolution = resolve_company(raw_value)
    return resolution.company_id if resolution.resolved else ""


def _mock_record(
    *,
    evidence_id: str,
    evidence_type: str,
    company_id: str,
    report_period: str,
    title: str,
    quote: str,
) -> Evidence:
    return Evidence(
        id=evidence_id,
        type=evidence_type,
        company_id=company_id,
        report_period=report_period,
        title=f"[Mock fixture] {title}",
        quote=f"[Mock fixture] {quote}",
        source="Mock fixture - not a real source",
        confidence="unverified",
    )


def create_mock_company_evidence(
    company: CompanyResolution | Mapping[str, Any] | str,
) -> CompanyEvidencePool:
    """Create structural evidence fixtures for NVDA or Tencent.

    Unsupported companies return an empty pool. Fixture records deliberately
    omit URLs, dates, and pages so they cannot resemble retrieved evidence.
    """
    company_id = _resolve_fixture_company(company)
    pool = CompanyEvidencePool(company_id=company_id)

    if company_id == "US_NVDA":
        period = "US_NVDA_FY2026_Q1"
        records = [
            _mock_record(
                evidence_id="mock_nvda_filing_001",
                evidence_type="filing",
                company_id=company_id,
                report_period=period,
                title="NVIDIA quarterly report evidence",
                quote="Placeholder for a passage extracted from an official filing.",
            ),
            _mock_record(
                evidence_id="mock_nvda_ir_001",
                evidence_type="company_ir",
                company_id=company_id,
                report_period=period,
                title="NVIDIA management commentary evidence",
                quote="Placeholder for sourced management commentary tied to the report period.",
            ),
            _mock_record(
                evidence_id="mock_nvda_news_001",
                evidence_type="news",
                company_id=company_id,
                report_period=period,
                title="NVIDIA report-related news evidence",
                quote="Placeholder for a relevant news summary with publisher attribution.",
            ),
        ]
    elif company_id == "HK_0700":
        period = "HK_0700_FY2025_ANNUAL"
        records = [
            _mock_record(
                evidence_id="mock_tencent_filing_001",
                evidence_type="filing",
                company_id=company_id,
                report_period=period,
                title="Tencent annual report evidence",
                quote="Placeholder for a passage extracted from an official annual report.",
            ),
            _mock_record(
                evidence_id="mock_tencent_ir_001",
                evidence_type="company_ir",
                company_id=company_id,
                report_period=period,
                title="Tencent business disclosure evidence",
                quote="Placeholder for a sourced business-segment disclosure.",
            ),
            _mock_record(
                evidence_id="mock_tencent_news_001",
                evidence_type="news",
                company_id=company_id,
                report_period=period,
                title="Tencent report-related news evidence",
                quote="Placeholder for a relevant news summary with publisher attribution.",
            ),
        ]
    else:
        records = []

    for record in records:
        pool.add_evidence(record)
    return pool


if __name__ == "__main__":
    import json

    for sample in ["NVDA", "腾讯"]:
        sample_pool = create_mock_company_evidence(sample)
        result = {
            "company_id": sample_pool.company_id,
            "evidence_count": len(sample_pool.evidence),
            "types": sorted({item.type for item in sample_pool.evidence}),
            "periods": sorted(
                {item.report_period for item in sample_pool.evidence if item.report_period}
            ),
        }
        print(f"\n=== {sample} ===")
        print(json.dumps(result, ensure_ascii=False, indent=2))
