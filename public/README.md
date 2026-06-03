# Guides for AI Bitcoin Agents

Field guides, handbooks, and **executable runbooks** for autonomous agents operating DeFi in the
Bitcoin / Stacks economy. Organized by protocol — **HODLMM (Bitflow) first**, more to follow.

This is a **community resource**, not official protocol documentation. It is vendor-neutral and
covers **public contracts and APIs** only. Not financial advice; mainnet, real funds at risk — verify
everything on-chain.

## The three document types

This repo follows one model so agents and operators always know what they're reading:

| Layer | Answers | Changes | Rule |
|---|---|---|---|
| **Handbook** (doctrine) | "What's true, and what must I never violate?" | rarely (versioned) | the source of truth; everything else cites it |
| **Operating guide** (field manual) | "How do I work day-to-day, and *which* runbook do I run when?" | occasionally | references the handbook; doesn't duplicate it |
| **Runbook** (procedure) | "Exact steps to do *this one* operation safely" | per-procedure | executable; **imports** the handbook's invariants; one operation per file |

**Discipline:** operating guides and runbooks **import** the handbook — they cite invariants by ID
(e.g. `INV-3`) and never restate its constants. Each runbook declares the handbook version it conforms
to. When the handbook changes a constant, everything downstream inherits it.

## Map

```
public/
├── hodlmm/                  # Bitflow HODLMM (DLMM concentrated liquidity)
│   ├── handbook/            # doctrine — the canonical reference
│   ├── operating-guide/     # daily practice + strategy selection
│   └── runbooks/            # executable procedures (one op each)
└── shared/                  # cross-protocol runbooks (span >1 protocol)
```

- **[HODLMM →](./hodlmm/README.md)**
- **[Shared / cross-protocol →](./shared/README.md)**

## Using this repo

New here? Read the protocol **handbook Chapter 0** first (the safety floor), then the **operating
guide**, then pick the **runbook** for the operation you're performing.

## License

Documentation is licensed under **CC BY 4.0**. See each section's `LICENSE`.
