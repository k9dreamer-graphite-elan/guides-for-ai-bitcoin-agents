---
name: Wrapped/Bridged-Asset Peg Monitor Runbook
type: runbook
handbook: v0.7
enforces: [INV-7, INV-10, INV-11, INV-12, INV-13]
skills: [query]
status: draft
---

# Wrapped/Bridged-Asset Peg Monitor Runbook

> Conforms to the [HODLMM Agent Handbook](../hodlmm/handbook/HODLMM-Agent-Handbook.md) **v0.7**.
> Enforces: INV-7, INV-10, INV-11, INV-12, INV-13. Feeds INV-13's peg tier + cross-protocol routing.

## Purpose
Read-only: monitor a wrapped or bridged asset's peg to its underlying using an **independent** reference,
and a cash stablecoin's peg to USD, emitting `ok | warn | break` for the safety gate and routing.

## When to run / when NOT to run
- **Run when:** every cycle for any pool holding a wrapped (e.g. sBTC↔BTC) or bridged-cash (e.g.
 USDCx↔USD) leg; before entering or sizing such a pool.
- **Do NOT run when:** no wrapped/bridged leg (a native/native pair has no peg to monitor).
- Decision reference: INV-13 (peg band is fixed, absolute — not scaled with divergence).

## Inputs
| Param | Meaning | Default |
|---|---|---|
| `asset` | wrapped/bridged asset | — |
| `underlying-ref` | **independent** wrapped-vs-underlying price (a venue that is not the pool) | — |
| `usd-ref` | **independent** cash-vs-USD price | — |
| `warn_band` / `peg_band` | soft/hard deviation bands (absolute) | `[~0.3%] / [~0.5–1%]` |

## Required Approval Scope (INV-1)
- **None.** Read-only; emits a verdict. A `break` hands to the halt path (exit runbook) under its scope.

## Gates — run BEFORE compute
```
[ ] Independent reference(s) resolved and fresh (INV-7)
[ ] Reference is NOT derived from the pool being monitored (independence)
[ ] Ledger row prepared (INV-11)
```

## Procedure (read-only)
1. **READ REFS** — `query` `underlying-ref` and/or `usd-ref`; confirm freshness (INV-7).
2. **COMPUTE** — `dev_wrapped = |wrapped/underlying − 1|`; `dev_cash = |cash/USD − 1|`.
3. **CLASSIFY** — `ok` (both < warn_band); `warn` (warn_band ≤ dev < peg_band → tighten/defensive, size
 down); `break` (dev ≥ peg_band → abnormal per INV-13: halt-and-hold, do not blind-swap).
4. **EMIT + REMEMBER** — `{asset, dev_wrapped, dev_cash, state}`; ledger + memory (INV-11/12).

## Expected outputs
```
{ asset, dev_wrapped, dev_cash, state: ok|warn|break, feeds: INV-13 peg tier }
```

## Failure handling
| Symptom | Handbook |
|---|---|
| Reference stale/unreachable | Ch.3 §3.4 — treat as warn (conservative), don't act on a bad read |
| Only one reference available | report partial; can't clear the other leg's peg — flag low confidence |
| Persistent `break` | Ch.3 §3.6 → STOP + escalate (a real depeg is not a trading opportunity here) |

## Idempotency / cooldown
- Always safe to re-run; read-only; no cooldown. Persist the deviation series.

## Notes
- **Independence is the whole point.** A reference derived from the same pool can't reveal that the pool
 itself has depegged. Use an off-pool venue for `underlying-ref` and a real USD reference for `usd-ref`.
- The peg band is **fixed and absolute** (INV-13) — a depeg is a different event from pool/feed divergence.
