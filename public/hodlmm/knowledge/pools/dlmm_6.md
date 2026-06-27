---
type: kb-pool
pool: dlmm_6
pair: STX/sBTC
handbook: v0.6
version: 0.1
updated: 2026-06-26
last_ingested: 2026-06-26
status: active
sources:
  - https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/4
  - https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/5
---

# Pool playbook — dlmm_6 (STX/sBTC)

> Distilled from accepted Campaign Closeout issues — **raw source = the issues** (see `sources`). Cites
> the handbook by ID; restates no constants. PnL framed as the issues framed it (net-vs-hold after gas;
> display marks context-only — INV-8). No live state cached here.

## Status & liveness

**active.** The `HODLMM-DLMM6-20260602-001` campaign ([#4](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/4))
ran ~20 days and reached a clean, fully-realized exit (wallet DLP `0`, proven on-chain); the pool was
not flagged stale. No exit-only/`INV-9` stale status recorded for dlmm_6.

## What worked

| Tactic | Evidence | Confidence |
|---|---|---|
| Bounded capital envelope + standing operator authorization as the autonomy contract (manage inside the envelope; re-approve to add funds / change pool / go public) | [#4](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/4) | realized |
| Withdraw → swap → redeposit as a first-class recenter route when a native move shape is illegal | [#4](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/4), [#5](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/5) | realized |
| Upward / non-overlapping same-pool native moves (succeeded where downward one-sided shapes failed) | [#4](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/4) | realized |
| "Sit and wait" out-of-range with zero gas while repair design was genuinely uncertain — fees resumed when the bin naturally returned to range | [#4](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/4) | realized |
| Per-recovery-cycle gas cap (raised at the mid-campaign renewal) kept one bad loop from draining the envelope | [#4](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/4), [#5](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/5) | realized |
| Clean exit to DLP `0`, proven by wallet state + chain tx result | [#4](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/4) | realized |

## What failed

| Failure | Why | Evidence | Confidence |
|---|---|---|---|
| Downward one-sided same-pool native moves aborted with `(err u5001)` | Move legality is a source/target **geometry** proof, not an intent proof; downward shifts on a fully one-sided position are an illegal shape | [#4](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/4), [#5](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/5) | realized |
| First multi-bin deposit took two `abort_by_post_condition` attempts before success | Exact NFT postconditions are brittle for first-time multi-bin deposits | [#4](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/4) | realized |
| Agent blocked its own planned-end exit (state was `planned_end`, not `active`) | No exit-only terminal state permitting final withdrawal from non-active states | [#4](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/4), [#5](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/5) | realized |
| Bitflow status/position endpoints showed stale TVL after the confirmed exit | Protocol status reads lag; they are advisory, not closure proof | [#4](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/4) | realized |

## Effective recenter targeting

- Before a same-pool native move, **prove source/target bin non-overlap and a legal direction** for the
  position's current one-sidedness. Overlap, or a downward shift on a fully one-sided position → route
  to withdraw/swap/redeposit; never blind-retry a `(err u5001)` shape. (See the recenter runbook; cite
  `INV-3` and handbook `§4.2` for width-vs-IL.) → [LSN-0001](../lessons/lessons-catalog.md#lsn-0001)
- The specific field bin geometries in [#4](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/4)
  /[#5](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/5) are reviewer
  context, **not** durable targeting constants — don't hardcode them; compute against live state.

## Known API / tx-pattern gotchas

- `(err u5001)` on downward one-sided native moves → [LSN-0001](../lessons/lessons-catalog.md#lsn-0001)
- Status/position endpoints lag after exit → [LSN-0002](../lessons/lessons-catalog.md#lsn-0002)
- First multi-bin deposit postcondition aborts → [LSN-0003](../lessons/lessons-catalog.md#lsn-0003)

## PnL (honest framing — INV-8)

- **Headline: net −$1.25 vs holding the original tokens, after gas** (confidence: realized-withdrawal).
  Roughly flat — STX/USD fell over the window, creating one-sided IL drag on the STX leg that fee
  capture roughly offset; gas was small.
- BFF 30-day **display** earnings (~$27) are **context only — NOT realized fee income** (INV-8).
- Source framing: [#4 PnL section](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/4).

## Open questions / contradictions

- **"Sit and wait" bounds.** [#5](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/5)
  proposes recording an out-of-range hold as `pause_with_blocker` with an explicit watch condition
  rather than ordinary `hold`; the exact time/conditions bound is not yet settled. → [LSN-0005](../lessons/lessons-catalog.md#lsn-0005)

## Provenance

Ingested [#4](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/4) +
[#5](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/5) on 2026-06-26
(v1 seed). Full trail in [`../log.md`](../log.md).
