---
name: HODLMM Adverse-Selection & Width-Floor Runbook
type: runbook
handbook: v0.7
enforces: [INV-7, INV-11, INV-12]
skills: [hodlmm-risk, hodlmm-flow, query]
status: draft
---

# HODLMM Adverse-Selection & Width-Floor Runbook

> Conforms to the [HODLMM Agent Handbook](../handbook/HODLMM-Agent-Handbook.md) **v0.7**.
> Enforces: INV-7, INV-11, INV-12. Read-only; feeds the width/size knobs (operating-guide §3.2).

## Purpose
Read-only: estimate the expected **adverse-selection cost** per unit of provided liquidity and the
resulting **breakeven width floor**, so a position is only placed where expected fees exceed expected
adverse cost + gas.

## When to run / when NOT to run
- **Run when:** sizing/placing or re-widening any position, especially on a volatile pair.
- **Do NOT run when:** you need a *realized* PnL number — that's `hodlmm-pnl-runbook` (§6.2/§6.6). This
 estimates a *forward* cost.
- Decision reference: handbook §6.6 (IL is the realized form of this) + Ch.4 §4.2 (width vs adverse
 selection).

## Inputs
| Param | Meaning | Default |
|---|---|---|
| `pool-id` | pool | — |
| `sigma` | short-horizon realized vol (per reprice interval) | `hodlmm-risk` |
| `fee` | **live** pool fee for the direction | queried |
| `bin-granularity` | pool's per-bin price step | queried |
| `gas-per-fill` | amortized gas per reposition | measured |
| `k_adv` | tuning constant for the proxy | `[1.0]` (calibrate empirically) |

## Required Approval Scope (INV-1)
- **None.** Read-only estimate; no signer, no broadcast.

## Gates — run BEFORE compute
```
[ ] Fresh σ, live fee, bin granularity (INV-7)
[ ] k_adv calibrated from recent fills if available (else flagged as prior)
[ ] Ledger row prepared (INV-11)
```

## Procedure (read-only — rough proxy, calibrate empirically)
1. **READ** — σ (per reprice interval) from `hodlmm-risk`; live `fee` / `bin-granularity` /
 recent `gas-per-fill` via `query`; `hodlmm-flow` toxicity/velocity (scales the estimate up when flow is informed).
2. **ESTIMATE ADVERSE COST** — a workable proxy: **expected adverse cost per fill ≈ `k_adv · σ`**
 (the price tends to move ~σ against a resting quote between reprices; concentration and toxicity
 raise it). This is an **approximation** — treat `k_adv` as empirical, refit it from realized
 fill-vs-mid slippage. Relate to handbook §6.3's IL proxy: that estimates realized divergence; this
 estimates the *flow cost* that produces it.
3. **BREAKEVEN WIDTH FLOOR** — `width_floor = max(bin-granularity, expected_adverse + fee_breakeven + gas)`
 where a fill is only profitable if `fee ≥ expected_adverse`. If `fee < expected_adverse` at any
 feasible width ⇒ **pull** (size floor → 0), do not just widen.
4. **EMIT + REMEMBER** — `{expected_adverse, width_floor, pull_signal, k_adv, confidence}`; persist the
 series to refit `k_adv` (INV-11/12).

## Expected outputs
```
{ expected_adverse, fee, width_floor, pull_signal: bool, k_adv, confidence }
```
- `pull_signal = true` ⇒ expected adverse cost exceeds the fee at the floor width — stand aside.

## Failure handling
| Symptom | Handbook |
|---|---|
| σ or fee stale | Ch.3 §3.4 — widen conservatively / flag low confidence |
| No fill history to calibrate `k_adv` | report as a prior, low confidence — don't present as measured |

## Idempotency / cooldown
- Always safe to re-run; read-only; no cooldown. Each run refines `k_adv` from new fills.

## Notes
- This is a **decision aid, not a truth** — a rough proxy that must be calibrated on live fills. Its job
 is to keep width/size honest against adverse selection, which realized volatility alone misses.
- Feeds the operating-guide §3.2 knobs and the `hodlmm-volatile-pair-mm-runbook`.
