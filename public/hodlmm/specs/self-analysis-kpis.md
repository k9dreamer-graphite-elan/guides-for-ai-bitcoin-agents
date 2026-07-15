---
name: Self-Analysis KPIs & Actor Attribution Spec
type: spec
version: 1.0
updated: 2026-07-15
handbook: v0.9
status: draft
---

# Self-Analysis KPIs & Actor Attribution Spec (v1.0)

> Conforms to the [HODLMM Agent Handbook](../handbook/HODLMM-Agent-Handbook.md) **v0.9**.
> Origin: k9dreamer 30-day retrospective + automation-vs-intelligence analysis (2026-07-15),
> adopted operator-directed. Companion to the
> [Campaign PnL Report contract](../runbooks/hodlmm-pnl-runbook.md) and the
> [closeout runbook](../runbooks/hodlmm-closeout-runbook.md).

## Purpose

Autonomous-agent improvement claims are usually vibes. This spec makes them **measurable and
comparable** — across time for one agent, and across agents, models, and capital sizes as an
operation scales. It has two parts:

1. **KPI framework (sections A–E):** what to measure, from records agents already keep.
2. **Actor attribution (section F):** every transaction and material decision records *which
   actor* — human, script, or LLM agent (with model id) — planned, decided, executed, and
   reviewed it. Without F, none of A–E are interpretable at multi-agent scale.

The organizing insight: **automation improving** means the *same* situations get handled
cheaper; **intelligence improving** means *novel* situations get handled well on first
contact. These are different KPIs with different scaling implications, and results (PnL) are
the lagging indicator — reported last, never led with.

## A. Engineering-loop health (are we learning faster?)

| KPI | Definition | Source |
|---|---|---|
| **Incident→defense time** | Elapsed time from first occurrence of a new failure class to a deployed, tested gate/runbook | journal + automation git history |
| **Tuition cost per failure class** | Real money burned before the class was gated | tx ledger + campaign accounting |
| **Recurrence rate** | Same failure class paying tuition twice after being gated (target: 0) | learnings index vs incident log |
| **Doctrine growth & adoption** | New numbered learnings per month; % merged into a shared KB | learnings files, KB PRs |

## B. Confidence / revealed trust (is the operator right to let it run?)

The honest confidence metric is **revealed operator trust** — what actually runs unattended —
not claimed trust.

| KPI | Definition | Source |
|---|---|---|
| **Unattended hours between operator interventions** | Wall-clock of autonomous operation between required human touches | monitor logs + journal |
| **Standing-authority scope** | Breadth of approved unattended actions in campaign charters | `state.json` `approval.scope` |
| **Alert precision** | % of alerts that flagged a real, actionable condition | monitor log + triage notes |
| **Remedy accuracy** | % of alert-prescribed remedies that were the *right* action on fresh reads (an alert can be correct while its prescription is stale or value-destructive) | triage entries |
| **Halt discipline** | Halts triggered / halts that were correct to trigger | monitor state + journal |

## C. Automation maturity (same situations, cheaper)

| KPI | Definition | Source |
|---|---|---|
| **Zero-LLM coverage** | % of routine decisions (scan/repair/exit) executed with no LLM or human | auto-events vs journal |
| **Gate coverage** | Layered gates in the write path, each traceable to a prior incident | monitor script |
| **Gas efficiency** | Gas spent / budget, with failed-tx fees booked honestly | accounting blocks |
| **Clean-exit rate** | Campaigns closed with direct-read proof (DLP 0), on schedule | campaign index |

## D. Intelligence / judgment (novel situations, first contact) — the scarce metric

| KPI | Definition | Source |
|---|---|---|
| **Novel-situation first-contact success** | New failure/market regime handled well with no precedent or rule | journal case studies |
| **Judgment→doctrine conversion** | % of judgment events codified into a learning/gate within 48h | learnings timestamps |
| **Override quality** | When an actor overrules the automation (either direction), were they right? Scored against realized outcome at campaign close | triage entries + closeout PnL |

Count one-time events as one data point, not a habit. Section D is where **model
comparisons** live — sections A/C mostly measure the system, not the model.

## E. Results (the lagging indicator — report last, never lead)

| KPI | Definition | Source |
|---|---|---|
| **Net vs hold after gas** | Realized, per campaign, per the PnL Report contract | closeouts |
| **Capital under unattended management** | Capital deployed with standing authority | `state.json` |
| **Edge at size** | Does % edge hold as sizing steps up? | closeout series |

## F. Actor attribution (REQUIRED on every transaction and material decision)

Every `txRoleLedger` entry, triage decision, and closeout MUST carry:

```json
"attribution": {
  "planned_by":  "<actor>",
  "decided_by":  "<actor>",
  "executed_by": "<actor>",
  "reviewed_by": "<actor>"
}
```

- `planned_by` — who designed the action (campaign plan, repair plan)
- `decided_by` — who made the go/no-go call (including decisions **not** to act)
- `executed_by` — who signed/broadcast (or `n/a (no transaction)` for hold decisions)
- `reviewed_by` — who verified the outcome (post-checks, closeout scoring)

**Actor grammar** (one of):

| Form | Meaning | Example |
|---|---|---|
| `operator` | Human decision/execution | `operator` |
| `script:<name>@<version-or-commit>` | Zero-LLM automation | `script:hodlmm-campaign-monitor.sh@2026-07-14` |
| `agent:<agent-name>/<model-id>` | LLM agent — **model id required** | `agent:k9dreamer/claude-fable-5` |
| `unrecorded(pre-convention)` | Honest backfill for pre-adoption actions; never for new actions | `agent:k9dreamer/unrecorded(pre-convention)` |

Rules:

1. **Model id is mandatory** for agent actors. "The agent did it" is not attribution when
   sessions run on different models; per-model KPIs (section D) depend on it.
2. **Decisions not to act are attributed too.** A hold decision goes in a `decisionLedger`
   entry with full attribution and a `score_at_closeout` field.
3. Composite actions list multiple actors (e.g. `decided_by: operator`,
   `executed_by: agent:…`).
4. Section D KPIs are computed **per actor**; section B authority is granted **per actor**,
   not per system.
5. Closeouts MUST include an attribution table: every tx and every material decision →
   planned/decided/executed/reviewed actors.

## Scaling rules (multi-agent / multi-model / more capital)

1. **Per-agent scorecard:** every agent/model reports these same KPIs — comparability is the
   point. A new agent starts at section C zero (no inherited trust); doctrine (section A
   artifacts) transfers, **authority (section B) does not**.
2. **Authority follows metrics, not tenure:** expand `approval.scope` and capital only when
   section B rows support it (interventions trending down, remedy accuracy high, halts
   correct).
3. **Model comparisons live in section D:** A/B different models on novel-situation handling
   and override quality.
4. **Capital step-ups gated on section E:** next sizing increase requires clean-exit rate
   intact AND edge-at-size not degrading over ≥2 campaigns at current size.
5. **Closeout hook:** every closeout reports at minimum: tuition paid, gates added,
   unattended %, override quality, net vs hold, and the section F attribution table.

## Reporting cadence

- **Per campaign closeout:** sections C + E rows, any A/D events, and the F attribution table.
- **Monthly retro:** full framework; the "why the rating isn't higher" section must cite the
  weakest rows.
- **Before any authority/capital expansion:** section B snapshot in the approval request.

## Worked example (k9dreamer, 2026-06-14 → 2026-07-15)

One agent's first month under this lens, illustrating each section:

- **A:** u5001 abort class went from "mystery → automation disabled" (June) to same-day
  classify/recover/gate/test/deploy (2026-07-14) — ~10× incident→defense compression.
  Tuition trend per failure class: 0.25 STX → 0.35 STX → $0 (prevented).
- **B:** supervised-everything → dual concurrent campaigns fully unattended with standing
  auto-exit authority. First **remedy accuracy** case: a geometry-gate alert correctly
  fired, but fresh reads showed its prescribed withdraw/swap/redeposit had gone stale and
  would have realized a round-trip loss — the right action was HOLD.
- **C:** ~10 layered gates, each born from a specific incident; 4/4 clean exits.
- **D:** three judgment data points in one week (structural-vs-transient slippage diagnosis,
  same-day failure classification, economics-based override of the system's own alert) —
  a trend, not a trait. Override scored at closeout.
- **E:** net vs hold after gas: −$1.25 → +$6.31 (+13%) → +$9.0 (+18%); edge at size
  unproven — the open question gating the next capital step-up.
