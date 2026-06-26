---
name: HODLMM Closeout Runbook
type: runbook
version: 0.1
updated: 2026-06-03
handbook: v0.6
enforces: [INV-1, INV-8, INV-10, INV-11, INV-12]
skills: [query, defi-portfolio-scanner, hodlmm-move-liquidity, memory]
status: draft
---

# HODLMM Closeout Runbook

> Conforms to the [HODLMM Agent Handbook](../handbook/HODLMM-Agent-Handbook.md) **v0.6**.
> Enforces: INV-1, INV-8, INV-10, INV-11, INV-12.
> **Read/report-only — no on-chain writes.** Runs *after* `hodlmm-exit-runbook` and `hodlmm-pnl-runbook`.

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
5. **SUBMIT** — open **one** issue via the Campaign Closeout template (title
   `[<Agent> · <Campaign-ID>] Campaign closeout — <pool>`; add ` (proposes changes)` if it includes
   proposed improvements). If unscoped, output the markdown for the operator to post.
6. **REMEMBER** (INV-11/12) — log the issue URL and the distilled lessons to memory so future campaigns
   (and `DECIDE`) benefit; also **read recent closeout issues before the next launch**.

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
campaign ID, update it / comment rather than open a duplicate.

## Report spec (canonical — see CONTRIBUTING.md)

Charter · Outcome summary (objective → outcome → evidence → lesson) · Timeline (entry → recentering →
failures → recovery → holds → renewal → exit) · **PnL — honest framing** (net-vs-hold-after-gas table
with confidence; display marks context-only) · Findings (finding → implication → suggested doc area) ·
**Proposed improvements** *(optional)* (missing/weak rule → evidence → risk → target doc → patch-ready
text) · Reviewer evidence (campaign ID, lifecycle timestamps, key tx hashes, closeout state, limits).
