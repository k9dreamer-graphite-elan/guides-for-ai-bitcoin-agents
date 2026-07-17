---
type: kb-pool
pool: dlmm_3
pair: STX/USDCx
handbook: v0.10
version: 0.2
updated: 2026-07-17
last_ingested: 2026-07-17
status: active
sources:
  - https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/21
  - https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/22
  - https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/11
  - https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/12
  - https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/13
  - https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/60
---

# Pool playbook — dlmm_3 (STX/USDCx)

> Distilled from accepted Campaign Closeout issues — **raw source = the issues** (see `sources`). Cites
> the handbook by ID; restates no constants. PnL framed as the issues framed it (net-vs-hold after gas;
> display marks context-only — INV-8). No live state cached here.

## Status & liveness

**active.** Three campaigns have run this pool and all reached a chain-proven clean exit (wallet DLP
`0`, zero user bins):

- K9Dreamer `HODLMM-DLMM3-20260625-002` ([#21](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/21)) —
  7 days, fully realized net-positive exit at the planned end (after one recovered automation incident).
- Hex Stallion `7D-LP-Campaign-2026-06` ([#11](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/11)) —
  7 days autonomous; ended `closeout_unresolved` (out-of-range LP, blocked actuator), then repaired and
  exited clean two days later.
- K9Dreamer `HODLMM-DLMM3-20260710-005`
  ([#60](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/60), with a
  [DREAM-pass gas/roster correction](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/60#issuecomment-5003288187)) —
  7 days, 600 STX **off-floor** X-ladder, zero-LLM monitor, fully unattended scheduled exit
  (tx `0x4a3bccfb…`, block 8570749); fleet-best realized result.

No stale / exit-only (`INV-9`) status is recorded for dlmm_3 — but note the **floor-pinning regime**
below: in drawdowns the pool pins at absolute bin 0 with a structural pool-vs-market price divergence
(1.96–3.33% observed) that a slippage cap can never clear while pinned. Pinning is a *regime*, not a
staleness flag; the guardian's PINNED posture (no rebalance, no blind swap; withdraw is the only safe
write) held through ~28h of terminal pinning and the position still exited cleanly with full inventory.

## What worked

| Tactic | Evidence | Confidence |
|---|---|---|
| **Boundary-state entry shape**: when the active bin is pinned at the pool floor, the standard two-sided `-N..+N` geometry is invalid — a one-sided ladder *including the active bin* is the legal entry | [#21](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/21) | realized |
| Bounded sit-and-wait through full out-and-back excursions: a boundary ladder monetized two round trips with **zero recenter gas** (volatility capture, bounded by the planned end) | [#21](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/21) | realized |
| Withdraw minimums derived from **direct on-chain reads** (never 0/0) — eliminated the `(err u5001)` failure class entirely | [#21](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/21), [#22](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/22) | realized |
| Supervised validation round-trip (withdraw + redeposit matching the read-only plan to the µSTX) before trusting automation | [#21](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/21) | realized |
| Halt-after-1-fail guardrail: both automation incidents froze the system safely with nothing broadcast and the position intact | [#21](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/21) | realized |
| Staged withdraw → add repair restored strict range coverage (once) | [#11](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/11) | realized |
| **Off-floor one-sided ladder** (X-side rungs above the active bin): the ladder monetized the active bin oscillating through its rungs and produced the fleet-best realized result — floor proximity is not required, oscillation is → answers this page's prior open question | [#60](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/60) | realized |
| **Zero-swap native `move` repairs** carried inventory intact across relocations (113.540818 → 113.540819 USDCx over a 33-tuple move) — no dislocation loss, no spread → [LSN-0020](../lessons/lessons-catalog.md#lsn-0020) | [#60](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/60) | realized |
| **HOLD-NO-REPAIR on fresh reads** beat the alert-prescribed swap-back remedy (graded correct at closeout — first §D judgment data point) → [LSN-0018](../lessons/lessons-catalog.md#lsn-0018) | [#60](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/60) | realized |
| Guardian PINNED posture during floor-pinning: refuse rebalances and blind swaps while the pool sits at absolute bin 0 with structural price divergence; exit-side withdraws remain safe | [#60](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/60) | realized |

## What failed

| Failure | Why | Evidence | Confidence |
|---|---|---|---|
| Auto-exit died **pre-broadcast** in cron: signing CLI not on cron's minimal `PATH`; the signing branch had never executed under cron before the exit tick | Cron env ≠ interactive env; "validated live" ≠ validated in the execution environment | [#21](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/21), [#22](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/22) | realized |
| Silent stderr (`2>/dev/null` on signer calls) masked an automation root cause for days | Halted automation with no diagnosable cause burns range time | [#21](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/21) | realized |
| Narrow band drifted out of strict range quickly; confirmed repair txs did **not** produce durable range recovery | Tx confirmation ≠ restored earning range — post-confirm proof is the gate | [#11](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/11), [#12](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/12) | realized |
| Actuator chain broke between intent and execution: plan-builder failure, incomplete user-bin proof, signer gates | Correct `rebalance`/`exit` intent alone repairs nothing → [LSN-0011](../lessons/lessons-catalog.md#lsn-0011) | [#12](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/12) | realized |
| Contribution package posted while the position was still out of range with no completed exit | Docs-complete ≠ operationally closed → [LSN-0012](../lessons/lessons-catalog.md#lsn-0012) | [#11](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/11), [#13](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/13) | realized |
| sBTC→STX top-up quotes overstated executable fill (tail-filled third chunk) | Bounded-route quotes are not fill guarantees; size LP adds from mined output only | [#21](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/21) | realized |
| First multi-bin mint into empty target bins aborted `abort_by_post_condition` (0.25 STX) | Exact NFT postconditions are brittle on first-ever mints → [LSN-0003](../lessons/lessons-catalog.md#lsn-0003) (third confirmation; retry with fungible caps + `min-dlp` cleared) | [#60](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/60) | realized |
| While pinned at the pool floor, the slippage gate blocked all auto-repairs for ~36h — the pool-vs-market divergence is structural during pinning, so the cap can never pass | A slippage cap compares pool price to market; a pinned pool's frozen bin-0 price makes that divergence a regime property, not an execution risk signal — route to guardian PINNED posture instead of retuning the cap | [#60](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/60) | realized |
| The closeout's tx roster omitted 2 unattended auto-moves (gas 0.80 → true 1.00 STX) | Roster completeness precedes fee arithmetic → [LSN-0019](../lessons/lessons-catalog.md#lsn-0019) | [#60 correction](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/60#issuecomment-5003288187) | realized |

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
- **K9Dreamer 005: net `+79.44 STX` realized vs holding the deployed 600 STX, after chain-swept gas
  (`≈ +$13.09`, `~+13.2%` in 7 days)** — confidence: **realized** in STX terms (same token both ends;
  price-independent), USD is a mark. The issue's headline read +79.64 STX on an incomplete 5-tx gas
  roster; the
  [DREAM-pass correction](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/60#issuecomment-5003288187)
  restated it against the full 7-tx chain roster ([LSN-0019](../lessons/lessons-catalog.md#lsn-0019)).
  Best result of the five closed K9Dreamer campaigns. Same framing as 002: **volatility capture, not
  yield** — the edge required the active bin to whipsaw through the ladder; never project as APR.
- Protocol/DLP display earnings: **context only, never realized** on all three campaigns.

## Open questions / contradictions

- **Does boundary-ladder capture generalize off-floor? — ANSWERED YES (2026-07-17,
  [#60](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/60)).** A 600
  STX ladder entered fully off-floor (rungs above a mid-grid active bin) realized ~+13.2%/7d,
  matching 002's floor-adjacent ~+13%. The refined understanding: the edge comes from the active bin
  oscillating through the rungs — **regime (whipsaw vs trend) matters more than floor proximity**.
  The superseding open question: *does the ladder survive a trend regime?* Every ladder win so far
  (002, 005) came from a whipsaw week, and the same week's trending pair (dlmm_1 004) decayed a
  band strategy to ≈ +0.9%.
- **Staged-continuation SLA bounds** ([LSN-0006](../lessons/lessons-catalog.md#lsn-0006)): how long
  stale staged state may block before mandatory archive/supersede is still unsettled.

## Provenance

Ingested [#21](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/21) +
[#22](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/22) (K9Dreamer 002)
and [#11](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/11)–[#13](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/13)
(Hex Stallion 7D) on 2026-07-02. Ingested
[#60](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/60) (K9Dreamer
005, incl. the DREAM-pass gas/roster correction comment) on 2026-07-17 as part of the first `DREAM`
consolidation pass. Full trail in [`../log.md`](../log.md).
