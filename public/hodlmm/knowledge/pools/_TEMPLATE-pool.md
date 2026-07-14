---
type: kb-pool
pool: <pool-id>            # e.g. dlmm_6
pair: <BASE/QUOTE>         # e.g. STX/sBTC
handbook: v0.10
version: 0.1
updated: <YYYY-MM-DD>
last_ingested: <YYYY-MM-DD>
status: active            # active | stale | deprecated   (stale = exit-only per INV-9)
sources:                  # raw-source closeout issue URLs
  - <issue URL>
---

# Pool playbook — <pool-id> (<BASE/QUOTE>)

> Distilled from accepted Campaign Closeout issues — **raw source = the issues** (see `sources`). Cites
> the handbook by ID; restates no constants. PnL framed as the issues framed it (net-vs-hold after gas;
> display marks context-only — INV-8). No live state cached here.

## Status & liveness

`active` | `stale (exit-only, INV-9)` — and the closeout that established it. One line.

## What worked

| Tactic | Evidence | Confidence |
|---|---|---|
| <tactic, in your own words> | [#N](url) | realized \| reported \| low |

## What failed

| Failure | Why | Evidence | Confidence |
|---|---|---|---|
| <failure> | <root cause, not just symptom> | [#N](url) | realized \| reported \| low |

## Effective recenter targeting

Heuristics only — cite `INV-3` / handbook `§4.2` and the recenter runbook. **Never** hardcode bin
indices, widths, or step counts here (those are live/handbook values). Field tx geometries from a
closeout are reviewer context, not durable targeting constants.

## Known API / tx-pattern gotchas

Short list, each cross-linked to a `LSN-` entry in
[`../lessons/lessons-catalog.md`](../lessons/lessons-catalog.md).

## PnL (honest framing — INV-8)

Headline net-vs-hold after gas + confidence label. Display/DLP marks labeled context-only, never
realized. No fabricated basis.

## Open questions / contradictions

Conflicting claims awaiting a tie-breaker closeout, or bounds still undefined.

## Provenance

Ingested closeouts + dates. Full trail in [`../log.md`](../log.md).
