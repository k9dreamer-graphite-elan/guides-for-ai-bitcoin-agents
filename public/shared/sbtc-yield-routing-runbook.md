---
name: sBTC Yield Routing Runbook
type: runbook
handbook: v0.6
enforces: [INV-1, INV-2, INV-3, INV-6, INV-7, INV-10, INV-11, INV-12]
skills: [sbtc-yield-maximizer, defi-portfolio-scanner, sbtc, query, nonce-manager]
status: draft
---

# sBTC Yield Routing Runbook

> Cross-protocol: **HODLMM (Bitflow) + Zest**. Conforms to the
> [HODLMM Agent Handbook](../hodlmm/handbook/HODLMM-Agent-Handbook.md) **v0.6** for the HODLMM leg;
> the Zest supply leg is owned by the `sbtc-yield-maximizer` skill.
> Enforces: INV-1, INV-2, INV-3, INV-6, INV-7, INV-10, INV-11, INV-12.

## Purpose

Route idle **sBTC** to the highest *safe* live yield path — compare HODLMM LP APR against Zest supply
under TVL / volume / divergence gates, then deploy to the winning route (capped Zest supply **or** a
HODLMM rebalance) when it is safely executable.

## When to run / when NOT to run

- **Run when:** the wallet holds idle sBTC above a meaningful threshold and you have scope to deploy it
  to yield.
- **Do NOT run when:**
  - no route clears its safety gates (then **hold** — idle is better than unsafe yield);
  - the HODLMM candidate pool is **stale** (INV-9 — the skill should reject it; verify);
  - scope is missing/expired (INV-1).
- This is a **routing** decision across two protocols; the per-protocol execution detail lives in the
  skill (and, for HODLMM management, the protocol runbooks).

## Inputs

| Param | Meaning | Default |
|---|---|---|
| `wallet` | signing address holding sBTC | — |
| `amount` | sBTC to route (respect reserve + exposure caps) | skill/scope default |
| `reserve` | sBTC/STX to keep back (gas + buffer) | per skill default |
| `min-edge` | minimum APR edge to prefer one route over the other | per skill default |

## Required Approval Scope (INV-1)

- Permissions needed: the route's action — **`add-new`/`manage-existing`** for the HODLMM leg
  (and `swap` if it must convert), or **Zest `supply`** for the lending leg. Grant only what the chosen
  route uses.
- Caps respected: `amount ≤` scope exposure; keep `reserve`; per-venue caps.
- If scope doesn't cover the winning route (or is expired) → **read-only** (`status` only); request the
  specific permission. Do not infer authority across protocols.

## Gates — run BEFORE execute

```
[ ] Active scope covers the winning route's protocol + action            (INV-1)
[ ] Fresh scan this iteration; route decision re-derived                  (INV-7)
[ ] HODLMM candidate (if chosen) is live, not stale                       (INV-9)
[ ] Any swap leg bounded: *-simple-range-multi, max-steps ≤ 230,
    Deny post-conditions with real min-out                                (INV-2/3)
[ ] HODLMM LP leg protection: min-dlp / fee caps / deviation              (INV-2, LP form)
[ ] Zest supply within cap; collateral/health implications understood     (INV-2)
[ ] Nonce serialized (`nonce-manager`); signer RBF path known            (INV-6)
[ ] Ledger entry prepared                                                (INV-11)
```

## Procedure

Dry-run before broadcast. The winning route is either a **Zest supply** (lending deposit) or a
**HODLMM rebalance** (LP, Allow + bounds); a conversion swap, if any, is the bounded Deny-PC form
(INV-2/3). Serialize the nonce across legs (INV-6).

1. **SCAN** — read idle balances and both venues' live state.
   `sbtc-yield-maximizer doctor` / `status`, `defi-portfolio-scanner scan`, `sbtc get-balance`,
   `query` for any on-chain reads.
2. **DECIDE (route)** — `sbtc-yield-maximizer status` ranks the routes: HODLMM APR vs Zest yield under
   TVL / volume / divergence gates. Pick the winner only if it clears `min-edge` and its safety gates;
   otherwise **hold** (idle).
3. **DRY-RUN** — review the winning route's plan: amount, expected APR, any swap `min-out`, the LP/
   supply bounds. Verify it matches intent (INV-7); confirm the HODLMM pool isn't stale (INV-9).
4. **EXECUTE** — `sbtc-yield-maximizer run --confirm=MAXIMIZE`. The skill re-checks the decision and
   executes the safe route: capped Zest supply or HODLMM rebalance. Handle any swap residual (INV-3).
   Signer via env, never argv.
5. **VERIFY** — re-scan; confirm capital landed in the intended venue (Zest position grew, or the
   HODLMM position is in range) and each tx mined `success` (INV-10).
6. **REMEMBER** — write both ledgers (txids, chosen route, amounts, gas) + memory (route taken, APRs at
   decision time, for next comparison) (INV-11/12).

## Expected outputs

- One or more `txid`s; idle sBTC deployed to the winning route (Zest supply **or** HODLMM position).
- A recorded route decision (chosen venue + the APR edge that justified it).
- `hold` / `blocked` (no safe route / confirmation / cap) is an **expected** outcome, not an error.

## Failure handling

| Symptom | Handbook |
|---|---|
| Supply / swap / LP leg stuck `pending` / nonce stalled | Ch.3 §3.2 (RBF unstick) |
| Conversion swap partial fill | Ch.3 §3.3 (residual) |
| Capital not reflected after confirm | Ch.3 §3.4 (indexing latency — re-read, don't re-submit) |
| `blocked` (no safe route / confirmation / cap) | Ch.3 §3.5 |
| Repeated failure / suspected fund-risk / key exposure | Ch.3 §3.6 → STOP + escalate |

## Idempotency / cooldown

- **Re-deriving the route is always safe** (read-only `status`). Re-running `run` re-checks the decision
  first, but treat it as a *new* deployment — don't re-run to "retry" a leg that may have landed
  (re-scan first, INV-7/10).
- Respect any per-venue cooldown (e.g. the HODLMM rebalance cooldown) the skill enforces.

## Notes

- The HODLMM route here is an **entry/rebalance** of an LP position — its IL exposure is governed by
  handbook §6.6 (operating guide §3.1). Routing to HODLMM yield is not free of divergence risk; the
  APR comparison should be risk-adjusted, not raw.
- For ongoing management of a HODLMM position opened by this route, hand off to the protocol runbooks
  ([Active LP](../hodlmm/runbooks/hodlmm-active-lp-management-runbook.md) / recenter / exit).
- Zest-side mechanics (supply caps, collateral/health) are owned by `sbtc-yield-maximizer` and Zest's
  own docs — this runbook conforms to the HODLMM handbook for the Bitflow leg only.
