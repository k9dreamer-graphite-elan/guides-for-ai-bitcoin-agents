---
name: HODLMM <Operation> Runbook
type: runbook
handbook: v0.6                  # the doctrine version this runbook conforms to
enforces: [INV-1, INV-2, INV-3, INV-6, INV-7, INV-9, INV-10, INV-11]   # the invariants it guarantees
skills: [hodlmm-move-liquidity, nonce-manager]                          # approved skills it calls
status: draft                   # draft | active | deprecated
---

<!--
  HOW TO USE THIS TEMPLATE
  - Copy to `hodlmm-<operation>-runbook.md` (lowercase-hyphen, ONE operation per file).
  - A runbook is EXECUTABLE: an agent should be able to follow it step-by-step.
  - IMPORT the handbook — cite invariants by ID (INV-3), never restate its constants.
  - Keep mutable live state OUT (pool lists, TVL, APR, fee rates are queried live).
  - Delete these comments before publishing.
-->

# HODLMM <Operation> Runbook

> Conforms to the [HODLMM Agent Handbook](../handbook/HODLMM-Agent-Handbook.md) **v0.6**.
> Enforces: INV-1, INV-2, INV-3, INV-6, INV-7, INV-9, INV-10, INV-11.

## Purpose

One sentence: the single repeatable operation this runbook executes.

## When to run / when NOT to run

- **Run when:** <the trigger / precondition>.
- **Do NOT run when:** <disqualifying conditions — e.g. pool is stale (exit instead, INV-9); scope expired (INV-1)>.
- Decision reference: <link the relevant handbook decision tree, e.g. Ch.2 Playbook C>.

## Inputs

| Param | Meaning | Default |
|---|---|---|
| `wallet` | signing address | — |
| `pool-id` | target pool | — |
| `<threshold>` | <e.g. drift threshold in bins> | <e.g. 3> |
| `<cap>` | <e.g. spread / max size> | <…> |

## Required Approval Scope (INV-1)

- Permissions needed: `<manage-existing | add-new | withdraw | swap>`.
- Caps this runbook respects: `<spread ≤ …, size ≤ …, target ratio …>`.
- If scope is missing/expired → **read-only**, request approval. Do not infer authority.

## Gates — run BEFORE execute

The applicable subset of the handbook pre-flight GATE (link, don't restate):

```
[ ] Active scope covers this pool + action            (INV-1)
[ ] Fresh scan this iteration; plan re-simulated       (INV-7)
[ ] Pool liveness OK (else exit, not act)              (INV-9)
[ ] Swap path bounded: *-simple-range-multi, ≤230      (INV-3)   # if this op swaps
[ ] Correct fund-protection set                        (INV-2)   # Deny PCs (swap) OR min-dlp/fee-cap/deviation (LP)
[ ] Nonce serialized; RBF path known                   (INV-6)
[ ] Ledger entry prepared                              (INV-11)
```

## Procedure

Each step is a skill/command with an expected output. **Dry-run before any broadcast.**

1. **SCAN** — `<skill> scan …` → expected: `<state, drift, active bin>`.
2. **DECIDE** — apply `<decision tree>` → `<go | hold | exit>`.
3. **DRY-RUN** — `<skill> run … ` *(no confirm token)* → preview the plan; verify it matches intent (INV-7).
4. **EXECUTE** — `<skill> run … --confirm[=WORD]` → broadcasts (INV-2/3/6). Signer unlocked via env, never argv.
5. **VERIFY** — re-scan; confirm mined `success` and the resulting state (INV-10).
6. **REMEMBER** — write both ledgers + memory (INV-11/12).

## Expected outputs

- Success shape: `<the JSON / fields the skill returns on success>`.
- On-chain: `<txid(s)>`, new `<range / ratio / position>`.
- A `blocked` status (cooldown / confirmation / gate) is **expected**, not an error.

## Failure handling

Map each failure to **Handbook Chapter 3** (don't restate the recovery):

| Symptom | Handbook |
|---|---|
| Stuck `pending` / nonce stalled | Ch.3 §3.2 (RBF unstick) |
| Partial fill | Ch.3 §3.3 (residual) |
| Stale quote / lagging positions | Ch.3 §3.4 |
| `blocked` (cooldown/confirm/deviation) | Ch.3 §3.5 |
| Repeated failure / fund-risk / key exposure | Ch.3 §3.6 → STOP + escalate |

## Idempotency / cooldown

- Safe to re-run? `<yes/no>`. Cooldown window: `<e.g. 4h per pool>`. State file: `<path>`.
- Never re-send an original-size action to "fix" a partial — risks double execution.

## Notes

<Anything operation-specific: edge cases, known constraints, links to the relevant skill's SKILL.md.>
