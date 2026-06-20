# Company Evidence Pool MVP Design

Status: Implemented with structural mock fixtures

## Purpose

The Company Evidence Pool is the provenance boundary between external company
sources and future Company Research Deck cards. It stores evidence records; it
does not analyze reports, call an LLM, or render UI.

## Evidence Contract

Each `Evidence` record contains:

- identity: `id`, `type`, `company_id`, `report_period`
- content: `title`, `quote`
- traceability: `page`, `source`, `url`, `published_at`
- evidence quality: `confidence`

Supported confidence labels follow the Company V2 contract:

- `primary`: official filing, exchange disclosure, company IR, or official data
- `secondary`: attributable reporting or sourced research
- `derived`: deterministic calculation tied to source evidence
- `unverified`: retained for structural review but invalid as factual evidence

The included NVDA and Tencent examples are mock fixtures. They are explicitly
marked `unverified`, identify their source as mock, and omit URLs, dates, and
pages. They must not support factual Company Deck claims.

## Pool Operations

`CompanyEvidencePool` supports:

- `add_evidence()`: validates company ownership, required identity fields, and
  unique evidence IDs
- `get_by_type()`: selects one evidence channel
- `get_by_period()`: selects one exact normalized report period
- `to_dict()`: exports a JSON-compatible Company V2 payload

An unsupported company produces an empty pool rather than invented evidence.

## Future Source Ingestion

### SEC

An SEC adapter will resolve ticker to CIK, retrieve filing metadata, and add
filing or financial-statement evidence. Each record should retain accession
number, filing URL, filing date, report period, source section, and an HTML
anchor when available. Page remains empty when an HTML filing has no stable
page reference.

### HKEX

An HKEX adapter will retrieve issuer announcements and annual/interim report
PDFs. Evidence records should preserve announcement URL, publication time,
report period, PDF page, and extracted quote. OCR-derived quotes must retain a
lower confidence until verified.

### Company IR

An IR adapter will ingest earnings releases, presentations, management
commentary, and segment disclosures. Official documents use `primary`
confidence only when the issuer and original URL are verified.

### News Pipeline

The existing News Pipeline can contribute `news` evidence after company-level
relevance filtering. Records should preserve publisher, headline, URL,
publication time, and a source excerpt. News remains distinct from company
statements and official filings.

## Evidence Rules

- IDs must be stable and unique within a company pool.
- A record cannot be added to a pool belonging to another company.
- Report periods use Company V2 period IDs, not display labels alone.
- Missing page, URL, or date remains empty and is never estimated.
- Mock or unverified evidence cannot be presented as fact.
- Future card interpretation may reference evidence IDs, but the Evidence Pool
  itself contains no investment advice or price prediction.
