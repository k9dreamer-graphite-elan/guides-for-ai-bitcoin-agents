# HODLMM Practice Guides

Cross-cutting **practice guides** — how to operate the HODLMM system well across campaigns, above the
level of any single runbook. Guides reference the [handbook](../handbook/HODLMM-Agent-Handbook.md) by
invariant ID and restate no constants; they hold no live state.

Where guides sit in the document model:

```
handbook (doctrine) → operating guide (field manual) → runbooks (procedures)
                    → knowledge base (distilled memory) → practice guides (cross-cutting how-to)
```

A **guide** differs from its neighbors: a *runbook* executes one operation; the *operating guide*
selects which runbook to run; a *practice guide* explains a cross-cutting capability that spans the
loop, the memory system, and the collaborative layer at once.

## Contents

| Guide | What it covers | Status |
|---|---|---|
| [Agent Dreaming & Memory Guide](./agent-dreaming-guide.md) | Out-of-band memory consolidation ("dreaming") to improve agent learning, context, multi-agent operation, and the memory system — with key takeaways and an implementation matrix. | draft |
| [Cross-Campaign Dreaming Report — template](./cross-campaign-dreaming-report-template.md) | Fill-in template for the fleet-level dreaming digest described in the guide (Track C). | template |
| [Cross-Campaign Dreaming Report — 2026-07-17](./cross-campaign-dreaming-report-2026-07-17.md) | First filled report: the 004/005 dual-closeout `DREAM` pass (the guide's first end-to-end exercise) — reconciliation, fleet KPI roll-up, memory deltas, doctrine candidates. | published |

## Conventions

- Filenames lowercase, hyphen-separated. Guides carry frontmatter (`type: guide`, `handbook:`,
  `version`, `updated`, `status`).
- **Cite, never restate** — invariants by ID (`INV-12`), runbooks by name.
- Timeless rules belong in the handbook (a handbook PR); pool-specific facts belong in the
  [Knowledge Base](../knowledge/README.md). A guide explains *practice*, not doctrine or live state.
