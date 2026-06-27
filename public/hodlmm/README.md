# HODLMM — Agent Guides

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
mechanics. Versioned (currently **v0.6**). Plus onboarding notes, security policy, contributing, license.

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
| [`hodlmm-exit-runbook.md`](./runbooks/hodlmm-exit-runbook.md) | Exit / stale-pool recovery — withdraw a position and stand down. | draft |
| [`hodlmm-campaign-entry-runbook.md`](./runbooks/hodlmm-campaign-entry-runbook.md) | Select a pool, grant scope, place the initial LP position. | draft |
| [`hodlmm-recenter-runbook.md`](./runbooks/hodlmm-recenter-runbook.md) | The atomic recenter procedure (move drifted bins around active). | draft |
| [`hodlmm-inventory-balancing-runbook.md`](./runbooks/hodlmm-inventory-balancing-runbook.md) | Restore target token ratio via corrective swap + redeploy. | draft |
| [`hodlmm-pnl-runbook.md`](./runbooks/hodlmm-pnl-runbook.md) | End-of-campaign PnL accounting — earned fees vs IL vs DLP m2m (read-only, INV-8). | draft |
| [`hodlmm-closeout-runbook.md`](./runbooks/hodlmm-closeout-runbook.md) | Post-campaign: assemble + submit the standardized Campaign Closeout issue (the learning loop). | draft |

Authoring or updating a runbook? Read [`runbooks/AGENT-AUTHORING-GUIDE.md`](./runbooks/AGENT-AUTHORING-GUIDE.md) first, then copy [`runbooks/_TEMPLATE-runbook.md`](./runbooks/_TEMPLATE-runbook.md).

### Knowledge base (distilled campaign memory)

[`knowledge/`](./knowledge/) — the cross-campaign distillation of accepted Campaign Closeout issues:
per-pool playbooks ([`pools/`](./knowledge/pools/)) and a lessons & failure-pattern catalog
([`lessons/lessons-catalog.md`](./knowledge/lessons/lessons-catalog.md)). **Read it before launching on
a pool.** It is **maintainer-written / agent-read** — agents contribute by submitting a closeout issue,
never by editing the KB. Maintenance is governed by [`knowledge/KB-MAINTAINER-GUIDE.md`](./knowledge/KB-MAINTAINER-GUIDE.md).

## Conventions

- Filenames: `hodlmm-<operation>-runbook.md`, lowercase-hyphen, **one operation per file**.
- Every runbook's frontmatter declares `handbook:` version + `enforces:` (the `INV-` IDs) + `skills:`.
- No mutable live state in any doc (pool lists, TVL, APR, fee rates are queried live).
- Knowledge-base pages **cite** issues by URL and the handbook by `INV-` ID — they never restate
  handbook constants, and never report a DLP/display mark as realized profit (INV-8).
