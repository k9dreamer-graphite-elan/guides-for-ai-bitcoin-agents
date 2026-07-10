---
name: HODLMM Recenter Runbook
type: runbook
handbook: v0.8
enforces: [INV-1, INV-2, INV-6, INV-7, INV-9, INV-10, INV-11, INV-12]
skills: [hodlmm-bin-guardian, hodlmm-move-liquidity, nonce-manager]
status: active
---

# HODLMM Recenter Runbook

> Conforms to the [HODLMM Agent Handbook](../handbook/HODLMM-Agent-Handbook.md) **v0.8**.
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
  pushed you out of range and converted you to one side (bins left above active hold X only, bins left
  below hold Y only — handbook §1.3), that divergence is real — recentering re-engages fees but doesn't
  claw it back.
  Weigh recenter vs exit on the fee-to-IL ratio (operating guide §3.1).
- This runbook is the atomic primitive; the **cadence** (when to check, the monitoring loop) lives in
  the Active LP Management runbook, scheduled via runtime cron or `hodlmm-move-liquidity auto`.
- Alternative skill: `hodlmm-range-keeper` offers a keeper-style recenter cadence over the same router
  entrypoint — same GATE applies.

## Field-confirmed addendum — HODLMM-DLMM6-20260602-001

> Source: K9Dreamer `dlmm_6` STX/sBTC campaign closeout (issues #4/#5). Independently
> reproduces the native-move findings from the Hex Stallion closeout (#2). Reviewer
> evidence (bins/pools) is campaign context, not evergreen doctrine.

**Native-move legality is a geometry proof, not an intent proof.** Before broadcasting a
same-pool native move (e.g. `move-relative-liquidity-multi`):

1. Read current active bin and current wallet bins.
2. Compute source and target bin sets.
3. Prove source/target **non-overlap** and a legal direction for the current one-sidedness.
4. If overlap exists, or the move is a downward shift on a fully one-sided (single-token)
   position, **do not broadcast** — route to withdraw/swap/redeposit.
5. A move returning `(err u5001)` is a shape rejection, not a timing hiccup. **Never blind-retry
   the same shape.**

Field results (dlmm_6 STX/sBTC, context only): failed `(u5001)` `319→333`, `314→328`
(downward, one-sided STX); succeeded `316→330`, `331→345` (upward / non-overlapping).

**Withdraw → swap → redeposit is a first-class recenter route** for `u5001`-shaped or
width-expanding repairs: withdraw (confirm on-chain) → swap toward target ratio if needed →
redeposit covering the current active bin with fresh min-DLP/postconditions. Higher gas per
cycle, but it is the reliable repair when a native move shape is illegal. Account for every
leg's gas; failed legs are campaign cost.

## Field-confirmed addendum — HODLMM-DLMM3-20260625-002

> Source: K9Dreamer `dlmm_3` STX/USDCx campaign-002 closeout (issues #21/#22). Reviewer evidence
> (bins/pools/amounts) is campaign context, not evergreen doctrine.

**Boundary (floor-pinned) geometry.** When the active bin sits at the pool floor (displayed bin `0`;
raw signed id at its minimum), two-sided `-N..+N` offsets are **invalid** — negative offsets map below
the pool's minimum bin. The legal shape is a one-sided ladder that *includes* the active bin (e.g.
offsets `0..+7`, base-token only), and a "recenter" degenerates to a same-shape withdraw + redeposit.
Only adopt a two-sided shape after the active bin has risen off the floor. Field results (dlmm_3,
context only): a bins-0–7 STX ladder entered cleanly with exact active-bin tolerance and later
monetized two full out-of-range round trips with zero recenter spend.

**Withdraw minimums from direct on-chain reads are exact, not merely safe.** Compute expected output
per bin as `get-balance(bin, user) / get-total-supply(bin) × get-bin-balances(bin)`, set minimums
from that (e.g. ×0.90), **nonzero on the expected side, never 0/0**. BFF-derived reserves can read
zero/degraded and are not a signing basis; if the direct reads are degraded, ABORT and alert — never
sign blind. Field results: mined withdraw output matched the read-only plan **to the µSTX, twice**
(supervised round-trip and final exit). This extends the dlmm_6 `u5001` rules above: the same
direct-read discipline that avoids illegal shapes also prices the exit exactly.

## Field-confirmed addendum — staged repair is a continuation state machine (Hex Stallion campaigns)

> Source: Hex Stallion closeouts (issues #1–#3, #11–#13).
> See [LSN-0006](../knowledge/lessons/lessons-catalog.md#lsn-0006).

Staged withdraw/add repair is a state machine, not a fresh strategy prompt each cycle. After a
staged withdraw begins, the valid states are: withdraw pending → withdraw confirmed / add required →
add submitted → add confirmed / post-confirm proof required → **completed with strict range proof** —
or **archived/superseded as an incident**. Field pattern (two campaigns): staged repair restored
range exactly once, then stale continuation state froze the actuator and blocked unrelated repairs
through closeout. Do not let stale staged state block indefinitely: diagnose, add a pre-broadcast
guard or patch if needed, then archive or supersede the staged state before new strategy selection
resumes. Tx success mid-chain is not LP recovery until post-confirm proof exists
([LSN-0011](../knowledge/lessons/lessons-catalog.md#lsn-0011)).

## Field-confirmed addendum — HODLMM-DLMM1-20260702-003

> Source: K9Dreamer `dlmm_1` sBTC/USDCx campaign-003 closeout
> ([#28](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/28)).

**Fee bumping is a new approval scope.** If the configured fee target fails, stop and alert; raising
the tx fee is a new approval decision unless a fee-bump ladder was explicitly authorized in the
campaign charter (INV-1). Field results (context only): `0.10 STX` cleared 8 consecutive recenters
and the exit; the step-downs `0.25 → 0.15 → 0.10` were each operator-approved, never automatic.

**Repair-count caps are campaign policy, not the safety invariant.** A narrow band on a volatile
pair legitimately needed 16 gated recenters in 7 days; a fixed repair-count ceiling would have forced
days of out-of-range idle. The safety invariant is the gate stack — N-scan confirmation + cooldown +
gas cap + slippage/mempool/source-agreement gates — with any repair-count limit a deliberate charter
choice on top.

**Enforce invariants at sign time, not only at dry-run time.** A signer that refreshes the active
bin immediately before signing may execute a different destination range than the dry-run showed
(field case: dry-run `445-450`, executed `437-442` after a pre-sign refresh). That is acceptable
only because the invariants — same pool, same existing inventory, correct side-offset rule — were
enforced in the signing path itself. Log both the dry-run target and the executed target; a
dry-run/execution divergence with invariants enforced is an audit note, without them it is an incident.
