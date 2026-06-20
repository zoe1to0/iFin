# Company Router MVP Design

Status: Implemented as a local deterministic resolver

The Company Router normalizes a supported company name or ticker into a stable
Company V2 identity. It does not call Yahoo Finance, SEC, HKEX, or any other
network service.

## Resolution Contract

`resolve_company(query)` returns a `CompanyResolution` value containing:

- `resolved`
- `company_id`
- `display_name`
- `legal_name`
- `ticker`
- `market`
- `exchange`
- `confidence`
- `candidates`

Unknown inputs return `resolved=false`, empty normalized fields, confidence
`0.0`, and an empty candidate list. The MVP does not use fuzzy matching.

## company_id Rule

`company_id` is an internal stable identifier using:

```text
{MARKET}_{CANONICAL_LOCAL_TICKER}
```

Examples:

- `US_NVDA`
- `US_GOOGL`
- `HK_0700`
- `HK_9988`

The identifier does not use the display name, so a future company rename does
not require changing stored Company V2 records.

## ticker Rule

- US tickers use uppercase exchange symbols, for example `NVDA` and `AAPL`.
- Hong Kong tickers use a four-digit local code plus `.HK`, for example
  `0700.HK` and `9988.HK`.
- Alternate listed symbols may resolve to one canonical Company V2 identity.
  `GOOG` and `GOOGL` currently resolve to `US_GOOGL`, whose canonical ticker is
  `GOOGL`.
- Ticker aliases are matched case-insensitively after whitespace cleanup.

## market Rule

The MVP uses short market codes:

- `US`: United States listed companies
- `HK`: Hong Kong listed companies

The exchange is stored separately:

- `NASDAQ` for the supported US companies
- `HKEX` for the supported Hong Kong companies

Future A-share support should use market `CN` and preserve the specific
exchange, such as `SSE` or `SZSE`.

## Confidence Rule

- `1.0`: exact canonical ticker match
- `0.98`: exact configured alias match, including company names and alternate
  tickers
- `0.0`: unresolved input

Confidence reflects deterministic alias quality only. It is not a market-data
or company-evidence confidence score.
