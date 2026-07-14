---
name: HODLMM Stuck-Transaction Runbook
type: runbook
handbook: v0.7
enforces: [INV-1, INV-2, INV-3, INV-6, INV-7, INV-10, INV-11, INV-12]
skills: [nonce-manager, bitflow, hodlmm-move-liquidity, query]
status: draft
---

# HODLMM Stuck-Transaction Runbook

> Conforms to the [HODLMM Agent Handbook](../handbook/HODLMM-Agent-Handbook.md) **v0.7**.
> Enforces: INV-1, INV-2, INV-3, INV-6, INV-7, INV-10, INV-11, INV-12.
> This runbook is the procedure for **Ch.3 §3.7** (stuck-tx root-cause discrimination).

## Purpose
Triage a HODLMM transaction that is stuck `pending`, reverted, or partially filled to its **root cause**,
and apply the correct recovery — the three causes need three different fixes and are easy to conflate.

## When to run / when NOT to run
- **Run when:** a broadcast hasn't mined within the watchdog, reverted, or partially filled; or the head
 nonce is blocking later txs.
- **Do NOT run when:** the tx simply hasn't been read back yet (indexing lag, Ch.3 §3.4).
- Decision reference: Ch.3 §3.7 (root-cause), §3.2 (stuck nonce), §3.3 (partial), R1/R2, §3.6 (escalate).

## Inputs
| Param | Meaning | Default |
|---|---|---|
| `wallet` | signing address | — |
| `pool-id` | pool targeted | — |
| `stuck-txid` / `nonce` | the tx + nonce | — |
| `original-intent` | swap/add/recenter/withdraw + its scope | — |
| `fee-bump-step` | RBF bump per attempt | `[+25%]` |
| `max-recovery-attempts` | before escalation | `[3]` |
| `per-cycle-gas-cap` | gas ceiling for one recovery cycle | scope/profile |

## Required Approval Scope (INV-1)
- Recovery acts **within the original action's scope**. A replacement swap needs `swap`; a replacement LP
 op needs the original LP permission. The cancel primitive (1 µSTX transfer to a fixed external address at the stuck nonce — never
 self-addressed; handbook §3.2) is a
 wallet op — clears the signer, grants no new authority. Expired scope ⇒ read-only; escalate.

## Gates — run BEFORE execute
```
[ ] Confirmed genuinely stuck (not indexer lag) (INV-7, §3.4)
[ ] Original scope still covers the recovery (INV-1)
[ ] Root cause identified before any resend (§3.7)
[ ] Replacement swap bounded: ≤230, real min-out (INV-3)
[ ] Correct fund-protection (Deny PCs swap / Allow+bounds LP) (INV-2)
[ ] Nonce serialized; per-cycle gas cap not exceeded (INV-6)
[ ] Ledger row prepared (INV-11)
```

## Procedure (dry-run any replacement first)
1. **CONFIRM STUCK** — `query` tx + mempool + head nonce; rule out indexer lag (§3.4).
2. **DIAGNOSE** — apply the Ch.3 §3.7 root-cause table (underpriced → RBF; oversized/read-ceiling →
 replace bounded, **not** a fee bump; adversarial revert → refresh/retry-once/escalate; `u5001` →
 withdraw→swap→redeposit; partial → residual).
3. **CLEAR HEAD NONCE FIRST** — if the stuck tx is the head nonce, unstick it before anything else (§3.2 /
 R2); serialize via `nonce-manager` (INV-6).
4. **APPLY FIX** — bounded replacement swap via `bitflow` (Deny PCs + real min-out, INV-2/3) or LP op
 via `hodlmm-move-liquidity` (Allow + bounds). Signer via env, never argv.
5. **VERIFY** — replacement mined `success`, head nonce advanced, re-scan position/ratio (INV-10). Partial
 fill is expected.
6. **REMEMBER** — log cause, fix, gas, outcome to both ledgers + memory (INV-11/12).

## Expected outputs
- Head nonce advanced / signer unblocked; action completed (possibly via bounded replacement + residual)
 or cleanly cancelled with a recorded blocker. `{root_cause, action_taken, replacement_txid, gas,
 residual_handled, outcome}`. A recorded blocker + escalation is a valid terminal outcome.

## Failure handling
| Symptom | Handbook |
|---|---|
| RBF still not mining after a bump | §3.7 → if oversized, stop bumping; replace the payload (R1) |
| Replacement partial fill | §3.3 (residual — never resend original size) |
| Repeated reverts (adversarial) | §3.6 → widen/chunk/private/escalate; don't loop |
| Custody won't expose RBF | §3.2 → out-of-band cancel with the key, or wait out the mempool |
| Per-cycle gas cap hit mid-recovery | STOP, record blocker (active-LP addendum) |
| Suspected fund-risk / key exposure | §3.6 → STOP + escalate |

## Idempotency / cooldown
- One tx per (account, nonce) can ever confirm — same-nonce RBF/replace can't double-execute (INV-6).
 **Never** resubmit at a *new* nonce. Track the nonce explicitly; don't rely on mempool timeouts.
 Read-only triage is always safe; recovery broadcasts are gated by the per-cycle gas cap + attempts.

## Notes
- The mistake this runbook prevents: bumping the fee on an oversized/read-ceiling tx. RBF only cures
 underpricing (§3.7). Prevention beats recovery: bounded swaps + serialized nonces up front.
