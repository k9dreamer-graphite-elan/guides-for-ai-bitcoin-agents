---
type: kb-lessons
handbook: v0.6
version: 0.5
updated: 2026-07-10
last_ingested: 2026-07-10
status: active
sources:
  - https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/1
  - https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/2
  - https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/3
  - https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/4
  - https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/5
  - https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/11
  - https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/12
  - https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/13
  - https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/21
  - https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/28
  - https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/35
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
  stale TVL / an open position for a while. Variant (dlmm_1): the position endpoint showed
  zero-liquidity rows *before* exit and no-position/404 *after* exit — misleading in both directions.
- **Mitigation:** closure proof = wallet DLP zero **and** chain-confirmed withdraw tx (Hiro). Treat
  protocol status/position reads as advisory; a lagging read must **not** trigger a duplicate exit or a
  false "still open" alarm (`INV-10`).
- **Pools seen on:** [dlmm_6](../pools/dlmm_6.md)
- **Evidence:** [#4](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/4), [#5](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/5)
- **Confidence:** realized · **Status:** active · **last_ingested:** 2026-06-26

---

## effective recenter targeting

<a id="lsn-0013"></a>
### LSN-0013 — Single-source active-bin reads jitter; require multi-source agreement before any write

- **Category:** flaky-API patterns
- **Pattern:** transient wrong active-bin values from a single source (two occurrences in one
  campaign, from different read paths), each far from the true bin. Either one, trusted alone, would
  have produced a wrong-destination recenter.
- **Mitigation:** gate every write on **multi-source active-bin agreement** (direct contract read +
  protocol quote endpoint + the planning tool's own read). On divergence, block the write and re-read
  until convergence — **even when the position is clearly out of range**; a delayed correct move beats
  a prompt wrong one. Log discarded outliers. (Recenter runbook; `INV-7`.)
- **Pools seen on:** [dlmm_1](../pools/dlmm_1.md)
- **Evidence:** [#28](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/28)
- **Confidence:** realized · **Status:** active · **last_ingested:** 2026-07-10

<a id="lsn-0016"></a>
### LSN-0016 — Auxiliary-data failures must not block a bounded terminal exit

- **Category:** flaky-API patterns
- **Pattern:** a mature campaign-end `exit` was blocked by optional infrastructure/market-data
  errors even though the target-pool withdrawal proof and write gates were clean; separately,
  post-exit closure was misclassified as incomplete because "no active LP inventory + zero user
  bins + absent/zero DLP" was not accepted as closure input. Both faults delayed a clean closeout
  past the planned end.
- **Mitigation:** define the gate hierarchy explicitly. A bounded terminal exit requires ONLY:
  direct-read withdrawal proof (per-bin shares, nonzero expected-side minimums), clean write gates
  (mempool, nonce, gas), and lifecycle state. Auxiliary reads — market data, display/positions
  endpoints, price cards — **degrade to alert, never block**. And closure-proof acceptance is:
  chain-confirmed withdraw + direct-read zero user bins + zero/absent DLP (a missing DLP row for an
  empty position is zero, not unknown — extends [LSN-0002](#lsn-0002)). (`INV-9`, `INV-10`;
  exit + unattended-automation runbooks.)
- **Pools seen on:** [dlmm_1](../pools/dlmm_1.md)
- **Evidence:** [#11 campaign-2 update](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/11#issuecomment-4931652170) (exit tx `0xbb118b51…0987` verified success/canonical, block 8518497)
- **Confidence:** realized · **Status:** active · **last_ingested:** 2026-07-10

<a id="lsn-0005"></a>
### LSN-0005 — Out-of-range nonzero LP is a required repair/pause, never ordinary "hold"

- **Category:** effective recenter targeting
- **Pattern:** narrow/reactive bands drift outside active-bin coverage and stop earning active-bin fees
  while still carrying one-sided exposure. A monitor can be fresh and a position can still have value
  without the LP earning — monitoring freshness ≠ earning.
- **Mitigation:** require **strict range proof** (active bin inside the wallet's liquidity range). An
  out-of-range nonzero LP is a required repair/exit/`pause_with_blocker` (with a watch condition), never
  ordinary `hold` (`INV-9`; see the active-LP runbook). Confirmed again on a single-pool autonomous
  campaign: entered in range, repaired once, ended out of range — with a *boundary ladder* the bounded
  sit-and-wait was actively profitable, but only because the planned end bounded it.
- **Pools seen on:** [dlmm_6](../pools/dlmm_6.md); [dlmm_3](../pools/dlmm_3.md); Hex Stallion multi-pool campaign
- **Evidence:** [#1](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/1), [#2](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/2), [#3](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/3), [#5](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/5), [#11](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/11), [#21](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/21)
- **Confidence:** realized · **Status:** active · **last_ingested:** 2026-07-02

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
  failure handling = handbook Ch.3.) Confirmed on a second, autonomous campaign: staged repair restored
  range exactly once, then continuation fragility persisted through closeout.
- **Pools seen on:** Hex Stallion multi-pool campaign; [dlmm_3](../pools/dlmm_3.md)
- **Evidence:** [#1](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/1), [#2](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/2), [#3](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/3), [#11](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/11), [#12](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/12)
- **Confidence:** realized · **Status:** active · **last_ingested:** 2026-07-02

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

<a id="lsn-0014"></a>
### LSN-0014 — Fee bumping is a new approval scope, not an agent convenience

- **Category:** operator approvals/rejections
- **Pattern:** on micro-notional campaigns, silent or automatic tx-fee bumps can erase the entire
  edge. One campaign deliberately stepped its repair fee target down three times — each step a
  separate, explicit operator approval — and the lowest target cleared every recenter and the final
  planned-end exit on mainnet.
- **Mitigation:** if the configured fee target fails, **stop and alert**. Raising the fee is a new
  approval decision unless a fee-bump ladder was explicitly authorized in the campaign charter
  (`INV-1`). Record the fee policy and its history in campaign state. (Exit + recenter runbook addenda.)
- **Pools seen on:** [dlmm_1](../pools/dlmm_1.md)
- **Evidence:** [#28](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/28)
- **Confidence:** realized · **Status:** active · **last_ingested:** 2026-07-10

<a id="lsn-0015"></a>
### LSN-0015 — Autonomous repair loops must read campaign lifecycle before signing

- **Category:** operator approvals/rejections
- **Pattern:** a repair daemon that ignores lifecycle state can repair a **closed** campaign —
  re-entering a pool the operator believes is exited, outside any approval scope.
- **Mitigation:** every autonomous write path reads campaign lifecycle first and **refuses repairs at
  or after planned end unless a renewal scope is present**; the terminal exit runs an explicit renewal
  check before withdrawing; the loop is disarmed immediately after closure. The gate must cover **ALL
  write paths — including missing-LP re-entry and top-up repairs — not just recenters**: once the
  window closes, `auto_exit` dominates everything. Field-proven from both sides: the healthy case
  (#28: one lifecycle-gated unattended auto-repair, renewal-checked scheduled exit, post-close disarm)
  and the failure case (Hex Stallion `7D-LP-Campaign-2`, dlmm_1: a post-deadline repair path
  re-entered the pool **three times on-chain** after `campaign_ends_at` before the recovered exit —
  adds `0x164d439c…`/`0xec45f224…`/`0xf1b950e9…` interleaved with withdrawals, 2026-07-10).
  (`INV-1`; active-LP + unattended-automation runbooks.)
- **Pools seen on:** [dlmm_1](../pools/dlmm_1.md)
- **Evidence:** [#28](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/28), [#11 campaign-2 update](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/11#issuecomment-4931652170)
- **Confidence:** realized · **Status:** active · **last_ingested:** 2026-07-10

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
  from a terminal state is not. (Campaign prompt.) Confirmed from the healthy side on dlmm_1: a
  scheduled planned-end exit ran an explicit renewal check, withdrew cleanly, and the automation
  refused any post-end repair ([LSN-0015](#lsn-0015)).
- **Pools seen on:** [dlmm_6](../pools/dlmm_6.md), [dlmm_1](../pools/dlmm_1.md)
- **Evidence:** [#4](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/4), [#5](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/5), [#28](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/28)
- **Confidence:** realized · **Status:** active · **last_ingested:** 2026-07-10

<a id="lsn-0008"></a>
### LSN-0008 — Monitor freshness ≠ completeness

- **Category:** post-check lessons
- **Pattern:** a fresh-but-incomplete read (missing target position/bin data) can erase the last
  complete range proof.
- **Mitigation:** track **freshness** and **completeness** as separate claims; a fresh incomplete
  monitor cannot supersede a prior complete proof. Keep four fields distinct: latest monitor, last
  complete in-range proof, last complete out-of-range proof, incomplete-monitor blocker. (Active-LP runbook.)
- **Pools seen on:** Hex Stallion multi-pool campaign; [dlmm_3](../pools/dlmm_3.md)
- **Evidence:** [#1](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/1), [#2](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/2), [#3](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/3), [#11](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/11), [#12](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/12)
- **Confidence:** realized · **Status:** active · **last_ingested:** 2026-07-02

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

<a id="lsn-0011"></a>
### LSN-0011 — Tx confirmation is not repair proof: prove the actuator chain end-to-end

- **Category:** post-check lessons
- **Pattern:** a campaign can select the correct repair (`rebalance` / bounded `exit`) every cycle and
  still fail. Two campaigns — one operator-intervened, one autonomous — broke at the *conversion* layer:
  plan-builder failures, incomplete user-bin proof, signer gates, and missing post-confirm proof each
  severed the link between intent and a restored earning range. Several transactions confirmed on-chain
  while final proof still showed out-of-range LP; auto-exit missed the campaign end.
- **Mitigation:** track the actuator chain as first-class state, separate from strategy intent:
  `required_action → plan_built → signer_gated → tx_confirmed → post_confirm_range_proven` (or exit
  proven). A repair is complete only when the last link holds. Plan-builder failure is an actuator
  incident, not an ordinary pause. A retry loop preserves intent — it does not repair; if the same
  required action stays blocked across repeated cycles, open an incident record with blocker, failed
  tx/preflight shape, diagnosis, fix or archive/supersede path, and the post-fix proof required.
  (Active-LP runbook addendum; `INV-9`, `INV-10`.)
- **Pools seen on:** [dlmm_3](../pools/dlmm_3.md); [dlmm_1](../pools/dlmm_1.md) (confirmed from the
  healthy side: 16 repairs + exit, each with post-confirm direct-read range/closure proof, 0 broken links)
- **Evidence:** [#11](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/11), [#12](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/12), [#1](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/1), [#2](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/2), [#28](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/28)
- **Confidence:** realized · **Status:** active · **last_ingested:** 2026-07-10

<a id="lsn-0012"></a>
### LSN-0012 — A posted contribution is not a closeout: report closeout outcomes separately

- **Category:** post-check lessons
- **Pattern:** a campaign posted a complete three-part contribution package while its LP was still out
  of range with no completed exit — documentation-complete and operationally-failed at the same time.
  The initial closeout honestly reported itself unresolved; a later repaired exit (confirmed tx +
  zero-DLP/user-bin proof) upgraded it to clean, and the honest label is what made that auditable.
- **Mitigation:** at closeout, report **operational**, **artifact**, **upstream**, and
  **accounting-confidence** outcomes separately. For `end_behavior: auto_exit`, a clean closeout
  requires all three: a confirmed exit tx, post-confirm proof of zero DLP / zero user bins, and a
  PnL/exposure report with confidence boundaries — anything less is `closeout_unresolved`.
  (Closeout runbook addendum; `INV-8`, `INV-10`.)
- **Pools seen on:** [dlmm_3](../pools/dlmm_3.md)
- **Evidence:** [#11](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/11) (incl. follow-up comments), [#12](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/12), [#13](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/13)
- **Confidence:** realized · **Status:** active · **last_ingested:** 2026-07-02

<a id="lsn-0017"></a>
### LSN-0017 — Disarm is host-level: no signer-enabled process may outlive campaign closure

- **Category:** post-check lessons
- **Pattern:** a campaign's dedicated exit, zero-DLP/zero-user-bin proof, and PnL were all valid, yet
  the execution **host** was not cleanly disarmed. A **generic, signer-enabled resident** —
  autonomous mode, `rebalance,exit` scope, 6h interval — was still loaded against a *separate,
  already-ended* campaign via an **implicit campaign default** (not a campaign-specific schedule
  anyone remembered arming). Its latest cycle timed out and submitted no tx, and the wallet had no
  pending HODLMM tx, but stale write authority survived closure. Position-level closure ≠
  control-plane closure.
- **Mitigation:** disarm proof is **host-level, and it is a proof, not an intent**. At close: (a)
  enumerate **both campaign-specific and generic** monitors/executors/repair loops/watchdogs; (b)
  disable/unload every schedule that can target the ended campaign; (c) verify no signer-enabled
  process still references it; (d) verify no in-flight tx remains; (e) **reconcile repository ↔
  installed ↔ loaded** scheduler config to a dormant, signer-disabled, campaign-unbound template; and
  (f) prove the runtime **fails closed** — a closure-proven campaign state is rejected *before* any
  heartbeat/loop can start, and generic services require an explicit campaign-state binding rather
  than an implicit default. Extends [LSN-0015](#lsn-0015) from the campaign-specific write-path gate
  to the shared control plane. (`INV-1`; closeout + unattended-automation runbooks.)
- **Pools seen on:** [dlmm_1](../pools/dlmm_1.md)
- **Evidence:** [#35](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/35) (Hex Stallion control-plane closeout addendum; post-close source refresh at HODLMM `main` `b4af6777`; terminal exit tx `0xbb118b51…0987` unaffected, still success/canonical)
- **Confidence:** realized · **Status:** active · **last_ingested:** 2026-07-10
