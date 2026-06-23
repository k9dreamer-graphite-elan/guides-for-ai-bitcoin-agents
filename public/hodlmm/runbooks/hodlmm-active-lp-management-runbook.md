---
name: HODLMM Active LP Management Runbook
type: runbook
handbook: v0.6
enforces: [INV-1, INV-2, INV-6, INV-7, INV-9, INV-10, INV-11, INV-12]
skills: [hodlmm-move-liquidity, hodlmm-bin-guardian]
status: active
---

# HODLMM Active LP Management Runbook

> Conforms to the [HODLMM Agent Handbook](../handbook/HODLMM-Agent-Handbook.md) **v0.6**.
> Enforces: INV-1, INV-2, INV-6, INV-7, INV-9, INV-10, INV-11, INV-12.
>
> Author: @k9dreamer_btc

## Purpose

Recenter an existing HODLMM LP position near the active bin when live drift exceeds the operator-approved threshold.

## When to run / when NOT to run

- **Run when:** a fresh read-only scan shows an existing in-scope position has drifted outside its approved active-management band.
- **Do NOT run when:** approval scope is missing or expired, the pool is stale, the position is already inside the approved band, the operation would add new capital, or the command would touch any pool outside scope.
- Decision reference: use the operating guide's active-management profile, then apply the handbook Chapter 0 pre-flight GATE.

## Inputs

| Param | Meaning | Default |
|---|---|---|
| `wallet` | signing address that owns the LP position | - |
| `pool-id` | target HODLMM pool ID | - |
| `range-percent` | target recenter width requested by the operator or strategy profile | approval scope |
| `drift-threshold` | minimum drift that allows a recenter decision | approval scope |
| `state-file` | campaign or operation state used for counters/cooldowns | operation-specific |
| `check-interval` | read-only monitor cadence for active campaigns | ~2h |

## Required Approval Scope (INV-1)

- Permissions needed: `manage-existing` for the exact `pool-id`.
- Caps this runbook respects: pool allowlist, duration, recenter count, gas budget, range/deviation limits, cooldown policy, and any explicit "no swap" / "no add-new" constraints.
- If scope is missing, expired, ambiguous, or narrower than the proposed action -> **read-only**, request approval. Do not infer authority.

## Gates (Ch.0 pre-flight subset)

The applicable subset of the handbook pre-flight GATE:

```
[ ] Active scope covers this pool + manage-existing action (INV-1)
[ ] Fresh scan this iteration; plan re-simulated        (INV-7)
[ ] Pool liveness OK; stale pool exits instead          (INV-9)
[ ] LP fund-protection bounds present                   (INV-2)
[ ] Nonce serialized; RBF path known                    (INV-6)
[ ] Ledger entry prepared                               (INV-11)
```

## Procedure

Each step is a skill/command with an expected output. Dry-run before any broadcast.

1. **SCAN** - run:

   ```bash
   hodlmm-move-liquidity scan --wallet <wallet>
   hodlmm-bin-guardian run --wallet <wallet> --pool-id <pool-id>
   ```

   Expected: current HODLMM positions, target `pool-id`, active bin, user bins, drift, DLP identity, pool health fields, and a read-only hold/rebalance/check recommendation.

2. **DECIDE** - compare the scan to the active approval scope.

   Expected: one of `hold`, `recenter`, `exit-candidate`, or `approval-required`. If the pool is stale, stop this runbook and use an exit runbook path instead.

3. **DRY-RUN** - run without a confirm token:

   ```bash
   hodlmm-move-liquidity run --wallet <wallet> --pool <pool-id> --range-percent <range-percent>
   ```

   Expected: a non-broadcast plan with decision, target range, cooldown state, projected bounds, and any blocked reason.

4. **EXECUTE** - only when the dry-run says a recenter is needed and every gate passes:

   ```bash
   hodlmm-move-liquidity run --wallet <wallet> --pool <pool-id> --range-percent <range-percent> --confirm
   ```

   Expected: one signed transaction for the in-scope pool. Signer unlock material must come from the execution environment, never command-line arguments.

5. **VERIFY** - confirm on-chain status, then re-scan the same pool.

   Expected: mined `success`, current bins/range reflect the intended move, and no out-of-scope pool changed.

6. **REMEMBER** - update transaction and performance ledgers.

   Expected: transaction receipt, pre/post state, approval scope, gas, current exposure, DLP/bin state, drift, pool economics, mark-to-market, fee-attribution confidence, and lesson learned.

## Expected outputs

- Success shape: txid, pool ID, old range, new range, active bin at signing, post-confirm active bin, post-confirm user bins, and ledger paths.
- Blocked shape: `blocked` with reason such as cooldown, no active scope, no move needed, stale pool, failed liveness, or failed bounds.
- A `blocked` status is an expected safety result, not an error.

## Failure handling

Map each failure to Handbook Chapter 3:

| Symptom | Handbook |
|---|---|
| Stuck `pending` / nonce stalled | Ch.3 §3.2 (RBF unstick) |
| Partial or unexpected state | Ch.3 §3.3 (residual / post-state mismatch) |
| Stale quote / lagging positions | Ch.3 §3.4 |
| `blocked` cooldown / confirmation / deviation | Ch.3 §3.5 |
| Repeated failure / fund-risk / key exposure | Ch.3 §3.6 -> STOP + escalate |

## Idempotency/cooldown

- Safe to re-run read-only scan and dry-run steps.
- Read-only checks may run more frequently than the write cooldown; a normal active campaign checks about every 2h while respecting the handbook's skill-enforced 4h per-pool move cooldown.
- Do not re-submit the execute step unless the current scope, cooldown, nonce state, and fresh dry-run all still authorize it.
- Never resend an original-size action to "fix" a partial or ambiguous result; re-scan and derive a new plan.

## Notes

- This runbook manages existing liquidity only. Deposits, withdrawals, swaps, inventory balancing, and campaign entry/exit belong in separate runbooks.
- Public docs must cite handbook invariants by ID and query live pool state at runtime. Do not hardcode pool lists, TVL, APR, active bin, fee rates, contract constants, or private operational details here.

## Field-confirmed addendum — HODLMM-DLMM6-20260602-001

> Source: K9Dreamer `dlmm_6` closeout (issues #4/#5).

**Gas cap per recovery cycle, not just per campaign.** Maintain two caps: a per-campaign total
budget and a per-recovery-cycle cap. If a single repair/recover cycle would exceed the per-cycle
cap, stop and record a blocker instead of retrying. Field note: a `1.25 STX` per-campaign cap
would have been drained mid-run; the per-cycle cap is what protects the envelope from one failing
loop. (This campaign raised the campaign cap to `4.00 STX` at renewal.)

**"Sit and wait" is bounded, not passive hold.** Holding an out-of-range position with zero gas
is acceptable **only** while a repair design is genuinely uncertain and the bin is plausibly
returning to range. Record it as `pause_with_blocker` with an explicit watch condition — never as
ordinary `hold`. Field note: out-of-range holds earned fees on natural bin return at zero gas, but
an unbounded sit is just an unmanaged out-of-range LP.
