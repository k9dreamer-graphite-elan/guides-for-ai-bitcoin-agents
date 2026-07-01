---
name: HODLMM Inventory Balancing Runbook
type: runbook
handbook: v0.6
enforces: [INV-1, INV-2, INV-3, INV-6, INV-7, INV-9, INV-10, INV-11, INV-12]
skills: [hodlmm-inventory-balancer, nonce-manager]
status: draft
---

# HODLMM Inventory Balancing Runbook

> Conforms to the [HODLMM Agent Handbook](../handbook/HODLMM-Agent-Handbook.md) **v0.6**.
> Enforces: INV-1, INV-2, INV-3, INV-6, INV-7, INV-9, INV-10, INV-11, INV-12.

## Purpose

Restore a position's **token ratio** to target after one-sided swap flow has skewed it — via a
corrective Bitflow swap plus a redeploy around the active bin. This fixes **inventory drift** (ratio
imbalance), which is a different problem from **price drift** (range out of position — that's the
[Recenter runbook](./hodlmm-recenter-runbook.md)). See handbook §4.4.

## When to run / when NOT to run

- **Run when:** the position's price-weighted token ratio has drifted off target (e.g. past 50:50)
  beyond a threshold, the per-pool cooldown has elapsed, and the pool is healthy.
- **Do NOT run when:**
  - the pool is **stale** — exit, don't rebalance (INV-9);
  - the cooldown hasn't elapsed (the skill blocks — a safe stop);
  - regime is `crisis` or scope is missing/expired (INV-1).
- Decision reference: handbook Ch.4 **§4.4** (inventory balancing — symmetric exposure ≠ in-range).

## Inputs

| Param | Meaning | Default |
|---|---|---|
| `wallet` | signing address | — |
| `pool` | pool with the drifted position | — |
| `target-ratio` | desired X:Y split | `50:50` |
| `min-drift-pct` | deviation that triggers a rebalance | `5` |
| `skip-redeploy` | corrective swap only, leave redeploy | off |

## Required Approval Scope (INV-1)

- Permissions needed: **`swap`** (corrective trade) **and** **`manage-existing`** (redeploy around
  active). The balancer performs both legs.
- Caps respected: corrective swap `size` within exposure; redeploy `width`/deviation within scope;
  `target-ratio` from scope/profile.
- If scope lacks either permission (or is expired) → **read-only** (`status` / `recommend` only);
  request approval. Do not infer authority.

## Gates — run BEFORE execute

```
[ ] Active scope covers this pool + `swap` + `manage-existing`            (INV-1)
[ ] Fresh scan this iteration; rebalance plan re-simulated                (INV-7)
[ ] Pool healthy, NOT stale                                              (INV-9)
[ ] Per-pool cooldown elapsed (else blocked — safe stop)
[ ] Corrective swap bounded: *-simple-range-multi, max-steps ≤ 230,
    Deny post-conditions with real min-out                                (INV-2/3)
[ ] Redeploy protection: min-dlp / liquidity-fee caps / active-bin deviation (INV-2, LP form)
[ ] Nonce serialized across swap → redeploy                              (INV-6)
[ ] Ledger entry prepared                                                (INV-11)
```

## Procedure

Dry-run before broadcast. The balancer runs **two legs** — a bounded corrective **swap** (Deny
post-conditions + real `min-out`, INV-2/3) then an LP **redeploy** (Allow + bounds, INV-2) — back to
back; serialize the nonce between them (INV-6).

1. **SCAN / STATUS** — `hodlmm-inventory-balancer status --pool …` → current effective token ratio,
   target, deviation, and cooldown remaining. Confirm the pool is live (INV-9).
2. **DECIDE / RECOMMEND** — `hodlmm-inventory-balancer recommend --pool … --target-ratio … --min-drift-pct …`
   → dry-run the full cycle (corrective swap size + redeploy). Rebalance only if deviation ≥
   `min-drift-pct` and cooldown elapsed; otherwise **hold**.
3. **DRY-RUN** — review the `recommend` plan: swap direction/size, `min-out`, redeploy bins/bounds.
   Verify it matches intent (INV-7). The corrective swap must be a bounded entrypoint, `max-steps ≤ 230`
   (INV-3).
4. **EXECUTE** — `hodlmm-inventory-balancer run --confirm=BALANCE --pool …` (add `--skip-redeploy` for
   swap-only). The skill performs the bounded swap (Deny PCs) then the `hodlmm-move-liquidity` redeploy;
   handle any swap residual (INV-3). Signer via env, never argv.
5. **VERIFY** — re-scan; confirm the ratio is at/near target and the redeployed position is in range;
   confirm both legs mined `success` (INV-10).
6. **REMEMBER** — write both ledgers (txids, before/after ratio, gas) + memory (new ratio, rebalance
   timestamp for the cooldown) (INV-11/12).

## Expected outputs

- Up to two `txid`s (corrective swap + redeploy); the position's token ratio restored to target and the
  redeployed bins in range.
- A `blocked` status (cooldown / confirmation / deviation) is **expected**, not an error.

## Failure handling

| Symptom | Handbook |
|---|---|
| Swap or redeploy stuck `pending` / nonce stalled | Ch.3 §3.2 (RBF unstick) |
| Corrective swap partial fill | Ch.3 §3.3 (residual — don't re-send original size) |
| Swap done, redeploy failed | Ch.3 §3.4 (re-scan) → resume redeploy only; never re-swap |
| Ratio still off after confirm | Ch.3 §3.4 (indexing latency — re-read, don't re-rebalance) |
| `blocked` (cooldown / confirmation / deviation) | Ch.3 §3.5 |
| Repeated failure / suspected fund-risk / key exposure | Ch.3 §3.6 → STOP + escalate |

## Idempotency / cooldown

- **4h per-pool cooldown** (the balancer enforces it) — do not loop rebalances; `blocked: cooldown` is
  a safe stop, not a failure.
- A partial cycle (swap landed, redeploy didn't) is **resumable** — re-scan and finish the redeploy;
  never re-send the corrective swap, which would over-correct the ratio (INV-6).

## Notes

- Inventory drift (ratio) and price drift (range) are **distinct** — don't recenter to fix a ratio or
  rebalance to fix a range (handbook §4.4). Diagnose with `status` before acting.
- Rebalancing trades realize a small cost; only worth it when the ratio skew is material and the pool
  is productive. Persistent one-sided flow may instead argue for an **asymmetric range** (§4.3) or an
  **exit** if it reflects a regime the position shouldn't fight.
- The corrective swap and redeploy are owned by the `hodlmm-inventory-balancer` skill; this runbook
  orchestrates the decision + GATE around it rather than driving `bitflow` / `hodlmm-move-liquidity`
  directly.

## Addendum — asymmetric inventory for volatile / cash pairs

For a volatile major (V) vs cash (C) pair under a USD numéraire, the target is **not** 50:50 — see
handbook Ch.4 §4.4 and the operating-guide "Volatile major/cash pair" profile. Differences from the
symmetric procedure above:

- The `target-ratio` is the profile's `f*` (cash-tilted), not 50:50; the trigger is the **V-only** soft/
 hard cap, not a symmetric deviation band.
- **Soft cap is handled passively** (skew-to-sell + widen + reduce size) — usually **no swap**.
- The **hard-cap corrective swap runs only when the INV-13 tier is aligned/healthy.** If the divergence/
 feed gate reports defensive/abnormal, **do not blind-swap** — halt-and-hold and hand to the exit path.
- **No lower-side correction:** never market-buy V to "rebalance up." Cash-heaviness is re-accumulated
 passively via bids on dips.
- The corrective swap is still bounded (`*-simple-range-multi`, `max-steps ≤ 230`, real `min-out`, INV-3)
 with nonce serialized across swap → redeploy (INV-6).
