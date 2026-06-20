# Company Card Adapter MVP Design

Status: Implemented as a rule-based evidence adapter

## Purpose

The Company Card Adapter converts Company V2 inputs into a stable ten-card
Research Deck contract. It does not retrieve data, call an LLM, render UI, or
invent missing analysis.

## Card Contract

Every card contains `id`, `title`, `card_summary`, `key_points`,
`expanded_sections`, `evidence_ids`, `report_period`, `confidence`, and
`empty_state`.

All ten cards are always returned. A card without the evidence needed to
answer its research question uses `empty_state=true`, an empty summary, and no
evidence IDs.

## Evidence Routing

| Card | MVP evidence requirement |
|---|---|
| 公司当前状态 | filing, financial statement, company IR, or market-data evidence |
| 本期财报说了什么 | filing or financial statement |
| 相比上一期变化 | filing/statement evidence from at least two report periods |
| 哪些业务驱动变化 | company IR or financial statement |
| 上期展望兑现了吗 | sourced guidance/outlook evidence from at least two periods |
| 市场怎么看 | news or market-data evidence |
| 问题与风险 | evidence explicitly containing a risk or uncertainty signal |
| 行业位置与竞争环境 | industry-data evidence |
| 公司发展进程 | company announcement or official-regulator evidence |
| 未来关注什么 | sourced guidance, outlook, calendar, or scheduled disclosure |

Evidence may support more than one research question when its type and content
meet each card's rule. The adapter does not copy arbitrary evidence merely to
avoid an empty card.

## Market Snapshot Boundary

`market_snapshot` is accepted by `build_company_card_pool()` because it is part
of the frozen Company V2 input contract. Market values are not rendered into a
factual card until the snapshot has a corresponding `market_data` Evidence
record and evidence ID. This prevents an untraceable provider value from being
presented as sourced card analysis.

## Mock Evidence

Cards linked to the current mock fixtures use:

- `confidence="unverified"`
- `card_summary="示例证据，仅用于结构验证。"`
- mock evidence IDs and source previews

They are structural fixtures, not company analysis. Missing mock coverage
remains an empty card.

## Safety Rules

- A non-empty factual card must have at least one evidence ID.
- Evidence IDs must come from the supplied Evidence Pool.
- The adapter only summarizes evidence availability and exposes source
  previews; it does not infer financial conclusions.
- It does not generate buy, sell, or hold recommendations.
- It does not predict price direction or returns.
- Industry language uses `行业内主要参与者` or `相关公司`. It does not generate
  unsupported labels such as `头部`, `领先`, or `第二梯队`.
- Missing comparative periods, guidance, risk evidence, or industry data stay
  empty instead of being filled by generic knowledge.
