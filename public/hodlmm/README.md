# HODLMM — Agent Guides

> **⚠️ Skills advisory:** before installing or running the public Bitflow skills these guides reference,
> read [pinned issue #53](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/53)
> — a 2026-07-15 field audit found critical safety issues; upstream fixes are landing
> (`aibtcdev/skills` #409 merged, #406/#407/#408/#410/#411 in review) and the issue keeps the
> current install-then-patch recipe up to date.

Everything an autonomous agent (and its operator) needs to trade and provide liquidity on **Bitflow
HODLMM** (DLMM concentrated-liquidity pools on Stacks) safely.

> **Read [Handbook Chapter 0](./handbook/HODLMM-Agent-Handbook.md#chapter-0--invariants--pre-flight)
> before any autonomous trade or LP action.** It is the safety floor.

## Reading order

1. **[Handbook](./handbook/HODLMM-Agent-Handbook.md)** — the doctrine. Start with Ch.0 (invariants) and Ch.1 (canonical reference).
2. **[Operating guide](./operating-guide/hodlmm-operating-guide.md)** — daily practice + how to pick a strategy.
3. **[Runbooks](./runbooks/)** — the step-by-step procedure for whatever you're about to do.

## Documents

### Handbook (doctrine)
[`handbook/`](./handbook/) — canonical safety model, invariants, terminology, contract truths, fee
mechanics. Versioned (currently **v0.10**). Plus onboarding notes, security policy, contributing, license.

### Operating guide (field manual)
[`operating-guide/hodlmm-operating-guide.md`](./operating-guide/hodlmm-operating-guide.md) — what to
check and how often, the tool/skill catalog, **strategy profiles** (which LP strategy to run when),
and what healthy operation looks like.

[`operating-guide/hodlmm-autonomous-campaign-prompt.md`](./operating-guide/hodlmm-autonomous-campaign-prompt.md) —
copy-paste prompt for asking an operator/agent pair to plan a fully autonomous HODLMM pool campaign.

### Runbooks (executable procedures)

Each runbook is one operation: inputs → gates → procedure (skills/commands) → expected outputs →
failure handling. All conform to the handbook and declare the invariants they enforce.

| Runbook | Purpose | Status |
|---|---|---|
| [`hodlmm-active-lp-management-runbook.md`](./runbooks/hodlmm-active-lp-management-runbook.md) | Manage concentrated liquidity near the active bin under approval (scan → recenter loop). | active |
| [`hodlmm-exit-runbook.md`](./runbooks/hodlmm-exit-runbook.md) | Exit / stale-pool recovery — withdraw a position and stand down. | active |
| [`hodlmm-unattended-automation-runbook.md`](./runbooks/hodlmm-unattended-automation-runbook.md) | Arm + operate an unattended monitor/executor loop for a campaign — day-0 environment parity, per-tick write gates, watchdog, halt/recover, rehearsal, disarm. | active |
| [`hodlmm-campaign-entry-runbook.md`](./runbooks/hodlmm-campaign-entry-runbook.md) | Select a pool, grant scope, place the initial LP position. | draft |
| [`hodlmm-recenter-runbook.md`](./runbooks/hodlmm-recenter-runbook.md) | The atomic recenter procedure (move drifted bins around active). | active |
| [`hodlmm-inventory-balancing-runbook.md`](./runbooks/hodlmm-inventory-balancing-runbook.md) | Restore target token ratio via corrective swap + redeploy. | draft |
| [`hodlmm-pnl-runbook.md`](./runbooks/hodlmm-pnl-runbook.md) | End-of-campaign PnL accounting — earned fees vs IL vs DLP m2m (read-only, INV-8). | active |
| [`hodlmm-closeout-runbook.md`](./runbooks/hodlmm-closeout-runbook.md) | Post-campaign: assemble + submit the standardized Campaign Closeout issue (the learning loop). | active |
| [`hodlmm-divergence-safety-runbook.md`](./runbooks/hodlmm-divergence-safety-runbook.md) | Read-only gate: classify price-divergence + feed health (aligned/defensive/abnormal); disambiguate feed lag from real decoupling; emit the write/halt verdict. | draft |
| [`hodlmm-stuck-transaction-runbook.md`](./runbooks/hodlmm-stuck-transaction-runbook.md) | Triage a stuck/reverted/partial tx to root cause (underpriced vs read-ceiling vs adversarial) and recover. | draft |
| [`hodlmm-volatile-pair-mm-runbook.md`](./runbooks/hodlmm-volatile-pair-mm-runbook.md) | One management cycle for a volatile-major/cash pair — composes the knobs, applies the V-only cap, dispatches recenter/rebalance/exit. | draft |
| [`hodlmm-adverse-selection-runbook.md`](./runbooks/hodlmm-adverse-selection-runbook.md) | Read-only: estimate expected adverse-selection cost + breakeven width floor (feeds width/size). | draft |
| [`hodlmm-pair-calibration-runbook.md`](./runbooks/hodlmm-pair-calibration-runbook.md) | Pre-launch: derive + validate a new pair's caps/thresholds; enforce the ordering invariants. | draft |

Authoring or updating a runbook? Read [`runbooks/AGENT-AUTHORING-GUIDE.md`](./runbooks/AGENT-AUTHORING-GUIDE.md) first, then copy [`runbooks/_TEMPLATE-runbook.md`](./runbooks/_TEMPLATE-runbook.md).

### Knowledge base (distilled campaign memory)

[`knowledge/`](./knowledge/) — the cross-campaign distillation of accepted Campaign Closeout issues:
per-pool playbooks ([`pools/`](./knowledge/pools/)) and a lessons & failure-pattern catalog
([`lessons/lessons-catalog.md`](./knowledge/lessons/lessons-catalog.md)). **Read it before launching on
a pool.** It is **maintainer-written / agent-read** — agents contribute by submitting a closeout issue,
never by editing the KB. Maintenance is governed by [`knowledge/KB-MAINTAINER-GUIDE.md`](./knowledge/KB-MAINTAINER-GUIDE.md).

### Practice guides (cross-cutting how-to)

[`guides/`](./guides/) — cross-cutting practice guides that span the loop, the memory system, and the
collaborative layer at once (above the level of any single runbook).
[`guides/agent-dreaming-guide.md`](./guides/agent-dreaming-guide.md) covers **"dreaming"** — out-of-band
memory consolidation — to improve agent learning, context, multi-agent operation, and the memory system,
with key takeaways and an easy/med/complex implementation matrix; the accompanying
[Cross-Campaign Dreaming Report template](./guides/cross-campaign-dreaming-report-template.md) is the
fleet-level digest. Guides add no doctrine — they cite the handbook by `INV-` ID.

### Tools (reference implementations)

[`tools/`](./tools/) — small, copy-and-adapt reference implementations of doctrine that is easier to
trust as running code. [`tools/earnings-card/`](./tools/earnings-card/) renders the
[`hodlmm-pnl-runbook`](./runbooks/hodlmm-pnl-runbook.md) Campaign PnL Report (a ledger-derived report
object) into a Bitflow-style card PNG — NET-PnL-after-gas hero, Bitflow's Earnings/Fee-TVL as
subordinate non-additive chips — with a stdlib test suite. Illustrative, not a dependency.

## Conventions

- Filenames: `hodlmm-<operation>-runbook.md`, lowercase-hyphen, **one operation per file**.
- Every runbook's frontmatter declares `handbook:` version + `enforces:` (the `INV-` IDs) + `skills:`.
- No mutable live state in any doc (pool lists, TVL, APR, fee rates are queried live).
- Knowledge-base pages **cite** issues by URL and the handbook by `INV-` ID — they never restate
  handbook constants, and never report a DLP/display mark as realized profit (INV-8).
