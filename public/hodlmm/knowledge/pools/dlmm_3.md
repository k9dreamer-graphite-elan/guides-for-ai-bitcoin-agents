---
type: kb-pool
pool: dlmm_3
pair: STX/USDCx
handbook: v0.9
version: 0.1
updated: 2026-07-02
last_ingested: 2026-07-02
status: active
sources:
  - https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/21
  - https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/22
  - https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/11
  - https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/12
  - https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/13
---

# Pool playbook — dlmm_3 (STX/USDCx)

> Distilled from accepted Campaign Closeout issues — **raw source = the issues** (see `sources`). Cites
> the handbook by ID; restates no constants. PnL framed as the issues framed it (net-vs-hold after gas;
> display marks context-only — INV-8). No live state cached here.

## Status & liveness

**active.** Two independent campaigns ran this pool over overlapping June 2026 windows and both reached
a chain-proven clean exit (wallet DLP `0`, zero user bins):

- K9Dreamer `HODLMM-DLMM3-20260625-002` ([#21](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/21)) —
  7 days, fully realized net-positive exit at the planned end (after one recovered automation incident).
- Hex Stallion `7D-LP-Campaign-2026-06` ([#11](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/11)) —
  7 days autonomous; ended `closeout_unresolved` (out-of-range LP, blocked actuator), then repaired and
  exited clean two days later. No stale / exit-only (`INV-9`) status recorded for dlmm_3.

## What worked

| Tactic | Evidence | Confidence |
|---|---|---|
| **Boundary-state entry shape**: when the active bin is pinned at the pool floor, the standard two-sided `-N..+N` geometry is invalid — a one-sided ladder *including the active bin* is the legal entry | [#21](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/21) | realized |
| Bounded sit-and-wait through full out-and-back excursions: a boundary ladder monetized two round trips with **zero recenter gas** (volatility capture, bounded by the planned end) | [#21](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/21) | realized |
| Withdraw minimums derived from **direct on-chain reads** (never 0/0) — eliminated the `(err u5001)` failure class entirely | [#21](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/21), [#22](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/22) | realized |
| Supervised validation round-trip (withdraw + redeposit matching the read-only plan to the µSTX) before trusting automation | [#21](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/21) | realized |
| Halt-after-1-fail guardrail: both automation incidents froze the system safely with nothing broadcast and the position intact | [#21](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/21) | realized |
| Staged withdraw → add repair restored strict range coverage (once) | [#11](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/11) | realized |

## What failed

| Failure | Why | Evidence | Confidence |
|---|---|---|---|
| Auto-exit died **pre-broadcast** in cron: signing CLI not on cron's minimal `PATH`; the signing branch had never executed under cron before the exit tick | Cron env ≠ interactive env; "validated live" ≠ validated in the execution environment | [#21](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/21), [#22](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/22) | realized |
| Silent stderr (`2>/dev/null` on signer calls) masked an automation root cause for days | Halted automation with no diagnosable cause burns range time | [#21](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/21) | realized |
| Narrow band drifted out of strict range quickly; confirmed repair txs did **not** produce durable range recovery | Tx confirmation ≠ restored earning range — post-confirm proof is the gate | [#11](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/11), [#12](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/12) | realized |
| Actuator chain broke between intent and execution: plan-builder failure, incomplete user-bin proof, signer gates | Correct `rebalance`/`exit` intent alone repairs nothing → [LSN-0011](../lessons/lessons-catalog.md#lsn-0011) | [#12](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/12) | realized |
| Contribution package posted while the position was still out of range with no completed exit | Docs-complete ≠ operationally closed → [LSN-0012](../lessons/lessons-catalog.md#lsn-0012) | [#11](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/11), [#13](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/13) | realized |
| sBTC→STX top-up quotes overstated executable fill (tail-filled third chunk) | Bounded-route quotes are not fill guarantees; size LP adds from mined output only | [#21](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/21) | realized |

## Effective recenter targeting

- **Check for boundary state first.** If the active bin sits at the pool floor, do not force the
  standard two-sided design — enter (or re-enter) as a one-sided ladder that includes the active bin.
  The specific bin numbers in the issues are reviewer context, **not** durable constants; compute
  against live state (`INV-3`, handbook §4.2).
- **Boundary ladder + patience beat reactive recentering** on this pool: both campaigns' best outcomes
  came from *not* spending recenter gas while price excursions ran their course. This is the bounded
  `pause_with_blocker` sit-and-wait of [LSN-0005](../lessons/lessons-catalog.md#lsn-0005) — bounded by
  the planned end, never an unbounded ordinary `hold`.
- **Repair completion = post-confirm strict range proof**, not a confirmed tx
  ([LSN-0011](../lessons/lessons-catalog.md#lsn-0011)); staged withdraw/add is a continuation state
  machine, not a fresh strategy prompt each cycle ([LSN-0006](../lessons/lessons-catalog.md#lsn-0006)).

## Known API / tx-pattern gotchas

- `(err u5001)` class avoided entirely via direct-read nonzero withdraw minimums → [LSN-0001](../lessons/lessons-catalog.md#lsn-0001)
- Status/position endpoints lag after exit; closure proof = wallet DLP zero + chain-confirmed tx → [LSN-0002](../lessons/lessons-catalog.md#lsn-0002)
- Fresh-but-incomplete monitors must not erase the last complete range proof → [LSN-0008](../lessons/lessons-catalog.md#lsn-0008)

## PnL (honest framing — INV-8)

- **K9Dreamer 002: net `+37.89 STX` ≈ `+$6.31` vs holding the original tokens, after gas**
  (confidence: realized; ≈ +13% on deployed capital in 7 days). Explicitly labeled **volatility
  capture, not yield**: the edge came from two complete out-of-range round trips through a one-sided
  ladder; a one-way price move would have read materially negative vs hold. Never project this shape
  as an APR. ([#21 PnL section](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/21))
- **Hex Stallion 7D: roughly flat (≈ `+$0.34` after gas) at LOW confidence** — hold baseline and
  IL-only attribution were not reconstructable; reported by component with confidence labels rather
  than a rounded headline. ([#11 closeout comments](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/11))
- Protocol/DLP display earnings: **context only, never realized** on both campaigns.

## Open questions / contradictions

- **Does boundary-ladder capture generalize off-floor?** The net-positive result depended on the pool
  being in (and returning to) a boundary state. Behavior with a mid-range active bin is undocumented
  for this pool.
- **Staged-continuation SLA bounds** ([LSN-0006](../lessons/lessons-catalog.md#lsn-0006)): how long
  stale staged state may block before mandatory archive/supersede is still unsettled.

## Provenance

Ingested [#21](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/21) +
[#22](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/22) (K9Dreamer 002)
and [#11](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/11)–[#13](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/13)
(Hex Stallion 7D) on 2026-07-02. Full trail in [`../log.md`](../log.md).
