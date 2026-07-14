---
name: HODLMM Pair Calibration Runbook
type: runbook
handbook: v0.7
enforces: [INV-1, INV-7, INV-9, INV-11, INV-12, INV-13]
skills: [hodlmm-risk, query]
status: draft
---

# HODLMM Pair Calibration Runbook

> Conforms to the [HODLMM Agent Handbook](../handbook/HODLMM-Agent-Handbook.md) **v0.7**.
> Enforces: INV-1, INV-7, INV-9, INV-11, INV-12, INV-13. Read-mostly; produces a pair config.

## Purpose
Pre-launch: derive and **validate** the parameter set for a new volatile/cash pair — asset profile, V-only
caps, divergence/peg thresholds, width/size floors, viability floor — enforcing the ordering invariants
before any capital is deployed.

## When to run / when NOT to run
- **Run when:** onboarding a new pair, or re-calibrating after a regime shift.
- **Do NOT run when:** you're mid-campaign and just need to act — this produces config, not trades.
- Decision reference: Ch.4 §4.4 (asymmetric inventory), INV-13 (divergence/peg), operating-guide §3.2.

## Inputs
| Param | Meaning | Default |
|---|---|---|
| `pool-id` | pool | — |
| `V`, `C` | volatile + cash legs | — |
| `underlying-ref`, `usd-ref`, `external-feed` | independent references | — |
| `T` (tolerance), `m` (stress move) | drawdown dial | `[15%] / [30%]` |
| `sigma-window` | vol window | profile |

## Required Approval Scope (INV-1)
- **None** for calibration itself (read-mostly). Hands the validated config to `hodlmm-campaign-entry`
 (which needs `add-new`) for the initial placement.

## Gates — run BEFORE emit
```
[ ] Asset profile complete: wrapped? gas-asset==V? slow-redeem path? anchor quality? (INV-13)
[ ] Independent references resolved (external, usd-ref, underlying-ref)
[ ] Ordering invariants proven: f* < f_soft < f_hard AND d_warn < d_halt
[ ] Width floor ≥ bin granularity + fee + adverse (from adverse-selection runbook)
[ ] Viability floor: expected fee ≥ expected gas at the chosen cadence
[ ] Ledger row prepared (INV-11)
```

## Procedure (read-mostly)
1. **ASSET PROFILE** — record: is V wrapped (⇒ peg halt via `underlying-ref`)? is the gas asset == V
 (⇒ exclude the gas buffer from `f`, measure runway in gas-asset units)? slow-redeem path? external
 anchor quality (weaker ⇒ widen `d_warn`, treat P&L benchmark cautiously).
2. **CAPS** — `f_hard ≈ T/m`; `f_soft = f_hard − [buffer]`; `f* = f_hard − [larger buffer]`. **Assert
 `f* < f_soft < f_hard`** — reject the set otherwise (Ch.4 §4.4).
3. **DIVERGENCE/PEG** — `d_warn = k_warn·σ`; `d_halt = max(halt_floor, k_halt·σ)` (σ from
 `hodlmm-risk`; reference reads via `query`); **assert `d_warn < d_halt`** (clamp `d_warn`). Fixed
 absolute `peg_band` for `underlying-ref`/`usd-ref` (INV-13).
4. **WIDTH/SIZE FLOORS** — from `hodlmm-adverse-selection-runbook`: width floor + the conditional
 size-floor (pull when adverse ≥ fee).
5. **VIABILITY** — confirm expected fee income ≥ expected gas at the intended cadence; set the minimum
 capital / max cadence.
6. **EMIT + REMEMBER** — the validated pair config; persist for the campaign (INV-11/12). Hand to
 `hodlmm-campaign-entry-runbook` for placement.

## Expected outputs
```
{ asset_profile, f*, f_soft, f_hard, d_warn, d_halt, peg_band, width_floor, size_floor_rule,
 viability: {min_capital, max_cadence}, invariants_ok: true }
```
- `invariants_ok = false` ⇒ **do not launch**; fix the set first.

## Failure handling
| Symptom | Handbook |
|---|---|
| Ordering invariant fails | reject config; re-derive (do not launch on an incoherent set) |
| Weak external anchor (thin/chain-correlated V) | widen `d_warn`; flag the P&L benchmark as weak |
| Missing independent reference | can't set that peg halt — flag; don't launch that leg blind |

## Idempotency / cooldown
- Always safe to re-run; read-mostly. Re-run on regime shifts; version the config.

## Notes
- This runbook is the guardrail against the two incoherence traps: inverted `f`-caps and inverted
 `d_warn`/`d_halt`. Both are refused here rather than discovered live.
- Generalizes cleanly to any volatile/cash pair — only the asset profile + refits change.
