---
type: kb-lessons
handbook: v0.6
version: 0.1
updated: 2026-06-26
last_ingested: 2026-06-26
status: active
sources:
  - https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/1
  - https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/2
  - https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/3
  - https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/4
  - https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/5
---

# HODLMM cross-campaign lessons & failure patterns

> The reviewed, shared analogue of an agent's private `memory/hodlmm-lessons.md`. Organized by the six
> **`INV-12`** memory categories (handbook §6.5). Each entry cites the handbook by ID and the source
> issues by URL; PnL claims carry confidence (INV-8). `LSN-` ids are stable and never reused; lessons
> are **superseded, not deleted**.

Categories: [stale-pool IDs](#stale-pool-ids) · [flaky-API patterns](#flaky-api-patterns) ·
[effective recenter targeting](#effective-recenter-targeting) · [failed-tx patterns](#failed-tx-patterns) ·
[operator approvals/rejections](#operator-approvalsrejections) · [post-check lessons](#post-check-lessons)

---

## stale-pool IDs

_No stale-pool lessons recorded yet._ dlmm_6 was operated to a clean exit and not flagged stale
([#4](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/4)). When a
closeout flags a pool exit-only (`INV-9`), record it here and set the pool page `status: stale`.

---

## flaky-API patterns

<a id="lsn-0002"></a>
### LSN-0002 — Bitflow status/position endpoints lag after a confirmed exit

- **Category:** flaky-API patterns
- **Pattern:** after a withdraw is chain-confirmed, Bitflow status/position endpoints can still show
  stale TVL / an open position for a while.
- **Mitigation:** closure proof = wallet DLP zero **and** chain-confirmed withdraw tx (Hiro). Treat
  protocol status/position reads as advisory; a lagging read must **not** trigger a duplicate exit or a
  false "still open" alarm (`INV-10`).
- **Pools seen on:** [dlmm_6](../pools/dlmm_6.md)
- **Evidence:** [#4](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/4), [#5](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/5)
- **Confidence:** realized · **Status:** active · **last_ingested:** 2026-06-26

---

## effective recenter targeting

<a id="lsn-0005"></a>
### LSN-0005 — Out-of-range nonzero LP is a required repair/pause, never ordinary "hold"

- **Category:** effective recenter targeting
- **Pattern:** narrow/reactive bands drift outside active-bin coverage and stop earning active-bin fees
  while still carrying one-sided exposure. A monitor can be fresh and a position can still have value
  without the LP earning — monitoring freshness ≠ earning.
- **Mitigation:** require **strict range proof** (active bin inside the wallet's liquidity range). An
  out-of-range nonzero LP is a required repair/exit/`pause_with_blocker` (with a watch condition), never
  ordinary `hold` (`INV-9`; see the active-LP runbook).
- **Pools seen on:** [dlmm_6](../pools/dlmm_6.md); Hex Stallion multi-pool campaign
- **Evidence:** [#1](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/1), [#2](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/2), [#3](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/3), [#5](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/5)
- **Confidence:** realized · **Status:** active · **last_ingested:** 2026-06-26

---

## failed-tx patterns

<a id="lsn-0001"></a>
### LSN-0001 — Downward one-sided same-pool native move aborts `(err u5001)`

- **Category:** failed-tx patterns
- **Pattern:** a same-pool native move (`move-relative-liquidity-multi`) with overlapping source/target
  bins, or a downward shift on a fully one-sided position, aborts with `(err u5001)`. Upward /
  non-overlapping shapes succeed. Two independent campaigns hit the same wall.
- **Mitigation:** before broadcasting, prove source/target **non-overlap** and a legal direction for the
  position's one-sidedness. Overlap or downward-one-sided → route to **withdraw → swap → redeposit**.
  Never blind-retry a `(err u5001)` shape — it is a shape rejection, not a timing hiccup. (Recenter
  runbook; `INV-3`.)
- **Pools seen on:** [dlmm_6](../pools/dlmm_6.md); Hex Stallion multi-pool campaign
- **Evidence:** [#1](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/1), [#2](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/2), [#4](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/4), [#5](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/5)
- **Confidence:** realized · **Status:** active · **last_ingested:** 2026-06-26

<a id="lsn-0003"></a>
### LSN-0003 — First multi-bin deposit postcondition aborts

- **Category:** failed-tx patterns
- **Pattern:** exact NFT postconditions are brittle for first-time multi-bin deposits — two
  `abort_by_post_condition` attempts preceded the first successful deposit.
- **Mitigation:** prefer fungible spend caps + `min-dlp` + active-bin tolerance over exact NFT
  postconditions for multi-bin deposits (`INV-2`, LP Allow form).
- **Pools seen on:** [dlmm_6](../pools/dlmm_6.md)
- **Evidence:** [#4](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/4)
- **Confidence:** realized · **Status:** active · **last_ingested:** 2026-06-26

<a id="lsn-0006"></a>
### LSN-0006 — Staged withdraw/add must be modeled as an incident state machine

- **Category:** failed-tx patterns
- **Pattern:** staged repair restores range once, but stale staged continuation state later **freezes
  the actuator** and blocks unrelated repairs through closeout. Correct repair *intent* survives, but
  there is no safe execution path.
- **Mitigation:** treat staged withdraw/add as a continuation/incident state machine with diagnosis +
  owner + archive/supersede + post-fix proof + an SLA — not an open-ended retry loop. (Recenter runbook;
  failure handling = handbook Ch.3.)
- **Pools seen on:** Hex Stallion multi-pool campaign
- **Evidence:** [#1](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/1), [#2](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/2), [#3](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/3)
- **Confidence:** realized · **Status:** active · **last_ingested:** 2026-06-26

---

## operator approvals/rejections

<a id="lsn-0010"></a>
### LSN-0010 — Social comments are not control inputs

- **Category:** operator approvals/rejections
- **Pattern:** public discussion of a campaign occurred, but execution authority stayed with the
  operator and the approved scope.
- **Mitigation:** social/community commentary is never an execution input. Execution authority = the
  operator + the granted scope, not the issue/social thread (`INV-1`).
- **Pools seen on:** [dlmm_6](../pools/dlmm_6.md)
- **Evidence:** [#4](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/4)
- **Confidence:** realized · **Status:** active · **last_ingested:** 2026-06-26

---

## post-check lessons

<a id="lsn-0004"></a>
### LSN-0004 — DLP / display mark ≠ realized fee income

- **Category:** post-check lessons
- **Pattern:** BFF/DLP "display earnings" read far above the realized net-vs-hold (display ~$27 vs a
  ≈flat realized result). Reporting the mark as profit is the easiest way to lie with a closeout.
- **Mitigation:** headline PnL = net-vs-hold after gas with a confidence label; DLP balance and protocol
  display earnings are **context only, never realized** (`INV-8`; PnL runbook).
- **Pools seen on:** [dlmm_6](../pools/dlmm_6.md); Hex Stallion multi-pool campaign
- **Evidence:** [#1](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/1), [#3](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/3), [#4](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/4), [#5](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/5)
- **Confidence:** realized · **Status:** active · **last_ingested:** 2026-06-26

<a id="lsn-0007"></a>
### LSN-0007 — A campaign needs an exit-only terminal state

- **Category:** post-check lessons
- **Pattern:** the agent's own state machine blocked its planned-end exit because state was `planned_end`,
  not `active` — capital can be stranded by a state machine that can't close.
- **Mitigation:** define an **exit-only terminal state** that permits final withdrawal from non-`active`
  states (`planned_end`, `halted`, `incident`). Closing is always permitted; opening new earning legs
  from a terminal state is not. (Campaign prompt.)
- **Pools seen on:** [dlmm_6](../pools/dlmm_6.md)
- **Evidence:** [#4](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/4), [#5](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/5)
- **Confidence:** realized · **Status:** active · **last_ingested:** 2026-06-26

<a id="lsn-0008"></a>
### LSN-0008 — Monitor freshness ≠ completeness

- **Category:** post-check lessons
- **Pattern:** a fresh-but-incomplete read (missing target position/bin data) can erase the last
  complete range proof.
- **Mitigation:** track **freshness** and **completeness** as separate claims; a fresh incomplete
  monitor cannot supersede a prior complete proof. (Active-LP runbook.)
- **Pools seen on:** Hex Stallion multi-pool campaign
- **Evidence:** [#1](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/1), [#2](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/2), [#3](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/3)
- **Confidence:** realized · **Status:** active · **last_ingested:** 2026-06-26

<a id="lsn-0009"></a>
### LSN-0009 — Gas caps are per-cycle, not just per-campaign

- **Category:** post-check lessons
- **Pattern:** a per-campaign-only gas cap can be drained by a single failing recovery loop (the initial
  cap would have been exhausted mid-run without "sit and wait").
- **Mitigation:** maintain a **per-recovery-cycle** gas cap in addition to the per-campaign cap; if a
  cycle would exceed it, stop and record a blocker instead of retrying. (Active-LP runbook.)
- **Pools seen on:** [dlmm_6](../pools/dlmm_6.md)
- **Evidence:** [#4](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/4), [#5](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/5)
- **Confidence:** realized · **Status:** active · **last_ingested:** 2026-06-26
