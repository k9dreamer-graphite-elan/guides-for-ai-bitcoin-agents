---
type: kb-pool
pool: dlmm_14
pair: STX/USDCx
handbook: v0.10
version: 0.1
updated: 2026-07-29
last_ingested: 2026-07-29
status: active
sources:
  - https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/73
---

# Pool playbook — dlmm_14 (STX/USDCx v2)

> First source: K9Dreamer campaign `HODLMM-DLMMV2-20260722-007`. Empirical pool memory, not
> doctrine. No live state is cached; recompute every execution input (`INV-3`).

## Status & liveness

**Active as observed during campaign 007.** The v2 pool had current router flow, two observed
pop-through events, and enough two-sided activity to pass the successor-pool branch of
[LSN-0023](../lessons/lessons-catalog.md#lsn-0023). That historical pass is not a current liveness
guarantee.

## What worked

| Tactic | Evidence | Confidence |
|---|---|---|
| Pre-entry dead-pool + successor/router screen selected v2 instead of the structurally drained v1 venue | [#73](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/73) | realized |
| Static ask ladder above spot captured sparse pop-through-and-return events without repairs | [#73](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/73) | realized (one campaign) |
| Fresh direct per-bin reads produced nonzero expected-side withdrawal minimums; one transaction withdrew all bins and returned 631.718775 STX | [#73](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/73) | realized |
| Explicit no-auto-repair scope kept 59 intentional out-of-range scans silent and made zero unauthorized write attempts | [#73](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/73) | realized |

## What failed

| Failure | Why | Evidence | Confidence |
|---|---|---|---|
| A closeout verifier false-alarmed before the first post-end monitor tick | Verification time ignored the scheduler's cadence | [#73](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/73) | realized |
| Exit-success Telegram delivery logged `ALERT-FAILED` | Alert delivery lacked a reliable retry/queue | [#73](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/73) | reported |
| Two daily checkpoints were missed with no script log | The host did not execute cron; no catch-up detector existed | [#73](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/73) | reported |

## Effective recenter targeting

Campaign 007 was intentionally **out of range by design** and had no recenter authority. Treat this
as a static event-capture posture, not an exception to ordinary strict-range rules. A future charter
must explicitly choose that posture; authority does not transfer from this closeout (`INV-1`).

## Known API / tx-pattern gotchas

- Exit verification must use the complete scheduler window → [LSN-0027](../lessons/lessons-catalog.md#lsn-0027).
- Withdrawal arithmetic comes from fresh direct reads → [LSN-0025](../lessons/lessons-catalog.md#lsn-0025).
- Full exit event pagination is mandatory; 007 required 50/50/20 events before the empty page.

## PnL (honest framing — INV-8)

Campaign 007 returned `631.718775 STX` from a `600 STX` basis. After `0.368 STX` chain-summed gas:
**+31.350775 STX / +5.225% net vs hold** (realized-withdrawal confidence). The BFF display earnings
were context-only and are not additive.

## Open questions / contradictions

- Does per-STX edge remain near-linear at larger size before the ladder becomes material pool depth?
  Only the 600-STX point is field-exercised; [LSN-0028](../lessons/lessons-catalog.md#lsn-0028) stays
  draft until a scaled campaign tests it.
- Does this venue remain live after its first week? Re-run the successor/router/liveness screen.

## Provenance

Ingested [#73](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/73)
through the 2026-07-29 DREAM pass. Full trail in [`../log.md`](../log.md).
