# iFin Product Log

This document records current product decisions and implementation status.

Status language:

- **Implemented**: available in the current application or pipeline.
- **Designed**: architecture is finalized, but implementation is pending.
- **Future Vision**: directional planning only, outside the current MVP.

## Product Log - 2026-06-20

### Event V2 Research Deck

**Status: Implemented / stabilized**

Event V2 has stabilized around the Research Deck model. The product organizes
market research as equal questions rather than a report that users must read in
sequence.

Current core chain:

```text
Search
  -> Router
  -> Source Plan
  -> Evidence Pool
  -> LLM Analysis
  -> Card Adapter
  -> Research Deck
  -> Notes
```

Event V2 contains ten Research Question Cards:

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

The cards are equal. Their numbering is documentation reference only and does
not define a required reading order or completion path.

### Retrieval & Evidence Upgrade

**Status: Implemented**

This iteration added or stabilized:

- Router refactor and standardized topic classification
- Topic-aware source plans
- Multi-source retrieval
- Strict relevance filtering
- Evidence Pool normalization
- `evidence_status` for explicit evidence boundaries
- Query variants that improve recall without weakening relevance requirements
- Rule-backed Historical Pattern and Watch Metrics cards

Under strict evidence filtering, QA coverage improved from **4/12 to 9/12**.
Queries without acceptable evidence continue to return an insufficient state
instead of being filled with unrelated material.

Core principle:

> 宁可证据不足，也不使用错误证据。

## Company V2 — Company Research Workspace

**Status: Designed, not implemented**

The existing Report Page will not continue as a financial-report summary page.
Its planned successor is Company V2, the company-oriented counterpart to Event
V2.

Company V2 helps users understand the current state of a company. It does not
provide direct investment advice, price predictions, target prices, or trading
signals.

Planned page structure:

```text
Search
  -> Company Market Layer
  -> Company Research Deck
  -> Notes
```

### Company Market Layer

Planned market context includes:

- K-line / price history
- Open / high / low / average price
- PE / market capitalization / turnover rate
- Trading volume / trading value
- Fund flow

If a stable source is unavailable, the product must show `暂未接入`. It must
not estimate, fabricate, or silently replace the value with demo data.

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

Interpretation boundaries:

- `相比上一期变化` is a longitudinal comparison of the company.
- `哪些业务驱动变化` explains internal business and segment drivers.
- `行业位置与竞争环境` is a horizontal industry comparison.
- Industry position must not use an unsupported composite ranking.
- Use `行业内主要参与者 / 相关公司`, not `竞品 / 竞争主体`.
- Prefer facts, data, and context over unsupported labels such as `头部`,
  `领先`, or `第二梯队`.

## Future Vision — Judgment & Sentiment Layer

**Status: Future Vision, not part of the current MVP**

iFin is currently designed as a calm, evidence-based market understanding
tool. A longer-term product loop may include a Judgment & Sentiment Layer.

Users may record a personal judgment or emotional response on an Event or
Company page. The final taxonomy has not been designed and should remain within
four or five choices. Early examples include, but are not limited to:

- 看好
- 谨慎
- 观望
- 期待
- 担忧

These examples are not final product categories.

The intended mechanism is that users must express their own view before seeing
the distribution of other users' views for the same event, sector, or company.

Design goals:

- Form an independent judgment first
- Observe market sentiment second
- Reduce anchoring by group sentiment
- Turn isolated notes into a long-term judgment system
- Create a future entry point for community retention

Long-term loop:

```text
Research -> Judgment -> Reflection -> Community
```

Sentiment is not a trading signal. Sentiment is one part of understanding the
market.
