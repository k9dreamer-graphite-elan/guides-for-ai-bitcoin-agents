---
name: Cross-Campaign Dreaming Report (template)
type: guide
handbook: v0.10
version: 1.0
updated: 2026-07-16
status: draft
---

# Cross-Campaign Dreaming Report — `<period>`

> Fill-in template for the fleet-level dreaming digest (see
> [Agent Dreaming & Memory Guide](./agent-dreaming-guide.md) Track C). Produced by a `DREAM` pass over
> many accepted Campaign Closeouts. **Read/report-only** — no on-chain writes. Publishing is
> outward-facing: needs a `publish-closeout` scope grant or explicit operator approval (`INV-1`).
> Cite the handbook by ID; carry every PnL figure with its confidence label (`INV-8`).

## Scope of this pass

| Field | Value |
|---|---|
| Period | `<YYYY-MM-DD → YYYY-MM-DD>` |
| Closeouts dreamed (source issues) | `<#…, #…>` |
| Agents / models covered | `<agent:<name>/<model-id>, …>` |
| Pools covered | `<dlmm_1, dlmm_3, …>` |
| KB state before → after | `<commit8> → <commit8 or PR #>` |
| Run by (attribution §F) | `planned_by / decided_by / executed_by / reviewed_by` |

## 1. Reconciliation across agents

Conflicting or overlapping findings, partitioned by `(watched principal, campaign id)`. The raw issue
wins on conflict.

| Claim | Agents/campaigns | Resolution | Evidence (issue URLs) |
|---|---|---|---|
| `<claim>` | `<agent · campaign-id>` | `merged \| superseded-by LSN-#### \| kept-both (per-sender)` | `<urls>` |

## 2. Fleet KPI roll-up

Per [`self-analysis-kpis`](../specs/self-analysis-kpis.md) §A–E. **Results (§E) reported last, never
led with.** §D is where model comparisons live.

| KPI | Section | This period | Prior | Δ |
|---|---|---|---|---|
| Recurrence rate (target 0) | A | | | |
| Tuition cost per failure class | A | | | |
| Incident → defense time | A | | | |
| Unattended hours between interventions | B | | | |
| Clean-exit rate | C | | | |
| Novel-situation first-contact success **by model** | D | | | |
| Net vs hold after gas (realized) | E | | | |

## 3. Memory deltas produced

What the dream changed in the KB. Supersede-not-delete; every delta traces to a source issue.

| Delta | Type | Pages touched | Source issue(s) |
|---|---|---|---|
| `<LSN-#### created / merged / superseded>` | `new \| merge \| supersede \| enrich` | `<pools/…, lessons/…>` | `<urls>` |

## 4. New cross-campaign insights (enrichment)

Patterns visible only across campaigns/agents/pools — none stated by a single closeout.

- **`<insight>`** — evidence across `<campaigns>`; proposed `LSN-####`; category `<INV-12 category>`.

## 5. Doctrine candidates (out of scope for the dream itself)

Lessons that look timeless enough to become rules. These are **handbook/runbook PRs**, not KB or dream
edits — listed here for a maintainer to decide.

- `<candidate>` → target: `<handbook §/INV or runbook>`.

## Confirmations

- [ ] No secrets; only on-chain-public or operator-approved data.
- [ ] Every PnL figure carries a confidence label; no display/DLP mark presented as realized (`INV-8`).
- [ ] Every memory delta traces to a source issue; `dream-log`/`log.md` row matches the page diff.
- [ ] Agents did not open the PR; a maintainer reviews and merges (`INV-1`).
