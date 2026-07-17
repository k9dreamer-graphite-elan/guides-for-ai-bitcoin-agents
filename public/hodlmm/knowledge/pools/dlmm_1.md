---
type: kb-pool
pool: dlmm_1
pair: sBTC/USDCx
handbook: v0.10
version: 0.3
updated: 2026-07-17
last_ingested: 2026-07-17
status: active
sources:
  - https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/28
  - https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/35
  - https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/59
---

# Pool playbook — dlmm_1 (sBTC/USDCx)

> Distilled from accepted Campaign Closeout issues — **raw source = the issues** (see `sources`). Cites
> the handbook by ID; restates no constants. PnL framed as the issues framed it (net-vs-hold after gas;
> display marks context-only — INV-8). No live state cached here.

## Status & liveness

**active.** Three independent 7-day campaigns now provide complementary evidence:

- K9Dreamer `HODLMM-DLMM1-20260702-003`
  ([#28](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/28)),
  bounded autonomous and existing-sBTC-only, reached a chain-proven clean **scheduled** exit at the
  planned end (confirmed withdraw tx, wallet DLP `0`, zero user bins, renewal check run before
  withdrawing).
- Hex Stallion `HODLMM-DLMM1-20260703-002`
  ([#35](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/35)),
  bounded autonomous and fee-capture-oriented, failed its strict range SLO and its planned-end
  auto-exit. A bounded repair process eventually produced a chain-proven terminal exit, zero DLP,
  zero user bins, and a complete medium-confidence net-vs-hold report.

- K9Dreamer `HODLMM-DLMM1-20260710-004`
  ([#59](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/59), with a
  [DREAM-pass gas/roster correction](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/59#issuecomment-5003288054)),
  two-sided sBTC/USDCx band run by a **zero-LLM script monitor**: 11 clean unattended auto-moves, one
  paid `u5001`-class abort followed by a supervised withdraw→swap→redeposit recovery, and a fully
  unattended scheduled exit (tx `0x417f6be6…`, block 8570534, DLP `0`, second consecutive clean
  unattended scheduled exit on this pool).

The healthy-side campaigns prove that lifecycle-gated repair and scheduled exit can work on this
pool. The failure-side campaign shows what happens when missing-position repair, write scope, and
host disarm are not subordinate to lifecycle. Do not average those outcomes into a single success
rate. No stale / exit-only (`INV-9`) pool status is recorded.

## What worked

| Tactic | Evidence | Confidence |
|---|---|---|
| Single-token (sBTC-only) ladder entry with exact active-bin tolerance; no swap leg, no added capital for the whole campaign | [#28](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/28) | realized |
| **Standing gated repairs** (two fresh out-of-range scans + cooldown + gas cap) instead of a fixed repair count — tracked repeated full-band traversals, selling sBTC rising and buying it back falling | [#28](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/28) | realized |
| **Explicit low fee target**: the lowest configured repair fee cleared every recenter and the final exit; each step-down was a separate operator approval, never an auto-bump | [#28](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/28) | realized |
| **Guarded auto-repair, narrow scope** (same pool, existing LP only, all gates + lifecycle check before signing): one unattended repair executed cleanly before the scheduled exit | [#28](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/28) | realized |
| **Zero-LLM script monitor as degraded fallback** (direct chain reads + alerts) after an LLM-cron outage — the unattended-automation runbook's prescribed failure mode, exercised live | [#28](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/28) | realized |
| Exit via direct-read share amounts with per-bin **nonzero minimums on the expected output side only**; closure proven by wallet-DLP-zero + chain receipt, not the app display | [#28](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/28) | realized |
| **Elapsed-time strict range accounting** separated monitor freshness, in-range time, out-of-range time, and no-position time instead of treating a deployed position as fee-active | [#35](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/35) | realized |
| **Side-preserving repairs** repeatedly restored coverage without requiring the missing sBTC side; the repair loop also stopped honestly at its cycle cap while QA remained red | [#35](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/35) | realized |
| Final terminal exit passed the complete actuator chain: terminal intent, signer-ready plan, canonical confirmation, zero-DLP proof, and zero-user-bin proof | [#35](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/35) | realized |
| Public chain leg-netting separated gross withdrawal/add churn from final released inventory and charged successful, failed, and out-of-scope runtime gas to campaign PnL | [#35](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/35) | medium |
| **Zero-LLM unattended monitor at full campaign scale**: 11 gated auto-moves + the scheduled exit executed with no LLM and no human touch; one mid-campaign supervised recovery was the only intervention (~111h then ~58h unattended stretches) | [#59](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/59) + [correction](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/59#issuecomment-5003288054) | realized |
| **Slippage gate as pacing, not blocking**: a 0.5%-cap deferral during a fast move re-cleared 2h later at 0.26% and the deferred repair executed cleanly — the gate delayed, it did not strand | [#59](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/59) | realized |
| **Memo-tag campaign demarcation end-to-end** (`E` retroactive entry-tag, `X` terminal tag, txid8-bound): first live use of the [memo-tag spec](../../specs/campaign-memo-tags.md); surfaced the v1.1 tag-sink erratum on first contact | [#59](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/59) | realized |

## What failed

| Failure | Why | Evidence | Confidence |
|---|---|---|---|
| Fixed repair-count ceiling proved too rigid for a narrow band on this volatile pair; scope had to be renegotiated mid-campaign | Repair-count caps are a policy choice; the safety invariant is the gate stack → closeout/recenter addenda | [#28](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/28) | realized |
| LLM monitor cron down ~14h: a per-cron model override lost its provider prefix and failed the runtime allowlist on every tick; price crossed the whole band unmonitored (sell-high leg executed by design — only the recenter was delayed) | Model availability is a first-class automation failure mode; detection/alerting must be deterministic → [LSN-0015](../lessons/lessons-catalog.md#lsn-0015)-adjacent harness doctrine | [#28](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/28) | realized |
| Transient single-source active-bin outliers (two occurrences) would each have produced a wrong-destination move if trusted | Single reads jitter; multi-source agreement is the gate → [LSN-0013](../lessons/lessons-catalog.md#lsn-0013) | [#28](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/28) | realized |
| Dry-run/execution divergence: the signer refreshed the active bin pre-sign and executed a different destination range than the dry-run showed | Invariants must be enforced at sign time, not only dry-run time; log both targets (recenter addendum) | [#28](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/28) | realized |
| Strict active-bin coverage reached only `69.3504%` against a `90%` campaign SLO | Positive PnL and eventual closure do not retroactively satisfy the operating objective; report objective, closeout, and PnL as separate axes | [#35](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/35) | realized |
| Lifecycle precedence failed: three exposure-increasing adds landed after `campaign_ends_at`, between full withdrawals | At planned end, `auto_exit` must dominate missing-position repair and every exposure-increasing path → [LSN-0015](../lessons/lessons-catalog.md#lsn-0015) | [#35](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/35) | realized |
| Campaign scope failed at the write boundary: four successful LP writes targeted a legacy pool outside the approved single-pool campaign | Monitoring or discovering a pool is not write authority; reassert campaign scope immediately before signing | [#35](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/35) | realized |
| Auxiliary data and absent-position representation delayed a mature bounded exit and initially obscured closure input | Optional infrastructure should degrade to alert once direct withdrawal and zero-position proof are sufficient → [LSN-0016](../lessons/lessons-catalog.md#lsn-0016) | [#35](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/35) | realized |
| The actuator incurred `14` failed writes; valid strategy intent repeatedly failed at planning, postcondition, data, and terminal-state boundaries | A selected action is not execution success; completion requires confirmed tx plus post-confirm range or closure proof → [LSN-0011](../lessons/lessons-catalog.md#lsn-0011) | [#35](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/35) | realized |
| A generic signer-enabled resident remained loaded after campaign closure, although it submitted no transaction | Disarm is host-level proof, not campaign-file intent → [LSN-0017](../lessons/lessons-catalog.md#lsn-0017) | [#35 follow-up](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/35#issuecomment-4933152534) | realized |
| `(err u5001)` recurred as a **paid abort on this pool**: a ~35-bin one-sided `move-liquidity-multi` gap after a hard trend leg; dry-run and guardian gates did not catch the shape | Native-move legality is geometry ([LSN-0001](../lessons/lessons-catalog.md#lsn-0001)); defense = pre-broadcast geometry gate, deployed ~2.4 days later and verified as a free block | [#59](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/59) (`0x5ef9bfa7…`, block 8547973) | realized |
| A narrow two-sided band (±3 bins ≈ ±0.3% on this bin step) fully converted to one side twice in a single trending week — the band shape needs oscillation, and this week trended | Two-sided volatility capture presumes mean reversion inside the band; in trend, the position becomes a slow one-way conversion plus repair drag → [LSN-0020](../lessons/lessons-catalog.md#lsn-0020) | [#59](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/59) | realized |
| The closeout's own tx roster missed the 11 unattended auto-moves, inverting its gas finding (reported 0.95 STX "chain-summed" vs true 2.05 STX) | Roster completeness precedes fee arithmetic → [LSN-0019](../lessons/lessons-catalog.md#lsn-0019) | [#59 correction](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/59#issuecomment-5003288054) | realized |

## Effective recenter targeting

- **Budget for high repair cadence.** A narrow band (small bps step) on this volatile pair legitimately
  needed many gated recenters in one week; a campaign gas cap must price that in, and a repair-count cap
  is a deliberate charter choice, not a safety rule (`INV-1`; recenter runbook addendum). Field tx
  geometries in the issue are reviewer context, **not** durable constants — compute against live state
  (`INV-3`, handbook §4.2).
- **Side-offset rule follows inventory**: quote-side (Y) inventory maps to active-or-below destination
  offsets, base-side (X) inventory to active-or-above — and the rule must hold **at signing time**, even
  if the signer refreshes the active bin after the dry-run.
- **Blocking on source divergence is correct** even when the position is clearly out of range — both
  jitter outliers would have mis-targeted the move ([LSN-0013](../lessons/lessons-catalog.md#lsn-0013)).
- Repair completion = post-confirm range proof, not a confirmed tx
  ([LSN-0011](../lessons/lessons-catalog.md#lsn-0011)) — held on every recenter this campaign.
- **Lifecycle precedes repair.** Before constructing any destination, test whether the campaign is
  still authorized to increase exposure. At or after planned end, absent LP is closure progress,
  not an `enter` signal; `auto_exit` dominates all repair paths unless a renewal scope is recorded
  ([#35](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/35),
  [LSN-0015](../lessons/lessons-catalog.md#lsn-0015)).
- **Measure the actual earning condition.** Deployed value and fresh monitoring do not prove active
  fee coverage. The strict SLO numerator is elapsed time with the active bin inside the wallet's
  nonzero-liquidity range; no-position and unknown-proof time remain separate states.

## Known API / tx-pattern gotchas

- Bitflow position endpoint can show zero-liquidity rows **before** exit and return no-position/404
  **after** exit — advisory only; closure proof is wallet DLP zero + chain receipt → [LSN-0002](../lessons/lessons-catalog.md#lsn-0002)
- Transient single-source active-bin read jitter → [LSN-0013](../lessons/lessons-catalog.md#lsn-0013)
- The "simple" liquidity skill entrypoints land on-chain as the **relative-multi router functions**
  (e.g. a simple withdraw appears as `withdraw-relative-liquidity-same-multi`); record both names so
  explorer audits match the campaign ledger (closeout attribution addendum).
- Auxiliary ranking, quote, or indexer failures must not veto a mature bounded withdrawal when
  direct target-pool reads, signer/write gates, and closure proof remain available →
  [LSN-0016](../lessons/lessons-catalog.md#lsn-0016).
- A full withdrawal is not necessarily a campaign exit. If automation subsequently re-enters, label
  the earlier leg `WITHDRAW` or `REBAL_WITHDRAW`; only the final confirmed withdrawal followed by
  zero-position proof is `EXIT` ([#35](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/35)).
- Assert the authorized campaign pool immediately before every write. Pool discovery, monitoring,
  legacy inventory, or ranking inclusion does not grant mutation authority.
- Closure includes the host control plane: enumerate shared and campaign-specific schedules, prove
  no signer-enabled process still references the ended campaign, and reconcile repository,
  installed, and loaded scheduler state → [LSN-0017](../lessons/lessons-catalog.md#lsn-0017).

## PnL (honest framing — INV-8)

- **K9Dreamer 003: net ≈ `+$9` vs holding the original tokens, after gas** (confidence:
  realized-withdrawal for token quantities, clean-read for the USD marks; ≈ +18% on ~$50 deployed in
  7 days). Explicitly labeled **volatility capture, not yield**: the edge came from many complete
  band traversals through a single-sided ladder plus flow-through fees; a one-way price move would
  read very differently. Never project this shape as an APR.
  ([#28 PnL section](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/28))
- Ending inventory was heavily quote-side (the ladder's sell-high residual at planned end) — net-vs-hold
  at closeout marks already prices this; do not read the token mix shift as a loss or a gain by itself.
- Bitflow 7D display earnings: **context only, never realized** (the issue's `$24.16` display vs
  ≈ `+$9` realized headline is the canonical example).
- **Hex Stallion 002: net `+$4.269794` vs hold after all campaign-runtime gas (`+16.64%`)**
  (confidence: medium; final inventory and gas are chain-derived, USD marks are closeout-time marks).
  The deployed basis was `$25.659230`; final inventory was marked at `$30.492582`; campaign-runtime
  gas was marked at `$0.563548`. Fee-only and IL-only attribution were unavailable, so neither is
  invented. The result includes failed and out-of-scope write gas and does not use a protocol
  earnings display as profit
  ([#35 PnL section](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/35)).
- Campaign 002's positive net-vs-hold result coexists with a failed range SLO, failed planned-end
  automation, post-end re-entry, and late terminal exit. Profit is not evidence that the control
  policy was correct.
- **K9Dreamer 004: net ≈ `+$0.81` vs hold after gas (`+0.9%` on ~$88 deployed, 7 days)** —
  confidence: **reported** (USD mark on realized final inventory of 140,575 sats at the exit-hour
  mark; chain-swept gas 2.05 STX). The issue's headline read ≈ +$0.99 / +1.1% on an incomplete
  8-tx gas roster; the
  [DREAM-pass correction](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/59#issuecomment-5003288054)
  restated it against the full 24-tx chain roster ([LSN-0019](../lessons/lessons-catalog.md#lsn-0019)).
  Same pool, same week as 003's +18%: the difference was regime (trend vs oscillation), not tactics —
  do not read either as the pool's expected return. The final inventory was 100% sBTC partly via
  repair swaps executed at a mark above the exit mark; the small positive net embeds that timing.
- Bitflow display earnings for 004 (`$8.83` at the last pre-exit snapshot): **context only, never
  realized** — consistent with the [LSN-0004](../lessons/lessons-catalog.md#lsn-0004) canonical example.

## Open questions / contradictions

- **Does the high-cadence repair strategy stay net-positive in a calmer regime?** This campaign's edge
  required repeated full-band traversals; with fewer excursions, the same repair cadence could bleed
  gas versus fee income. No calm-regime closeout exists yet for this pool. *Partial answer from 004
  ([#59](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/59)): in a
  trending week the same band shape decayed to ≈ +0.9% — the open cell is now specifically
  **trend-regime handling** (wider bands, one-sided entry, or earlier conversion-and-hold), not
  calm regimes.*
- **Fee-only attribution remains medium-confidence** — repeated traversals + recentering blur a clean
  fee-vs-inventory decomposition; a lower-churn campaign would isolate it better.
- **Can a `90%` strict active-bin SLO be met economically in a high-movement regime?** Campaign 002
  reached `69.3504%` and paid for substantial write churn. A future campaign should test whether
  wider targeting or lower repair churn improves coverage after gas without hardcoding campaign
  geometry as pool doctrine.
- **Will lifecycle and write-scope gates remain dominant across every repair entrypoint?** Campaign
  003 proves the healthy path; Campaign 002 proves that one bypass can turn completed withdrawals
  into post-end re-entry. Regression evidence is needed at each exposure-increasing write path.

## Provenance

Ingested [#28](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/28)
(K9Dreamer 003, incl. follow-up comments: independent verification pass + tx-attribution convention)
on 2026-07-10. Ingested [#35](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/35)
(Hex Stallion 002, failure-first closeout plus the accepted host-control-plane addendum) on
2026-07-11. The addendum's generalized host-disarm doctrine landed separately in
[PR #36](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/pull/36);
this page preserves how that failure appeared on `dlmm_1`. Ingested
[#59](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/59) (K9Dreamer 004,
incl. the DREAM-pass gas/roster correction comment) on 2026-07-17 as part of the first `DREAM`
consolidation pass. Full trail in [`../log.md`](../log.md).
