---
name: HODLMM Exit Runbook
type: runbook
handbook: v0.6
enforces: [INV-1, INV-2, INV-3, INV-6, INV-7, INV-9, INV-10, INV-11, INV-12]
skills: [hodlmm-move-liquidity, bitflow-hodlmm-withdraw, bitflow-swap-aggregator, nonce-manager]
status: draft
---

# HODLMM Exit Runbook

> Conforms to the [HODLMM Agent Handbook](../handbook/HODLMM-Agent-Handbook.md) **v0.6**.
> Enforces: INV-1, INV-2, INV-3, INV-6, INV-7, INV-9, INV-10, INV-11, INV-12.

## Purpose

Fully withdraw a wallet's liquidity from a HODLMM pool and stand the position down — used for
**stale-pool recovery**, **campaign end**, or an **operator-ordered / emergency exit**.

## When to run / when NOT to run

- **Run when:**
  - the pool is **stale** — no meaningful 24h volume, fees not generating, active bin not moving — and
    a position has drifted out of range (a stale pool is an **exit** candidate, not a rebalance one — INV-9);
  - the operator orders an exit, the campaign has ended, or an emergency exit is required.
- **Do NOT run when:** the pool is healthy and you intend to keep providing — **recenter instead**
  (see the [Active LP Management runbook](./hodlmm-active-lp-management-runbook.md)). Exit is terminal;
  don't use it as a rebalance.

## Inputs

| Param | Meaning | Default |
|---|---|---|
| `wallet` | signing address | — |
| `pool-id` | pool to exit | — |
| `bins` | which bins to withdraw | all of the wallet's bins in the pool |
| `convert-to` | optional: base asset to convert proceeds into (requires `swap` scope) | none (leave as withdrawn) |
| `slippage-bps` | min-out tolerance for any conversion swap | per skill default |

## Required Approval Scope (INV-1)

- Permissions needed: **`withdraw`** (and **`swap`** only if `convert-to` is set).
- Emergency exit is allowed with **no cooldown** (handbook / Active LP runbook cooldown policy), but it
  still requires `withdraw` scope and the full pre-flight GATE.
- If scope lacks `withdraw` (or is expired) → **read-only**; request approval. Do not infer authority.

## Gates — run BEFORE execute

```
[ ] Active scope includes `withdraw` (and `swap` if converting)        (INV-1)
[ ] Fresh scan this iteration; withdraw plan re-simulated               (INV-7)
[ ] Exit is the right call — pool genuinely stale or operator-ordered   (INV-9)
[ ] Withdraw protection set: min-dlp / liquidity-fee caps / deviation   (INV-2, LP form)
[ ] Conversion swap (if any): *-simple-range-multi, max-steps <= 230,
    Deny post-conditions with real min-out                              (INV-2/3)
[ ] Nonce serialized; signer RBF path known                            (INV-6)
[ ] Ledger entry prepared; mark pool exited/stale in memory             (INV-11/12)
```

## Procedure

Dry-run before any broadcast. The withdraw path burns DLP and returns the underlying — its protection
is the **LP (Allow + contract-level bounds)** form, not sender post-conditions (INV-2).

1. **SCAN** — read the wallet's position in the pool: bins held, per-bin amounts, total DLP, in/out-of-range.
   `bitflow-hodlmm-withdraw status …` (or `hodlmm-move-liquidity scan …`) → position report.
2. **DECIDE** — confirm exit is warranted (stale pool per §Pool checks, or operator order). If the pool
   is healthy and you meant to rebalance → stop and use the Active LP / recenter runbook instead.
3. **DRY-RUN** — preview the withdraw: target bins, expected token amounts, `min-dlp` / fee bounds.
   `bitflow-hodlmm-withdraw status …` *(no confirm token)*. Verify amounts match the position (INV-7).
4. **EXECUTE — withdraw** — `bitflow-hodlmm-withdraw run … ` with the skill's explicit confirm token
   (see its `SKILL.md`). Proof path: `dlmm-liquidity-router…withdraw-relative-liquidity-same-multi`.
   Large positions may need **multiple calls** across bin batches — handle each like a leg (re-scan
   between them, INV-7).
5. **EXECUTE — convert (optional)** — only if `convert-to` is set and scope grants `swap`: route the
   proceeds via `bitflow-swap-aggregator run … --confirm=SWAP`, bounded entrypoint, `max-steps ≤ 230`,
   real `min-out`, handle any residual (INV-3).
6. **VERIFY** — re-scan; confirm the position is **empty** (no remaining bins / DLP) and tokens are in
   the wallet; confirm each tx mined `success` (INV-10).
7. **REMEMBER** — write both ledgers (txids, before/after, gas); in memory, **mark the pool as exited /
   stale** so the monitoring loop doesn't re-engage it (INV-11/12).

## Expected outputs

- One or more `txid`s; the wallet's position in `pool-id` reduced to **zero** bins / zero DLP.
- Withdrawn tokens (and, if converted, the base asset) back in the wallet.
- A `blocked` status (confirmation / cooldown / deviation) is expected, not an error.

## Failure handling

| Symptom | Handbook |
|---|---|
| Withdraw/swap stuck `pending` / nonce stalled | Ch.3 §3.2 (RBF unstick) |
| Conversion swap partial fill | Ch.3 §3.3 (residual) |
| Position still shows balances after confirm | Ch.3 §3.4 (indexing latency — re-read, don't re-submit) |
| `blocked` (confirmation / deviation) | Ch.3 §3.5 |
| Repeated failure / suspected fund-risk / key exposure | Ch.3 §3.6 → STOP + escalate |

## Idempotency / cooldown

- **Emergency exit: no cooldown.** Re-running a withdraw against an already-empty position is a no-op
  (verify in step 1 and stop if nothing to withdraw).
- Multi-batch withdrawals are resumable — re-scan and continue from the remaining bins; never re-send a
  completed batch.

## Notes

- Exit is **terminal for that position** — it does not preserve range or fee accrual. If the goal is to
  keep earning, use recenter, not exit.
- Pair this with `hodlmm-pnl-runbook.md` (planned) for end-of-campaign accounting: attribute realized
  proceeds vs DLP mark-to-market vs earned fees (INV-8) — don't report DLP balance as PnL.
