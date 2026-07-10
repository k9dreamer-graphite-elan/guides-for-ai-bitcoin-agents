---
type: kb-pool
pool: dlmm_1
pair: sBTC/USDCx
handbook: v0.9
version: 0.1
updated: 2026-07-10
last_ingested: 2026-07-10
status: active
sources:
  - https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/28
---

# Pool playbook — dlmm_1 (sBTC/USDCx)

> Distilled from accepted Campaign Closeout issues — **raw source = the issues** (see `sources`). Cites
> the handbook by ID; restates no constants. PnL framed as the issues framed it (net-vs-hold after gas;
> display marks context-only — INV-8). No live state cached here.

## Status & liveness

**active.** One campaign to date — K9Dreamer `HODLMM-DLMM1-20260702-003`
([#28](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/28)), 7 days
bounded autonomous, existing-sBTC-only — reached a chain-proven clean **scheduled** exit at the planned
end (confirmed withdraw tx, wallet DLP `0`, zero user bins, renewal check run before withdrawing).
No stale / exit-only (`INV-9`) status recorded.

## What worked

| Tactic | Evidence | Confidence |
|---|---|---|
| Single-token (sBTC-only) ladder entry with exact active-bin tolerance; no swap leg, no added capital for the whole campaign | [#28](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/28) | realized |
| **Standing gated repairs** (two fresh out-of-range scans + cooldown + gas cap) instead of a fixed repair count — tracked repeated full-band traversals, selling sBTC rising and buying it back falling | [#28](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/28) | realized |
| **Explicit low fee target**: the lowest configured repair fee cleared every recenter and the final exit; each step-down was a separate operator approval, never an auto-bump | [#28](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/28) | realized |
| **Guarded auto-repair, narrow scope** (same pool, existing LP only, all gates + lifecycle check before signing): one unattended repair executed cleanly before the scheduled exit | [#28](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/28) | realized |
| **Zero-LLM script monitor as degraded fallback** (direct chain reads + alerts) after an LLM-cron outage — the unattended-automation runbook's prescribed failure mode, exercised live | [#28](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/28) | realized |
| Exit via direct-read share amounts with per-bin **nonzero minimums on the expected output side only**; closure proven by wallet-DLP-zero + chain receipt, not the app display | [#28](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/28) | realized |

## What failed

| Failure | Why | Evidence | Confidence |
|---|---|---|---|
| Fixed repair-count ceiling proved too rigid for a narrow band on this volatile pair; scope had to be renegotiated mid-campaign | Repair-count caps are a policy choice; the safety invariant is the gate stack → closeout/recenter addenda | [#28](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/28) | realized |
| LLM monitor cron down ~14h: a per-cron model override lost its provider prefix and failed the runtime allowlist on every tick; price crossed the whole band unmonitored (sell-high leg executed by design — only the recenter was delayed) | Model availability is a first-class automation failure mode; detection/alerting must be deterministic → [LSN-0015](../lessons/lessons-catalog.md#lsn-0015)-adjacent harness doctrine | [#28](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/28) | realized |
| Transient single-source active-bin outliers (two occurrences) would each have produced a wrong-destination move if trusted | Single reads jitter; multi-source agreement is the gate → [LSN-0013](../lessons/lessons-catalog.md#lsn-0013) | [#28](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/28) | realized |
| Dry-run/execution divergence: the signer refreshed the active bin pre-sign and executed a different destination range than the dry-run showed | Invariants must be enforced at sign time, not only dry-run time; log both targets (recenter addendum) | [#28](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/28) | realized |

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

## Known API / tx-pattern gotchas

- Bitflow position endpoint can show zero-liquidity rows **before** exit and return no-position/404
  **after** exit — advisory only; closure proof is wallet DLP zero + chain receipt → [LSN-0002](../lessons/lessons-catalog.md#lsn-0002)
- Transient single-source active-bin read jitter → [LSN-0013](../lessons/lessons-catalog.md#lsn-0013)
- The "simple" liquidity skill entrypoints land on-chain as the **relative-multi router functions**
  (e.g. a simple withdraw appears as `withdraw-relative-liquidity-same-multi`); record both names so
  explorer audits match the campaign ledger (closeout attribution addendum).

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

## Open questions / contradictions

- **Does the high-cadence repair strategy stay net-positive in a calmer regime?** This campaign's edge
  required repeated full-band traversals; with fewer excursions, the same repair cadence could bleed
  gas versus fee income. No calm-regime closeout exists yet for this pool.
- **Fee-only attribution remains medium-confidence** — repeated traversals + recentering blur a clean
  fee-vs-inventory decomposition; a lower-churn campaign would isolate it better.

## Provenance

Ingested [#28](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/28)
(K9Dreamer 003, incl. follow-up comments: independent verification pass + tx-attribution convention)
on 2026-07-10. Full trail in [`../log.md`](../log.md).
