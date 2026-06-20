# iFin Product Architecture

## Status Boundary

- **Event V2**: implemented and stabilized in the current MVP pipeline.
- **Company V2**: designed, not implemented.
- **Judgment & Sentiment Layer**: future vision only.

This separation is intentional. Architecture documentation must not imply that
designed or future capabilities are already available.

## Core Architecture

```text
Search
  |
  v
Router
  |
  v
Source Plan
  |
  v
Evidence Pool
  |
  v
LLM Reasoning
  |
  v
Research Deck
  |
  v
Notes
```

Layer responsibilities:

| Layer | Responsibility |
| --- | --- |
| Search | Capture a company, ticker, event, asset, sector, or market question |
| Router | Normalize intent and select the correct topic or company package |
| Source Plan | Decide which official, market, news, and report sources to attempt |
| Evidence Pool | Normalize evidence, provenance, freshness, URLs, and evidence status |
| LLM Reasoning | Organize evidence and explain relationships without inventing facts |
| Research Deck | Redistribute reasoning into equal, non-linear research questions |
| Notes | Preserve the user's own interpretation, questions, and observations |

## Event

Core question:

> 发生了什么？

Event supports market events, macro indicators, assets, companies, and broad
themes. Its Router and Source Plan determine which evidence is relevant before
LLM reasoning begins.

The Event Research Deck uses ten equal questions:

1. 市场发生了什么
2. 为什么会这样
3. 谁在行动
4. 市场如何反应
5. 支持这个观点的依据
6. 为什么需要谨慎
7. 过去发生过什么
8. 最大风险在哪里
9. 哪些数据值得关注
10. 后续应该关注什么

Historical Pattern and Watch Metrics currently use deterministic rule
libraries. News-dependent cards use the Evidence Pool. Unsupported topics or
missing sources return explicit empty or insufficient states.

## Company

Core question:

> 这家公司现在处于什么状态？

**Company V2 is designed but not implemented.** It will replace the current
Report Page rather than extend the existing report-summary architecture.

Planned architecture:

```text
Company / Ticker Search
  -> Company Router
  -> Company Source Plan
  -> Market Data + Official Filings + Company IR + News
  -> Company Evidence Pool
  -> Company LLM Reasoning
  -> Company Card Adapter
  -> Company Market Layer + Company Research Deck
  -> Notes
```

### Company Market Layer

- K-line / price history
- Open / high / low / average price
- PE / market capitalization / turnover rate
- Trading volume / trading value
- Fund flow

Only sourced market values may be displayed. Missing fields must show
`暂未接入`; they must not be estimated from unrelated data.

### Company Research Deck

1. 公司当前状态
2. 本期财报说了什么
3. 相比上一期变化
4. 哪些业务驱动变化
5. 上期展望兑现了吗
6. 市场怎么看
7. 问题与风险
8. 行业位置与竞争环境
9. 公司发展进程
10. 未来关注什么

Company comparisons follow three distinct lenses:

| Lens | Meaning |
| --- | --- |
| Longitudinal | Compare the company with its own previous period |
| Internal | Explain which segments or business drivers caused the change |
| Horizontal | Compare the company with relevant industry participants using consistent evidence |

Industry context should use `行业内主要参与者 / 相关公司`. It should not use
unsupported composite rankings or unverified labels such as `头部`, `领先`, or
`第二梯队`.

## Shared Product Principles

- Do not provide investment advice.
- Do not predict price direction or returns.
- Do not make decisions for the user.
- Help users understand facts, evidence, market reactions, uncertainty, and
  the basis for their own judgment.
- When evidence is unavailable, explicitly return an insufficient state.
- Do not use Mock data, generic knowledge, or model assumptions as if they were
  current verified evidence.
- Evidence and AI interpretation must remain distinguishable.
- Every externally verifiable claim should retain its source context.

## Future Vision: Judgment & Sentiment Layer

**Not part of the current MVP.**

The future layer may let users record a judgment or emotional response after
research. A user must express a personal view before seeing aggregated views
from other users for the same event, sector, or company.

Possible examples include `看好`, `谨慎`, `观望`, `期待`, and `担忧`, but the
final taxonomy has not been designed.

```text
Research -> Judgment -> Reflection -> Community
```

The purpose is to protect independent thinking, support later reflection, and
create a path toward community without treating sentiment as a trading signal.
