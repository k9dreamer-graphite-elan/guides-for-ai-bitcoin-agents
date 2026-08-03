---
type: kb-pool
pool: dlmm_14
pair: STX/USDCx
handbook: v0.10
version: 0.2
updated: 2026-08-03
last_ingested: 2026-08-03
status: active
sources:
  - https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/73
  - https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/85
---

# Pool playbook — dlmm_14 (STX/USDCx v2)

> Sources: K9Dreamer campaigns `HODLMM-DLMMV2-20260722-007` and `HODLMM-DLMMV2-20260729-008`
> (same wallet, back-to-back weeks, second at 1.5× capital). Empirical pool memory, not doctrine.
> No live state is cached; recompute every execution input (`INV-3`).

## Status & liveness

**Active as observed during campaigns 007 and 008 (2026-07-22 → 2026-08-03).** The v2 pool had
current router flow, pop-through events in both weeks, and enough two-sided activity to pass the
successor-pool branch of [LSN-0023](../lessons/lessons-catalog.md#lsn-0023) at both entries. That
historical pass is not a current liveness guarantee.

## What worked

| Tactic | Evidence | Confidence |
|---|---|---|
| Pre-entry dead-pool + successor/router screen selected v2 instead of the structurally drained v1 venue | [#73](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/73) | realized |
| Static ask ladder above spot captured sparse pop-through-and-return events without repairs | [#73](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/73) | realized (one campaign) |
| Fresh direct per-bin reads produced nonzero expected-side withdrawal minimums; one transaction withdrew all bins and returned 631.718775 STX | [#73](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/73) | realized |
| Explicit no-auto-repair scope kept 59 intentional out-of-range scans silent and made zero unauthorized write attempts | [#73](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/73) | realized |
| The 007 ladder repeated at 1.5× (900 STX, rung share 0.9–8.2% of bin depth) kept the per-STX event edge — +92.055414 STX / +10.228% realized | [#85](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/85) | realized (one campaign; [LSN-0028](../lessons/lessons-catalog.md#lsn-0028) scaling claim still draft) |
| Alert-only early-exit target (+10%) → fresh double-read → operator confirm banked the pop instead of riding the whipsaw back ([LSN-0030](../lessons/lessons-catalog.md#lsn-0030)) | [#85](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/85) | realized |
| Alert delivery with retry + queue (007's ALERT-FAILED fix) delivered every fill/target alert; fill-fraction telemetry tracked 16.7%→41.4% before the pop | [#85](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/85) | realized |

## What failed

| Failure | Why | Evidence | Confidence |
|---|---|---|---|
| A closeout verifier false-alarmed before the first post-end monitor tick | Verification time ignored the scheduler's cadence | [#73](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/73) | realized |
| Exit-success Telegram delivery logged `ALERT-FAILED` | Alert delivery lacked a reliable retry/queue | [#73](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/73) | reported |
| Two daily checkpoints were missed with no script log | The host did not execute cron; no catch-up detector existed | [#73](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/73) | reported |
| The 007-lesson missed-day detector false-alarmed every day of 008 | Its UTC threshold ignored that crontab fires host-local ([LSN-0031](../lessons/lessons-catalog.md#lsn-0031)) | [#85](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/85) | realized |

## Effective recenter targeting

Campaign 007 was intentionally **out of range by design** and had no recenter authority. Treat this
as a static event-capture posture, not an exception to ordinary strict-range rules. A future charter
must explicitly choose that posture; authority does not transfer from this closeout (`INV-1`).

## Known API / tx-pattern gotchas

- Exit verification must use the complete scheduler window → [LSN-0027](../lessons/lessons-catalog.md#lsn-0027).
- Withdrawal arithmetic comes from fresh direct reads → [LSN-0025](../lessons/lessons-catalog.md#lsn-0025).
- Full exit event pagination is mandatory; 007 required 50/50/20 events before the empty page
  (008: 120 events, identical pagination discipline).
- BFF `tvlUsd`/`poolComposition` read absurdly low for this pool at the 008 entry ($50.81 vs
  669k STX on-chain same minute) while volume/fee fields stayed sane — never screen this venue
  on BFF TVL; read reserves on-chain.
- One MCP pool-balance read returned 414 STX against a same-minute 669,335 on Hiro — any balance
  read gating a decision needs a second source (`balanceReadDoubleSource` charter gate).

## PnL (honest framing — INV-8)

Campaign 007 returned `631.718775 STX` from a `600 STX` basis. After `0.368 STX` chain-summed gas:
**+31.350775 STX / +5.225% net vs hold** (realized-withdrawal confidence). Campaign 008 returned
`992.420414 STX` from a `900 STX` basis on day 4.3 of 7 (early-exit lock-in). After `0.365 STX`
gas: **+92.055414 STX / +10.228% net vs hold** (realized-withdrawal confidence). BFF display
earnings were context-only in both weeks and are not additive.

## Open questions / contradictions

- Does per-STX edge remain near-linear at larger size before the ladder becomes material pool depth?
  600-STX and 900-STX (1.5×) points are now field-exercised and consistent with near-linear;
  [LSN-0028](../lessons/lessons-catalog.md#lsn-0028) stays draft until a materially larger multiple
  tests the saturation claim.
- Does this venue remain live beyond its first two weeks? Re-run the successor/router/liveness
  screen at every entry.
- How much of 008's outperformance vs 007 is the early-exit policy and how much is a bigger pop?
  Only an A/B on comparable weeks can split it; treat +10% weeks as tail events, not base case.

## Provenance

Ingested [#73](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/73)
through the 2026-07-29 DREAM pass; [#85](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/85)
(campaign 008, maintainer-authored closeout, chain-verified at closeout time) ingested 2026-08-03.
Full trail in [`../log.md`](../log.md).
