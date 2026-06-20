# Company Service Orchestrator MVP Design

Status: Implemented with mock evidence and no UI integration

## Purpose

`run_company_analysis(query)` is the first complete Company V2 application
boundary. It composes existing services without adding report interpretation,
LLM reasoning, real filing retrieval, or UI behavior.

## Pipeline

```text
User query
  -> Company Router
  -> Company Profile
  -> Company Market Layer
  -> Company Evidence Pool (mock fixture only)
  -> Company Card Adapter
  -> CompanyAnalysisResult
```

Each stage retains its own availability state. A market-data failure does not
erase evidence or cards, and missing evidence does not produce fabricated card
content.

## Return Contract

The service returns:

- `company_profile`: identity fields supplied by the local router
- `market_snapshot`: defensive Yahoo-backed snapshot or unavailable state
- `evidence_pool`: a flat list of evidence records
- `company_card_pool`: ten rule-based cards for resolved companies
- `metadata`: resolution, source mode, availability, and warnings

For an unresolved query, all content pools are empty and
`metadata.resolved=false`. The service does not attempt fuzzy guessing.

## Metadata

The MVP metadata contains:

- `resolved`
- `company_id`
- `data_mode="mock_evidence_mvp"`
- `evidence_status`
- `market_data_status`
- `warnings`

Evidence status is `unverified` when all records are mock fixtures,
`insufficient` when no fixture exists, and `partial` only when verified and
unverified records are mixed. Market status is passed through from the Company
Market Layer.

## Company Profile Boundary

The profile currently contains only Router-backed identity fields. Sector,
industry, business segments, and related companies remain empty because no
real company-profile source is connected. The orchestrator does not infer
them.

## Evidence and Card Rules

- NVDA and Tencent use the existing structural mock evidence fixtures.
- Mock evidence remains `confidence="unverified"` in the returned pool.
- Cards derived from mock evidence retain unverified confidence and explicitly
  identify themselves as structural examples.
- Resolved companies without fixtures receive ten empty cards.
- Unresolved queries receive an empty card pool.
- Market values do not enter factual cards without market-data evidence IDs.

## Safety Boundary

The orchestrator does not:

- present mock evidence as a real filing or news source
- generate buy, sell, or hold recommendations
- predict prices or returns
- estimate unavailable market or company fields
- call an LLM
- retrieve SEC, HKEX, company IR, or other filing sources
- modify the legacy Report page or service
