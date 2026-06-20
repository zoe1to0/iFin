# iFin

## Vision

AI organizes evidence.

Users form judgments.

iFin preserves thinking.

## What iFin Is

iFin is not a market prediction tool.

It is a market understanding and thinking companion. The system helps users:

- Understand what is happening
- Explore evidence
- Understand why it matters
- Preserve their own market thinking

iFin does not provide buy, sell, hold, target-price, or position advice.

## Core Architecture

```text
Living Market Layer
        |
        v
Evidence Explorer
        |
        v
Understanding
        |
        v
(Optional) Judgment
        |
        v
(Optional) Archive
        |
        v
(Optional) Reflection
```

Evidence Explorer is the primary product experience. The Living Market Layer
provides current context, while Judgment, Archive, and Reflection remain
optional.

## V2 Direction

Current V2 focus:

- Living Market Layer
- Evidence Explorer
- Non-linear Exploration
- Archive Refactor
- Reflection System

The redesign does not reduce financial content. It removes forced reading
order and redistributes financial reasoning across explorable evidence cards.

## Documentation

- [Product Log](docs/product_log.md)
- [Product Architecture](docs/product_architecture.md)
- [V2 Architecture Blueprint](docs/architecture/v2-blueprint.md)
- [V2 Product Refactor Log](docs/product_logs/2026-06-19-v2-product-refactor.md)

## Current Status

- Home V2: implemented
- Event V2: stabilized
- Company V2: design finalized, not implemented
- Guide V2: implemented
- Profile V1: implemented
- Settings: pending

Current MVP focuses on evidence-based market and company understanding, not
price prediction or investment advice.

## Local Run

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```
