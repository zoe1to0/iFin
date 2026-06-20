# Company Market Layer MVP Design

Status: Implemented as a defensive market snapshot adapter

## Purpose

The Company Market Layer provides a compact current-market context for a
company resolved by the local Company Router. It does not analyze financial
reports, generate Company Deck content, or provide investment advice.

## Input

`get_company_market_snapshot(company_resolution, market="")` accepts:

- a `CompanyResolution`
- a mapping containing `company_id`, `ticker`, and `market`
- a Company Router alias or supported raw ticker

The optional `market` argument supports explicit ticker/market input. The MVP
only fetches configured US and Hong Kong tickers. A-share input returns an
unavailable snapshot.

## Output

The normalized snapshot contains:

- company identity: `company_id`, `ticker`, `market`, `currency`
- sourced market values: `price`, `open`, `high`, `low`, `volume`,
  `market_cap`, `pe_ratio`
- provenance and availability: `updated_at`, `data_status`, `source`,
  `missing_fields`

`data_status` means:

- `available`: all seven MVP market fields are present
- `partial`: at least one field is present, but one or more are missing
- `unavailable`: no MVP market value could be retrieved

## Data Source

The MVP uses the existing `YahooFinanceService.get_stock_snapshot()` as its
safe baseline. A small local yfinance adapter adds the latest daily open, high,
low, observation time, and source-provided trailing PE.

Yahoo Finance is a convenient experimental aggregation source, not an official
exchange feed. Provider failures, rate limits, delayed fields, and incomplete
fundamentals are expected and are represented through `partial` or
`unavailable` status.

## PE Interpretation

`pe_ratio` is the provider-supplied trailing PE when available. The Market
Layer does not recalculate PE, harmonize accounting definitions across
markets, or treat PE values as directly comparable between exchanges.

## Missing-Data Rules

- Missing values remain `null`.
- No market value is estimated or filled with mock data.
- Provider failures do not propagate exceptions into the application.
- `updated_at` comes from the latest returned market observation; the service
  does not insert the current date when no observation exists.
- `source` is empty when all market fields are unavailable.

## Explicitly Outside MVP

The service does not provide or estimate:

- average price
- industry-average PE
- money flow
- turnover rate
- turnover value

These fields require stable sources and documented market-specific
definitions before they can enter the Company V2 contract.
