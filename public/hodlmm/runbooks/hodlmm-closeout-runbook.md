---
name: HODLMM Closeout Runbook
type: runbook
version: 0.5
updated: 2026-07-13
handbook: v0.6
enforces: [INV-1, INV-6, INV-8, INV-10, INV-11, INV-12]
skills: [query, defi-portfolio-scanner, nonce-manager]
status: active
---

# HODLMM Closeout Runbook

> Conforms to the [HODLMM Agent Handbook](../handbook/HODLMM-Agent-Handbook.md) **v0.6**.
> Enforces: INV-1, INV-6, INV-8, INV-10, INV-11, INV-12.
> **Read/report-only — no on-chain writes**, with one carve-out: the optional 1 µSTX **deferred exit
> stamp** (step 5), a labeling transfer under the [memo-tag spec](../specs/campaign-memo-tags.md) —
> never a trading write. Runs *after* `hodlmm-exit-runbook` and `hodlmm-pnl-runbook`.

## Purpose

Turn a completed campaign into a single, standardized **Campaign Closeout** report — settings,
results, PnL, learnings, insights — and submit it as **one GitHub issue** so other agents can learn
from it (the cross-agent learning loop). Recommended after every campaign; not mandatory.

## When to run / when NOT to run

- **Run when:** a campaign has reached a clean exit or planned end and PnL is finalized.
- **Do NOT run** before the position is actually closed — closure proof is required (see step 3). This
  runbook reports; it does not trade. For winding down funds use `hodlmm-exit-runbook`; for the numbers
  use `hodlmm-pnl-runbook`.

## Inputs

| Param | Meaning |
|---|---|
| `campaign-id` | `HODLMM-<POOL>-<YYYYMMDD>-<seq>` |
| Transaction + Performance ledgers | the campaign's INV-11 records |
| PnL output | from `hodlmm-pnl-runbook` (net-vs-hold after gas, fee attribution + confidence) |
| Exit confirmation | the chain-confirmed withdraw tx + post-exit scan |
| Charter / Approval Scope | the original campaign authorization |

## Required Approval Scope (INV-1)

- Reporting is read-only and always allowed. **Publishing the issue is outward-facing** — gate it on a
  `publish-closeout` scope grant or explicit operator approval. Without it, the agent **produces the
  filled issue markdown for the operator to post** (do not auto-publish; never infer authority).
- The agent **never opens a PR** — proposed improvements go *in the issue*; maintainers decide on PRs.

## Gates — before submitting

```
[ ] Position is actually closed (closure proof, step 3)                 (INV-10)
[ ] Host-level disarm proven — no signer-enabled schedule can start
    against the closed campaign (host-disarm addendum below)            (INV-1)
[ ] PnL framed net-vs-hold after gas; display marks = context-only      (INV-8)
[ ] Only on-chain-public / operator-approved data; no secrets
[ ] publish-closeout scope OR operator approval to post                 (INV-1)
[ ] Report follows the standard (CONTRIBUTING.md / issue form)
```

## Procedure (read-only)

1. **SCAN / gather** — pull the campaign's two ledgers, the `pnl-runbook` output, the exit tx, and the
   charter. Re-scan positions across pools (`defi-portfolio-scanner` / `query`).
2. **ASSEMBLE** — build the closeout report in the standard shape (see "Report spec" below; the GitHub
   **Campaign Closeout** issue form enforces it).
3. **VERIFY closure proof** — confirm **wallet DLP = 0 AND the exit withdraw is chain-confirmed**
   (INV-10). Protocol/status endpoints lag — treat as advisory, not proof.
4. **PnL honesty pass** (INV-8) — headline = net-vs-hold after gas with realized confidence; any DLP or
   protocol "display earnings" labeled **context-only, never realized**.
5. **STAMP (deferred exit tag)** — if the campaign adopts the
   [memo-tag spec](../specs/campaign-memo-tags.md): after closure proof (step 3) and the honesty
   pass, emit the `X` boundary tag (`H1X:<pool>-<yymmdd>-<nnn>:<txid8>` referencing the confirmed
   exit tx; 1 µSTX transfer to the spec's tag sink, nonce serialized via `nonce-manager` —
   INV-6). Exit is a **declaration, not an
   inference**: the campaign ends when the books close, not when DLP hits zero. The stamp is a
   labeling step, **not** a closure gate — closure proof (step 3) is complete without it, and a
   failed stamp never blocks or reopens a closeout (LSN-0016). Ledger-log the tag tx (INV-11).
6. **SUBMIT** — open **one** issue via the Campaign Closeout template (title
   `[<Agent> · <Campaign-ID>] Campaign closeout — <pool>`; add ` (proposes changes)` if it includes
   proposed improvements). If unscoped, output the markdown for the operator to post.
7. **REMEMBER** (INV-11/12) — log the issue URL and the distilled lessons to memory so future campaigns
   (and `DECIDE`) benefit; also **read recent closeout issues — and the pool's KB playbook
   (`../knowledge/pools/<pool>.md`) plus the [lessons catalog](../knowledge/lessons/lessons-catalog.md) —
   before the next launch**. (The KB is maintainer-written; you read it, you don't edit it.)

## Expected outputs

- One Campaign Closeout issue (URL), or the filled issue markdown ready to post.
- A memory entry linking campaign ID → issue → key lessons.

## Failure handling

| Symptom | Handling |
|---|---|
| Ledger / entry data missing | Report with **low confidence**; flag the gap. Never fabricate a basis (INV-8). |
| Position not actually closed | Stop — this isn't a closeout yet; finish `exit` first (INV-10). |
| No GitHub scope | Emit the markdown for the operator; do not auto-publish (INV-1). |
| Tempted to "round up" earnings | Don't — net-vs-hold after gas only; display marks are context (INV-8). |

## Idempotency

Read-only and re-runnable. **Do not double-post** — if a closeout issue already exists for this
campaign ID **and this agent**, update it / comment rather than open a duplicate. Campaign ids are
wallet-scoped, not globally unique (memo-tag spec, "Identity scoping") — another agent's issue can
carry the byte-identical id, so match on the `[<Agent> · <Campaign-ID>]` title pair, never the bare
id.

## Report spec (canonical — see CONTRIBUTING.md)

Charter · Outcome summary (objective → outcome → evidence → lesson) · Timeline (entry → recentering →
failures → recovery → holds → renewal → exit) · **PnL — honest framing** (net-vs-hold-after-gas table
with confidence; display marks context-only) · Findings (finding → implication → suggested doc area) ·
**Proposed improvements** *(optional)* (missing/weak rule → evidence → risk → target doc → patch-ready
text) · Reviewer evidence (campaign ID, lifecycle timestamps, key tx hashes, closeout state, limits).

## Field-confirmed addendum — closeout outcome taxonomy (7D-LP-Campaign-2026-06)

> Source: Hex Stallion 7-day autonomous `dlmm_3` closeout (issues #11–#13).
> See [LSN-0012](../knowledge/lessons/lessons-catalog.md#lsn-0012).

Report four outcomes **separately** at closeout: **operational** (in range / exited / unresolved
repair / unresolved blocker / failed), **artifact** (missing / draft / review-ready / posted),
**upstream** (not posted / issue posted / PR opened / merged), and **accounting confidence**
(high / medium / low / unavailable). A posted contribution is not a closeout, and a confirmed tx
alone is not a closeout. For `end_behavior: auto_exit`, a clean closeout requires all three:

1. a confirmed exit transaction;
2. post-confirm proof that campaign DLP and user bins are zero (INV-10);
3. a PnL/exposure report with confidence boundaries (INV-8).

Anything less is **`closeout_unresolved`** — say so rather than implying completion. Field note:
the source campaign posted a complete three-part contribution while its LP was still out of range;
the honest `closeout_unresolved` label is what made the later repaired, chain-verified clean exit
auditable.

## Field-confirmed addendum — HODLMM-DLMM1-20260702-003 (closeout belongs in the terminal checklist)

> Source: K9Dreamer `dlmm_1` sBTC/USDCx campaign-003 closeout
> ([#28](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/28)).

After confirmed exit and PnL card generation, run this closeout runbook **before** marking the
campaign fully closed. A campaign is **`operationally_closed`** only after all three exist:

1. exit proof (confirmed withdraw tx + direct-read DLP zero / user bins empty — INV-10);
2. a PnL report with confidence boundaries (INV-8);
3. either a **posted closeout issue** or a **saved unposted issue draft**.

A campaign can be mechanically closed (position zero, crons disarmed) and still fail the learning
loop — the field campaign finished its exit and PnL cards before any closeout report existed, and
only the checklist rule closed that gap. This extends the outcome-taxonomy addendum above: the
**artifact** and **upstream** axes are not optional trailers; at least the artifact axis must reach
`review-ready` before `operationally_closed` is claimed.

## Field-confirmed addendum — campaign tx attribution without extra gas (HODLMM-DLMM1-20260702-003)

> Source: follow-up on closeout
> [#28](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/28).

Explorer history alone cannot distinguish a terminal exit from a full withdrawal used for a
rebalance. Fix this in **reporting, not on chain**:

**Zero-gas default.** Never send standalone marker transactions just for labeling. Attribution is a
report-layer convention: every closeout report (and any PnL card or issue that cites transactions)
includes, per relevant tx: `campaign_id`, `tx_role`, and `campaign_state_after_tx`. Campaign ledgers
should record `tx_role` at signing time so the closeout can copy rather than reconstruct it.

**Role vocabulary:**

- `OPEN` — first LP deposit / campaign start
- `REPAIR` — same-campaign recenter or range repair
- `WITHDRAW` — liquidity removed but the campaign may continue
- `MOVE` / `REBAL` — full withdrawal plus redeposit where the campaign remains active
- `EXIT` — terminal withdrawal: the campaign ends and no renewal scope is present
- `CLOSE` — accounting/reporting finalized after exit verification (usually no tx of its own)

The load-bearing distinction: **`EXIT` means terminal campaign completion.** A full-liquidity
withdrawal that feeds a rebalance or pool move is `WITHDRAW`/`MOVE`/`REBAL`, never `EXIT` — labeling
it `EXIT` would make routine moves read as closeouts (and vice versa).

**Optional near-zero-cost memo rule.** Only put a campaign marker in a STX memo when a memo-bearing
transaction is already being sent for another reason, or the operator explicitly approves a tiny
marker transfer. Marker txs are never mandatory. *Superseding note (2026-07-10):* the
[**campaign memo-tag spec**](../specs/campaign-memo-tags.md) is now the standing operator-approved
form of exactly that marker transfer — its `H1…` grammar **replaces** the ad-hoc deterministic IDs
this paragraph previously suggested (`<CAMPAIGN-ID>-EXIT`, `<CAMPAIGN-ID>-CLOSE`). For campaigns
that adopt the spec, boundary tags (`E`/`R`/`X`) are emitted per its rules (see step 5); the
zero-gas default still governs everything else, and the `tx_role` report-layer vocabulary above is
unchanged (tags demarcate boundaries on-chain; `tx_role` attributes every tx in reports).

Worked example (this campaign's terminal tx):

```text
campaign_id: HODLMM-DLMM1-20260702-003
tx_role: EXIT
tx: 0xe1b385610b5993a98eae69cee6417302c0709f2b303314d9a0fafbc2310b2ed4
campaign_state_after_tx: closed=true, DLP=0, userBins=[]
```

## Field-confirmed addendum — host-level disarm proof belongs in the terminal checklist (dlmm_1)

> Source: Hex Stallion `dlmm_1` sBTC/USDCx control-plane closeout addendum
> ([#35](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/35)).
> See [LSN-0017](../knowledge/lessons/lessons-catalog.md#lsn-0017).

A position can be chain-proven closed and its PnL finalized while the **execution host** still
carries stale write authority — most dangerously a *generic, signer-enabled* resident bound to the
ended campaign by an **implicit default**, not a campaign-specific schedule anyone remembers arming.
In the field failure the resident submitted no transaction and the wallet had no pending HODLMM tx,
yet autonomous `rebalance,exit` authority against a closed campaign should never have survived
closure. Position closure (step 3) is therefore **necessary but not sufficient**: `operationally_closed`
also requires **host-level disarm proof**. Run this before marking the campaign fully closed — it
complements the exit runbook's closure proof, which is position-level, and it is disarm *proof*, not
disarm *intent* (enumerate and verify absence; do not assume the close script worked):

```
[ ] Enumerate campaign-specific AND generic monitors, executors, repair loops, and watchdogs
[ ] Disable/unload every schedule that can target the ended campaign
[ ] Verify no signer-enabled process still references the campaign
[ ] Verify no in-flight transaction remains
[ ] Reconcile repository, installed, and loaded scheduler config to a dormant,
    signer-disabled, campaign-unbound template
[ ] Prove the runtime rejects closure-proven campaign state before starting a heartbeat/loop
    (fail closed; generic services require an explicit campaign-state binding, never an implicit default)
```

This extends the `operationally_closed` criteria above with a **control-plane axis**: position zero
+ PnL + artifact is necessary but not sufficient while any signer-enabled process can still start
against the closed campaign. The disarm actions themselves live in the exit / unattended-automation
runbooks (the latter's DISARM step); this runbook *verifies* them at closeout.
