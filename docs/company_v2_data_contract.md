# Company V2 Data Contract

Status: Designed, not implemented

This document defines the future data boundary for Company V2. It does not
change the current Report Page, connect a data provider, or enable an LLM.

## 1. Core Return Structure

The future orchestration entry point is expected to follow this conceptual
signature:

```text
run_company_analysis(query, period_mode) -> CompanyAnalysisResult
```

`query` may be a company name, legal name, ticker, or supported market symbol.
`period_mode` describes the requested reporting scope, such as latest report,
specific period, or latest-versus-prior comparison.

```json
{
  "company_profile": {},
  "report_period": {},
  "market_snapshot": {},
  "evidence_pool": [],
  "company_card_pool": [],
  "metadata": {}
}
```

Recommended metadata fields:

```json
{
  "schema_version": "company_v2.v1",
  "query": "",
  "period_mode": "latest",
  "generated_at": "",
  "source_plan": [],
  "attempted_sources": [],
  "successful_sources": [],
  "failed_sources": [],
  "evidence_status": "sufficient | partial | insufficient",
  "warnings": []
}
```

## 2. Company Profile Schema

```json
{
  "company_id": "US_NVDA",
  "display_name": "NVIDIA",
  "legal_name": "NVIDIA Corporation",
  "ticker": "NVDA",
  "exchange": "NASDAQ",
  "market": "US",
  "currency": "USD",
  "sector": "Technology",
  "industry": "Semiconductors",
  "business_segments": [
    {
      "segment_id": "data_center",
      "name": "Data Center",
      "description": ""
    }
  ],
  "related_companies": [
    {
      "company_id": "US_AMD",
      "display_name": "AMD",
      "ticker": "AMD",
      "relationship": "行业内主要参与者"
    }
  ]
}
```

Field rules:

- `company_id` is the stable internal identity and must not depend only on the
  display name.
- `ticker` and `exchange` must be stored together because the same ticker text
  may exist in different markets.
- `business_segments` are company-reported or source-backed operating
  segments. They must not be invented from a generic industry taxonomy.
- Use `行业内主要参与者` or `相关公司` for `relationship`. Do not use `竞品`
  or `竞争主体` as the default product language.
- `related_companies` does not imply a ranking, direct substitutability, or a
  complete competitive set.

## 3. Report Period Schema

```json
{
  "period_id": "US_NVDA_FY2026_Q1",
  "period_label": "FY2026 Q1",
  "period_type": "quarterly",
  "fiscal_year": 2026,
  "fiscal_quarter": 1,
  "report_date": "2025-05-28",
  "source_url": "",
  "is_latest": true,
  "comparison_period_id": "US_NVDA_FY2025_Q1"
}
```

Allowed `period_type` examples:

- `quarterly`
- `semi_annual`
- `annual`
- `trailing_twelve_months`
- `interim`

Period rules:

- Fiscal years and calendar years are not interchangeable.
- Companies may end fiscal years in different calendar months.
- `fiscal_year` and `fiscal_quarter` must follow the company's own reporting
  calendar.
- `report_date` is the publication or filing date, not the period end date.
- `comparison_period_id` should normally point to the same fiscal period in the
  previous year for year-over-year analysis. Sequential comparison may use the
  immediately preceding fiscal period when explicitly requested.
- A future implementation should add `period_start` and `period_end` if the
  source provides reliable values.

## 4. Market Snapshot Schema

```json
{
  "price": null,
  "open": null,
  "high": null,
  "low": null,
  "average_price": null,
  "volume": null,
  "turnover": null,
  "market_cap": null,
  "pe_ratio": null,
  "pe_industry_avg": null,
  "money_flow": null,
  "updated_at": "",
  "data_status": "unavailable"
}
```

Recommended value representation for sourced fields:

```json
{
  "value": null,
  "unit": "",
  "currency": "",
  "source": "",
  "as_of": ""
}
```

Allowed `data_status` values:

- `available`: sourced and current enough for display
- `partial`: only some fields are sourced
- `stale`: sourced, but outside the accepted freshness window
- `unavailable`: no stable source is connected

Rules:

- Missing values remain `null` or empty and display as `暂未接入`.
- Do not estimate PE, turnover, money flow, industry averages, or current price.
- `updated_at` must come from the source observation time or latest data point.
- `pe_industry_avg` requires a documented peer universe and calculation method.
- `money_flow` must identify the market-specific definition and source.

## 5. Evidence Schema

```json
{
  "id": "filing_US_NVDA_FY2026_Q1_001",
  "type": "filing",
  "company_id": "US_NVDA",
  "report_period": "US_NVDA_FY2026_Q1",
  "title": "",
  "quote": "",
  "page": "",
  "source": "",
  "url": "",
  "published_at": "",
  "confidence": "primary"
}
```

Recommended evidence types:

- `filing`
- `financial_statement`
- `company_ir`
- `earnings_call`
- `company_announcement`
- `market_data`
- `official_regulator`
- `news`
- `industry_data`

Allowed confidence values:

- `primary`: official filing, exchange disclosure, company IR, or official data
- `secondary`: reputable reporting or sourced industry research
- `derived`: deterministic calculation based on referenced primary evidence
- `unverified`: retained for review but not valid as factual card evidence

## 6. Company Card Schema

```json
{
  "id": "current_state",
  "title": "公司当前状态",
  "card_summary": "",
  "key_points": [],
  "expanded_sections": [],
  "evidence_ids": [],
  "report_period": "US_NVDA_FY2026_Q1",
  "confidence": "insufficient",
  "empty_state": {
    "is_empty": true,
    "message": "当前缺少可验证证据。"
  }
}
```

Card rules:

- `evidence_ids` must resolve to records in the top-level `evidence_pool`.
- Card confidence is derived from evidence coverage, not model confidence.
- `empty_state.is_empty` is true when the card cannot answer its target
  question with the available evidence.
- A card remains present when empty so that the ten-card contract is stable.
- `expanded_sections` may contain card-specific structured fields, but each
  section must retain relevant evidence IDs when it contains factual claims.

## 7. Company Research Deck Contract

### 1. 公司当前状态

- **Target question:** What is the company's current operating and market
  state?
- **Required data:** latest filing, latest company announcement, basic market
  snapshot, current report period.
- **Optional data:** money flow, valuation context, recent operational update.
- **Empty state:** no current filing, announcement, or sourced market context.
- **Rule generation:** source freshness summary and deterministic metric labels.
- **LLM:** useful for connecting operating and market context; not required to
  display sourced facts.

### 2. 本期财报说了什么

- **Target question:** What are the central facts and management statements in
  the selected report?
- **Required data:** selected official filing or report text.
- **Optional data:** earnings presentation and call transcript.
- **Empty state:** selected report is unavailable or cannot be parsed.
- **Rule generation:** statement-table extraction and top-line financial
  changes when structured values are available.
- **LLM:** recommended for concise explanation and grouping, strictly grounded
  in filing evidence.

### 3. 相比上一期变化

- **Target question:** What changed relative to the valid comparison period?
- **Required data:** current and comparison-period financial statements with
  aligned accounting fields.
- **Optional data:** management explanation of each change.
- **Empty state:** comparison period is missing or accounting fields cannot be
  aligned.
- **Rule generation:** numeric deltas, percentages, direction, and period
  labels.
- **LLM:** optional for explaining sourced changes; must not calculate values.

### 4. 哪些业务驱动变化

- **Target question:** Which internal businesses or segments caused the
  company-level change?
- **Required data:** segment revenue, segment profit where available, MD&A, and
  operational metrics.
- **Optional data:** product, geography, customer, or channel breakdowns.
- **Empty state:** no sourced segment or management discussion evidence.
- **Rule generation:** segment contribution calculations when comparable data
  exists.
- **LLM:** recommended for connecting segment evidence to company outcomes.

### 5. 上期展望兑现了吗

- **Target question:** Did prior management guidance match the current result?
- **Required data:** prior-period guidance quote and current-period result.
- **Optional data:** earnings call transcript and updated guidance.
- **Empty state:** either the original guidance or comparable outcome is
  missing.
- **Rule generation:** range-versus-result comparison for explicit numeric
  guidance.
- **LLM:** useful for interpreting qualitative guidance, with both periods
  cited.

### 6. 市场怎么看

- **Target question:** How did observable market behavior respond?
- **Required data:** timestamped price, volume, and market reaction window.
- **Optional data:** sourced news, analyst commentary, and fund flow.
- **Empty state:** no reliable reaction window or market data.
- **Rule generation:** price and volume changes around the report date.
- **LLM:** optional for explaining disagreement; must not equate commentary
  with market consensus.

### 7. 问题与风险

- **Target question:** Which current issues and risks are supported by company
  evidence?
- **Required data:** filing risk disclosures, cash-flow and balance-sheet
  signals, or explicit operational issues.
- **Optional data:** regulatory announcements and relevant news.
- **Empty state:** no current, traceable risk evidence.
- **Rule generation:** threshold-based financial warnings when formulas and
  source data are documented.
- **LLM:** recommended for organizing risk paths and uncertainty, not assigning
  unsupported probabilities.

### 8. 行业位置与竞争环境

- **Target question:** How does the company compare with relevant industry
  participants under consistent definitions?
- **Required data:** documented peer set and comparable metrics for the same
  period.
- **Optional data:** industry reports and market-share disclosures.
- **Empty state:** peer universe, period, or metric definition is inconsistent.
- **Rule generation:** comparable metric tables and deltas.
- **LLM:** optional for contextual explanation. It must not create a composite
  ranking or unsupported labels such as `头部`, `领先`, or `第二梯队`.

### 9. 公司发展进程

- **Target question:** Which sourced milestones explain the company's current
  stage?
- **Required data:** official filings, announcements, product launches,
  acquisitions, and management changes.
- **Optional data:** selected historical reports and industry context.
- **Empty state:** no verified timeline records.
- **Rule generation:** chronological timeline construction and deduplication.
- **LLM:** optional for explaining why a milestone is relevant today.

### 10. 未来关注什么

- **Target question:** Which future disclosures, metrics, and company events can
  validate the current understanding?
- **Required data:** management guidance, reporting calendar, and unresolved
  evidence gaps.
- **Optional data:** product schedules, regulatory calendars, and industry
  metrics.
- **Empty state:** no sourced guidance, schedule, or evidence gap can be named.
- **Rule generation:** known dates, recurring disclosures, and missing-data
  checklist.
- **LLM:** useful for connecting each watch item to a specific research
  question; it must not predict outcomes.

## 8. Evidence Rules

1. A conclusion without an `evidence_id` must not be presented as fact.
2. Financial data, company statements, market reactions, news, and derived
   calculations must retain distinct source types.
3. LLM-generated explanation is allowed, but factual claims must remain
   traceable to the Evidence Pool.
4. Derived values must reference their source evidence and documented formula.
5. `unverified` evidence cannot support a factual card summary.
6. Missing evidence must produce an explicit empty or insufficient state.
7. Mock values and generic model knowledge must not impersonate current company
   evidence.
8. Do not output buy, sell, or hold recommendations.
9. Do not provide target prices, position sizing, timing instructions, or
   valuation conclusions presented as advice.
10. Do not predict price direction or investment returns.

## 9. Future Extensions

The following items are outside the initial data-contract implementation:

- SEC filing ingestion and XBRL normalization
- HKEX announcements and report ingestion
- Company IR report and announcement adapters
- Earnings Call Transcript ingestion
- Automatic selection of relevant industry participants
- Multi-year financial statement and segment trends
- Cross-market accounting and currency normalization
- Versioned Evidence Pool and report revisions
- Deterministic peer metrics with documented universes
- Judgment & Sentiment Layer

The Judgment & Sentiment Layer remains a future product direction. Sentiment is
part of market understanding, not a trading signal.
