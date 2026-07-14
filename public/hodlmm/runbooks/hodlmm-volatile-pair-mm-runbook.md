---
name: HODLMM Volatile-Pair Market-Making Runbook
type: runbook
handbook: v0.7
enforces: [INV-1, INV-2, INV-3, INV-6, INV-7, INV-9, INV-10, INV-11, INV-12, INV-13]
skills: [hodlmm-bin-guardian, hodlmm-risk, hodlmm-flow, query]
status: draft
---

# HODLMM Volatile-Pair Market-Making Runbook

> Conforms to the [HODLMM Agent Handbook](../handbook/HODLMM-Agent-Handbook.md) **v0.7**.
> Enforces: INV-1, INV-2, INV-3, INV-6, INV-7, INV-9, INV-10, INV-11, INV-12, INV-13.
> Strategy: operating-guide "Volatile major/cash pair" profile (§3.2); doctrine Ch.4 §4.4 + INV-13.

## Purpose
Run **one management cycle** for a volatile-major/cash pair (e.g. sBTC/USDCx): read state, clear the
divergence gate, set the four knobs, apply the V-only risk cap, and dispatch the on-chain operation
(recenter / rebalance / hold / exit) to the matching runbook.

## When to run / when NOT to run
- **Run when:** managing a volatile/cash position on the profile's cadence.
- **Do NOT run when:** the pair is not volatile/cash (use the standard profiles); scope missing/expired
 (read-only, INV-1); INV-13 tier is abnormal (halt — hand to exit).
- Decision reference: operating-guide §3.2; Ch.4 §4.4; INV-13.

## Inputs
| Param | Meaning | Default |
|---|---|---|
| `wallet` / `pool-id` | position + pool | — |
| `f*`, `f_soft`, `f_hard` | V-only cap set (from calibration) | profile |
| `sigma-window` | vol window for σ | profile |
| `drift-threshold` | recenter trigger | profile |

## Required Approval Scope (INV-1)
- `manage-existing` (recenter); `swap` **only** if a hard-cap corrective swap may fire. No `add-new`
 unless the scope grants it. Missing/expired ⇒ read-only.

## Gates — run BEFORE execute
```
[ ] Divergence/feed tier = aligned (or defensive applied); not abnormal (INV-13)
[ ] Flow check: lpSafety \!= avoid; toxicity acceptable (Ch.4)
[ ] Fresh scan; plan re-simulated (INV-7)
[ ] Pool healthy (else exit) (INV-9)
[ ] Swap (if any) bounded ≤230 + Deny PCs; LP op Allow+bounds (INV-2/3)
[ ] Nonce serialized (INV-6)
[ ] Ledger row prepared (INV-11)
```

## Procedure (dry-run before any broadcast)
1. **SCAN** — `hodlmm-bin-guardian` + `query`: active bin `p`, per-bin position, `f` (V share, excl. gas
 buffer), gas runway. `hodlmm-risk` → σ/regime; `hodlmm-flow` → toxicity/lpSafety/directionBias.
2. **GATE** — run `hodlmm-divergence-safety-runbook`. `abnormal` ⇒ halt → exit runbook, stop. `defensive`
 ⇒ force max-width/min-size and mark `f` at external. `crisis` regime or `lpSafety: avoid` ⇒ stand aside.
3. **RISK CAP** — if `f ≥ f_hard` and tier aligned/healthy ⇒ dispatch `hodlmm-inventory-balancing-runbook`
 (asymmetric addendum: V→C to `f_soft`, hysteresis). If `f ≥ f_soft` ⇒ saturate skew to V-sell (passive,
 no swap). If `f < f*` ⇒ bid-lean, deploy more C as bids; **never market-buy V**.
4. **KNOBS** — center on `p`; skew from `f`; width = f(σ, flow lifespan), floored per the adverse-selection
 estimate (`hodlmm-adverse-selection-runbook`); size = f(σ), conditional floor (pull when adverse ≥ fee).
5. **RECENTER** — if drift ≥ threshold and pool healthy ⇒ dispatch `hodlmm-recenter-runbook` (u5001
 fallback applies). Else hold.
6. **VERIFY + REMEMBER** — re-scan; mined `success`; separate DLP m2m from earned fees (INV-8); both
 ledgers (INV-11/12).

## Expected outputs
- At most one dispatched operation (recenter | rebalance | exit) or `hold`; `{tier, f, action, txid?}`.
- `blocked` (cooldown/deviation/gate) is expected, not an error.

## Failure handling
| Symptom | Handbook |
|---|---|
| Stuck / reverted / partial tx | `hodlmm-stuck-transaction-runbook` (Ch.3 §3.7) |
| Native move `u5001` | recenter runbook addendum (withdraw→swap→redeposit) |
| Divergence abnormal mid-cycle | INV-13 halt → exit; do not deploy |
| Repeated failure / fund-risk | Ch.3 §3.6 → STOP + escalate |

## Idempotency / cooldown
- Honors the sub-runbooks' cooldowns (recenter/balancer). One operation per cycle; never stack a deploy on
 an unconfirmed corrective swap — re-read next cycle (INV-6/10).

## Notes
- This runbook decides *which* operation; the on-chain mechanics live in the recenter / inventory-balancing
 / exit runbooks. It never invents a new on-chain path.
- The V-only cap and "no lower bound on `f`" are the whole point — see Ch.4 §4.4 and the profile.
