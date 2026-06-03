---
name: HODLMM Recenter Runbook
type: runbook
handbook: v0.6
enforces: [INV-1, INV-2, INV-6, INV-7, INV-9, INV-10, INV-11, INV-12]
skills: [hodlmm-bin-guardian, hodlmm-move-liquidity, nonce-manager]
status: draft
---

# HODLMM Recenter Runbook

> Conforms to the [HODLMM Agent Handbook](../handbook/HODLMM-Agent-Handbook.md) **v0.6**.
> Enforces: INV-1, INV-2, INV-6, INV-7, INV-9, INV-10, INV-11, INV-12.

## Purpose

Re-center a drifted HODLMM position: withdraw from out-of-range bins and re-deposit around the current
active bin in **one atomic transaction** (`move-relative-liquidity-multi`). This is the execution
primitive the [Active LP Management](./hodlmm-active-lp-management-runbook.md) loop calls when a healthy
position has drifted but the pool is still worth providing to.

## When to run / when NOT to run

- **Run when:** the pool is **healthy** (live volume, fees generating, active bin moving) and your
  position has drifted off the active bin far enough to hurt fee capture, but recentering still pays.
- **Do NOT run when:**
  - the pool is **stale** — that's an **exit**, not a recenter (INV-9 → [Exit runbook](./hodlmm-exit-runbook.md));
  - **IL is outrunning fee accrual** — also an exit decision (handbook §6.6 / operating guide §3.1);
  - regime is `crisis` (pull, don't reposition) or scope is missing/expired (INV-1).
- Decision reference: handbook Ch.2 **Playbook C** (manage/recenter) + Ch.4 §4.2.

## Inputs

| Param | Meaning | Default |
|---|---|---|
| `wallet` | signing address | — |
| `pool-id` | pool holding the position | — |
| `drift-threshold` | bins of drift that trigger a recenter | `3` (or scope/profile value) |
| `width` | bin spread to re-deposit around active | from regime (`hodlmm-risk.recommendedBinWidth`) |

## Required Approval Scope (INV-1)

- Permissions needed: **`manage-existing`** (move an existing position around the active bin).
- Caps respected: `width ≤` regime/scope spread; active-bin deviation tolerance set on the move.
- Recenter does **not** require `add-new` (no fresh capital) or `withdraw`-to-wallet (funds stay in the
  pool). If scope is missing/expired → **read-only**; request approval. Do not infer authority.

## Gates — run BEFORE execute

```
[ ] Active scope covers this pool + `manage-existing`                     (INV-1)
[ ] Fresh scan this iteration; move plan re-simulated                     (INV-7)
[ ] Pool healthy, NOT stale; recenter (not exit) is the right call        (INV-9)
[ ] IL not outrunning fees (else exit)                                    (§6.6)
[ ] Move protection set: min-dlp / liquidity-fee caps / active-bin deviation (INV-2, LP form)
[ ] Nonce serialized; signer RBF path known                              (INV-6)
[ ] Ledger entry prepared                                                (INV-11)
```

## Procedure

Dry-run before broadcast. The move is **atomic** — withdraw + re-deposit in one tx via the liquidity
router; its protection is the **LP (Allow + contract-level bounds)** form, not sender post-conditions
(INV-2). No swap leg, so no bounded-swap concern here.

1. **SCAN** — read the position vs the current active bin: bins held, per-bin amounts, drift, in/out of
   range. `hodlmm-move-liquidity scan` and/or `hodlmm-bin-guardian run` → `HOLD | REBALANCE | CHECK`.
2. **DECIDE** — recenter only if `REBALANCE` **and** the pool is healthy **and** IL isn't outrunning
   fees. If the pool is stale or divergence is winning → stop and use the Exit runbook (INV-9, §6.6).
3. **DRY-RUN** — `hodlmm-move-liquidity run …` *(no `--confirm`)* → preview the target range, bins to
   move, expected DLP, `min-dlp` / deviation bounds. Verify it matches intent (INV-7).
4. **EXECUTE** — `hodlmm-move-liquidity run … --confirm` (signer unlocked via env/`--password`, never
   argv-logged). Proof path: `dlmm-liquidity-router…move-relative-liquidity-multi`. Nonce serialized
   (INV-6).
5. **VERIFY** — re-scan; confirm the new range is centered on the active bin and in range; confirm the
   tx mined `success` (INV-10). `hodlmm-bin-guardian run` → expect `HOLD`.
6. **REMEMBER** — write both ledgers (txid, before/after range, gas) + memory (new range, recenter
   timestamp for cooldown) (INV-11/12).

## Expected outputs

- One `txid`; the position re-centered on the active bin at the intended width, DLP preserved (fees
  auto-compounded, not realized).
- A `blocked` status (cooldown / confirmation / deviation) is **expected**, not an error.

## Failure handling

| Symptom | Handbook |
|---|---|
| Move stuck `pending` / nonce stalled | Ch.3 §3.2 (RBF unstick) |
| Move confirmed but still out of range | Ch.3 §3.4 (re-read; the active bin may have moved again — re-scan, don't double-move) |
| Stale quote / lagging position | Ch.3 §3.4 |
| `blocked` (cooldown / confirmation / deviation) | Ch.3 §3.5 |
| Repeated failure / suspected fund-risk / key exposure | Ch.3 §3.6 → STOP + escalate |

## Idempotency / cooldown

- **Cooldown applies** — honor the per-pool recenter cooldown (Active LP runbook policy; e.g. 4h) so a
  fast-moving active bin doesn't trigger churn that bleeds gas. `blocked: cooldown` is a safe stop.
- Never re-send a move to "fix" one that may have landed — re-scan first (INV-7/10); the active bin
  moving again is a *new* decision, not a retry.

## Notes

- Recenter **preserves** a productive position; it does not undo **realized** IL. If price has already
  pushed you out of range and converted you to one side (above active = Y only, below = X only —
  handbook §1.3), that divergence is real — recentering re-engages fees but doesn't claw it back.
  Weigh recenter vs exit on the fee-to-IL ratio (operating guide §3.1).
- This runbook is the atomic primitive; the **cadence** (when to check, the monitoring loop) lives in
  the Active LP Management runbook, scheduled via runtime cron or `hodlmm-move-liquidity auto`.
- Alternative skill: `hodlmm-range-keeper` offers a keeper-style recenter cadence over the same router
  entrypoint — same GATE applies.
