---
name: HODLMM Divergence & Feed-Safety Runbook
type: runbook
handbook: v0.7
enforces: [INV-7, INV-9, INV-10, INV-11, INV-12, INV-13]
skills: [hodlmm-bin-guardian, hodlmm-risk, query]
status: draft
---

# HODLMM Divergence & Feed-Safety Runbook

> Conforms to the [HODLMM Agent Handbook](../handbook/HODLMM-Agent-Handbook.md) **v0.7**.
> Enforces: INV-7, INV-9, INV-10, INV-11, INV-12, INV-13.
> This runbook is the procedure for **INV-13** (divergence & feed-safety tiering).

## Purpose
Read-only: classify the pool's price-divergence and feed health into a safety tier (aligned / defensive /
abnormal), disambiguate a lagging feed from a genuinely decoupled pool, and emit the gating verdict every
write runbook checks before it acts (or that triggers a halt).

## When to run / when NOT to run
- **Run when:** every monitoring cycle, and as the gate immediately before any write.
- **Do NOT run when:** never skip it before a write. Read-only and always safe.
- Decision reference: INV-13; §1.4 (freshness/lag check).

## Inputs
| Param | Meaning | Default |
|---|---|---|
| `wallet` | context address (not signed) | — |
| `pool-id` | pool to assess | — |
| `external-feed` | independent V/USD reference | — |
| `usd-ref` | **independent** cash-vs-USD reference | — |
| `underlying-ref` | **independent** wrapped-vs-underlying reference | — |
| `k_warn` | `d_warn = k_warn · σ` | `[2]` |
| `d_halt` | `max(halt_floor, k_halt · σ)` | `halt_floor [~1–2%]`, `k_halt [3]` |
| `peg_band` | fixed absolute depeg band (cash + wrapped) | `[~0.5–1%]` |
| `feed_max_age` | stale → force defensive | `[90s]` |
| `feed_halt_age` | staleness → halt | `[~5 min]` |

## Required Approval Scope (INV-1)
- **None.** Read-only; emits a verdict. Recommended actions execute in write runbooks under their own
 scope; a halt hands off to `hodlmm-exit-runbook` (`withdraw`).

## Gates — run BEFORE compute
```
[ ] Fresh scan; indexer lag checked (INV-7, §1.4)
[ ] All three references resolved (INV-13)
[ ] Ordering invariant d_warn < d_halt holds (clamp if not)(INV-13)
[ ] No signer touched — read-only
[ ] Ledger row prepared (INV-11)
```

## Procedure (read-only — no confirm, no broadcast)
1. **READ STATE** — `hodlmm-bin-guardian run --pool <pool-id>` + `query`: active-bin `p`, composition of
 the active bin + neighbours (liquid or thin/empty?), indexer-lag signal (§1.4); `hodlmm-risk` for σ.
 Read `p` from on-chain/bin state, not a cached quote (INV-7).
2. **READ REFERENCES** — `query` external V/USD, `usd-ref`, `underlying-ref`; set `feed=stale`/`lost` by
 age.
3. **COMPUTE** — `d`, `d_warn = k_warn·σ`, `d_halt = max(halt_floor, k_halt·σ)`; clamp `d_warn < d_halt`.
4. **PEG CHECK (separate)** — cash depeg `|usd-ref − 1| > peg_band`; wrapped depeg via `underlying-ref`.
 Abnormal regardless of `d`.
5. **DISAMBIGUATE lag vs decoupling** — high `|d|` + high σ + stale feed + coherent bin advance ⇒ lag ⇒
 defensive; high `|d|` + fresh feed, or thin/empty active bin ⇒ decoupled/manipulation ⇒ halt.
6. **CLASSIFY TIER** — aligned / defensive (max width, min size; mark inventory at external) / abnormal
 (halt: broken-market ⇒ hold inventory, no blind-swap; operational ⇒ withdraw + stop). Per INV-13.
7. **EMIT + REMEMBER** — `{tier, feed, d, d_warn, d_halt, peg_ok, mark_basis, directive}`; ledger + memory
 (INV-11/12).

## Expected outputs
```
{ tier: aligned|defensive|abnormal, feed: fresh|stale|lost, d, d_warn, d_halt, peg_ok,
 mark_basis: active_bin|external, directive: proceed|force-defensive|halt-hold|halt-operational }
```

## Failure handling
| Symptom | Handbook |
|---|---|
| Reference feed stale/unreachable | Ch.3 §3.4 (force defensive, don't act) |
| `p` looks wrong (lag) | Ch.3 §3.4 (re-read after lag) |
| Abnormal but maybe a bad read | Ch.3 §3.6 (verify 2nd source before halting a healthy book) |
| Repeated abnormal cycling | Ch.3 §3.6 → STOP + escalate (possible manipulation) |

## Idempotency / cooldown
- Always safe to re-run; read-only; no cooldown. Persist the tier series (flapping is a signal). Never let
 an assessment broadcast directly — it emits a directive; the write runbook owns the tx + its GATE.

## Notes
- Two halt thresholds by design: divergence halt scales with σ; peg band is fixed. `d_warn < d_halt` is
 load-bearing. A cash/wrapped depeg cannot be seen from V/USD alone — hence the two independent refs.
