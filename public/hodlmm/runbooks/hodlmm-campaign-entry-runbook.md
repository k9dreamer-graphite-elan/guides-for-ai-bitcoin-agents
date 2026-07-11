---
name: HODLMM Campaign Entry Runbook
type: runbook
handbook: v0.8
enforces: [INV-1, INV-2, INV-3, INV-6, INV-7, INV-9, INV-10, INV-11, INV-12]
skills: [hodlmm-signal-allocator, hodlmm-risk, hodlmm-flow, defi-portfolio-scanner, bitflow, bitflow-swap-aggregator, bitflow-hodlmm-deposit, hodlmm-bin-guardian, nonce-manager]
status: draft
---

# HODLMM Campaign Entry Runbook

> Conforms to the [HODLMM Agent Handbook](../handbook/HODLMM-Agent-Handbook.md) **v0.8**.
> Enforces: INV-1, INV-2, INV-3, INV-6, INV-7, INV-9, INV-10, INV-11, INV-12.

## Purpose

Open a new HODLMM LP position: select a pool, confirm the entry is warranted by live signals, acquire
the right inventory, and place the **initial deposit** under an explicit Approval Scope. This is the
front door of a campaign; ongoing management is the [Active LP](./hodlmm-active-lp-management-runbook.md)
runbook.

## When to run / when NOT to run

- **Run when:** you have (or are granted) scope to open a position and the target pool is live, healthy,
  and passes the signal/regime/flow gates (handbook Ch.4).
- **Do NOT run when:**
  - the pool is **stale** or thin — never fund a stale pool (INV-9);
  - regime is `crisis` (do not add — pull) or flow verdict is `lpSafety: avoid` (Ch.4 §4.2);
  - scope is missing/expired → stay read-only and request approval (INV-1).
- Decision reference: handbook Ch.2 **Playbook B** (provide LP) + Ch.4 §4.2–4.6 (width/exposure/timing).

## Inputs

| Param | Meaning | Default |
|---|---|---|
| `wallet` | signing address | — |
| `pool-id` | target pool (or a candidate set to rank) | — |
| `size` | capital to deploy (respect exposure caps) | — |
| `width` | bin spread around active bin | from regime (`hodlmm-risk.recommendedBinWidth`) |
| `target-ratio` | X:Y inventory split for the deposit | per profile (e.g. 50:50) |
| `slippage-bps` | min-out tolerance for any prep swap | per skill default |

## Required Approval Scope (INV-1)

- Permissions needed: **`add-new`** (open a position) and **`swap`** only if a prep swap is required to
  acquire inventory.
- Caps this runbook respects: `size ≤` scope max exposure; `width` within the regime's
  `maxExposurePct`; pool must be in the scope's allowed set.
- If scope lacks `add-new` (or is expired) → **read-only**: rank pools, simulate, and request approval.
  Do not infer authority.

## Gates — run BEFORE execute

```
[ ] Active scope covers this pool + `add-new` (and `swap` if prepping)   (INV-1)
[ ] Fresh scan this iteration; entry plan re-simulated                    (INV-7)
[ ] Pool liveness OK and NOT stale — funding a live pool                  (INV-9)
[ ] Signals pass: regime ≠ crisis, flow ≠ avoid, allocator timing OK      (Ch.4 §4.2/§4.5)
[ ] Prep swap (if any): *-simple-range-multi, max-steps ≤ 230,
    Deny post-conditions with real min-out                                (INV-2/3)
[ ] Deposit protection set: min-dlp / liquidity-fee caps / deviation      (INV-2, LP form)
[ ] Nonce serialized; signer RBF path known                              (INV-6)
[ ] Ledger entry prepared                                                (INV-11)
```

## Procedure

Dry-run before any broadcast. The deposit burns inventory into bins and mints DLP — its protection is
the **LP (Allow + contract-level bounds)** form, not sender post-conditions (INV-2).

1. **SCAN** — read candidate pool state (TVL, volume, active bin, regime, flow) and the wallet's free
   balances. `bitflow get-hodlmm-pools` / `get-hodlmm-bins`, `defi-portfolio-scanner scan`,
   `hodlmm-risk regime-snapshot`, `hodlmm-flow flow`.
2. **DECIDE (gate entry)** — confirm the pool is live (INV-9) and signals pass: `hodlmm-risk`
   regime → width + `maxExposurePct`; `hodlmm-flow` → go/no-go + asymmetry; `hodlmm-signal-allocator
   scan` → allocation timing. Any `crisis` / `avoid` / bad-timing ⇒ **hold**, do not enter.
3. **SIZE** — set `width` from regime and `size` within exposure caps; compute the `target-ratio`
   inventory the deposit needs vs current balances.
4. **DRY-RUN deposit** — `bitflow-hodlmm-deposit status --wallet … --pool-id … --amount-x … --amount-y
   …` *(no confirm)* → preview bins, expected DLP, `min-dlp` / fee bounds. Verify it matches intent
   (INV-7).
5. **EXECUTE — prep swap (optional)** — only if inventory must be acquired and scope grants `swap`:
   `bitflow-swap-aggregator run … --confirm=SWAP`, bounded entrypoint, `max-steps ≤ 230`, real
   `min-out`, handle residual (INV-2/3). Re-scan after (INV-7).
6. **EXECUTE — deposit** — `bitflow-hodlmm-deposit run … --confirm=DEPOSIT`. Proof path:
   `dlmm-liquidity-router…add-relative-liquidity-same-multi` (above active = X only, below = Y only, at
   active = both & taxed — handbook §1.3). Serialize the nonce after the prep swap (INV-6).
7. **VERIFY** — re-scan; confirm the position exists with the intended bins/width and is **in range**.
   `hodlmm-bin-guardian run` → expect `HOLD` (in-range); confirm each tx mined `success` (INV-10).
8. **TAG** — if the campaign adopts the [memo-tag spec](../specs/campaign-memo-tags.md): after the
   deposit confirms, emit the `E` boundary tag (`H1E:<pool>-<yymmdd>-<nnn>`, 1 µSTX self-transfer,
   nonce serialized — INV-6/10) as a **Day-0 artifact**, same session as the entry. This mints the
   campaign id on-chain; the tag labels, it never feeds the money math.
9. **REMEMBER** — write both ledgers (txids, entry bins, cost basis, gas) and seed memory: pool,
   entry price, target ratio, width — the basis the [PnL runbook](./hodlmm-pnl-runbook.md) and
   monitoring loop will use (INV-11/12). Record the **deposited native amounts and the entry
   timestamp** explicitly: the closeout PnL report/card derives the deployed hold baseline and the
   campaign-period label from them, and there is no endpoint that can reconstruct them later.

## Expected outputs

- One (deposit) or two (prep swap + deposit) `txid`s; a new in-range position in `pool-id` with the
  intended width and DLP minted.
- Seeded cost basis + Transaction Ledger row for the campaign.
- A `blocked` status (confirmation / cooldown / deviation / failed gate) is **expected**, not an error.

## Failure handling

| Symptom | Handbook |
|---|---|
| Prep swap / deposit stuck `pending` / nonce stalled | Ch.3 §3.2 (RBF unstick) |
| Prep swap partial fill | Ch.3 §3.3 (residual — don't re-send original size) |
| Deposit confirmed but position not in range | Ch.3 §3.4 (re-read) then recenter (Active LP runbook) |
| Stale quote / lagging pool state | Ch.3 §3.4 |
| `blocked` (confirmation / deviation / failed signal gate) | Ch.3 §3.5 |
| Repeated failure / suspected fund-risk / key exposure | Ch.3 §3.6 → STOP + escalate |

## Idempotency / cooldown

- **Not blindly re-runnable** — a second deposit opens *more* exposure, it doesn't retry the first.
  After a partial (swap done, deposit failed), re-scan and resume from the remaining step; never
  re-send a completed leg (INV-6).
- Respect any per-pool entry cooldown the scope or strategy imposes.

## Notes

- Entry width is an **IL decision**, not just a fee decision (handbook §6.6 / operating guide §3.1):
  narrower captures more fees but realizes IL faster on a move. Size width against expected fee capture
  **and** expected IL.
- For an asymmetric entry under a strong `hodlmm-flow.directionBias`, skew bins per handbook §4.3 —
  still inside the same GATE.
- One operation: **open**. Recenter, rebalance, and exit are their own runbooks.

## Field-confirmed addendum — HODLMM-DLMM3-20260625-002

> Source: K9Dreamer `dlmm_3` STX/USDCx campaign-002 closeout (issues #21/#22).

**Floor-pinned entry shape.** If the pre-entry scan shows the active bin at the pool floor, the
standard two-sided entry is illegal (negative offsets fall below the minimum bin). Enter with a
one-sided ladder including the active bin, exact active-bin tolerance (`maxDeviation=0`) so the
position cannot shift under a stale read — or wait for the bin to rise before opening a two-sided
shape. See the recenter runbook's boundary-geometry addendum for the matching repair shape.

**Size scale-ups from mined output, not quotes.** On bounded routes, swap quotes are not fill
guarantees: a tx can succeed while spending only part of the requested input and returning less
than quoted. Broadcast top-up swaps in small chunks, verify mined in/out per tx, size the LP add
from **confirmed wallet balances only**, and stop swapping once the route tail-fills (fees eat the
edge past that point). Field results (context only): three sBTC→STX chunks filled 8,864 / 27,372 /
1,205 sats against much larger requests; the third was the stop signal.
