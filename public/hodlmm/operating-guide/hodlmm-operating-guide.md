# HODLMM Operating Guide

> The field manual: how to operate on HODLMM day-to-day, and **which runbook to run when**.
> Conforms to the [HODLMM Agent Handbook](../handbook/HODLMM-Agent-Handbook.md) **v0.7** — this guide
> **references** the handbook; it does not restate its invariants or constants.

This sits between the **handbook** (doctrine — what's true, what you must never violate) and the
**runbooks** (executable procedures). Read the handbook's Chapter 0 first.

---

## 1. The daily loop

Operate on the handbook's seven-phase loop: `SCAN → DECIDE → DRY-RUN → EXECUTE → VERIFY → REMEMBER →
MEASURE`. In steady state, most cycles are **read-only**:

- **Monitoring cadence:** active-management campaigns normally use read-only checks every ~2h; lower-touch
  profiles can choose a slower interval. Each check reads positions,
  active bin, drift, pool health, and the freshness/lag signal — it never signs.
- **Act only on a trigger:** a scan that crosses a threshold (drift, inventory deviation, regime
  change, stale pool) hands off to the matching **runbook**, which runs the gated write path.
- **Before every write:** fresh scan + the Chapter 0 pre-flight GATE. A plan older than the current
 cycle is stale — re-derive it (INV-7). Clear the **divergence/feed-safety gate**
 (`hodlmm-divergence-safety-runbook`) first: a `defensive` tier forces conservative params, an
 `abnormal` tier halts (INV-13).

## 2. Tool / skill catalog

Read-only (safe anytime, no scope): `hodlmm-bin-guardian`, `hodlmm-risk`, `hodlmm-flow`,
`defi-portfolio-scanner`, `query`, and the quote/`scan` verbs of the write skills.

Write (require scope + the pre-flight GATE + an explicit confirm token):
`bitflow` / `bitflow-swap-aggregator`, `bitflow-hodlmm-deposit` / `-withdraw`, `hodlmm-move-liquidity`,
`hodlmm-inventory-balancer`. Nonce safety: `nonce-manager`.

> Skills are published at **aibtc.com/skills**. A write skill must run the Chapter 0 GATE before
> broadcast (handbook Ch.8).

## 3. Strategy selection (which runbook to run)

**Strategy choice lives here; strategy execution lives in a runbook.** Pick a profile from live
readings (`hodlmm-risk` regime + `hodlmm-flow`), then run the matching runbook.

| Profile | Use when | Width / exposure | Runbook |
|---|---|---|---|
| **Active management** (concentrated, recentered) | calm/elevated regime, healthy volume, you can monitor | narrow, near active bin; recenter on drift | `hodlmm-active-lp-management-runbook` |
| **Passive wide-range** | you want low-touch exposure; volatile or thin attention | wide; rare rebalancing | `hodlmm-campaign-entry-runbook` (wide profile) |
| **Single-bin high-concentration** | strong conviction price holds; calm regime; max fee share | ±0–1 bins; high drift risk | `hodlmm-campaign-entry-runbook` (single-bin profile) |
| **Inventory-balanced** | one-sided flow pulling your token ratio off target | maintain target ratio (e.g. 50:50) | `hodlmm-inventory-balancing-runbook` |
| **Volatile major / cash pair** (asymmetric inventory) | pairing a volatile major (V) vs a cash stablecoin (C) — e.g. sBTC/USDCx, STX/USDCx; high divergence, large asymmetric IL | width scales with σ; **V-only** soft/hard caps; hold no idle V beyond a gas buffer | `hodlmm-volatile-pair-mm-runbook` |
| **Exit / stale recovery** | pool volume dead, position drifted out | withdraw, stand down | `hodlmm-exit-runbook` |

**Hard rules from the handbook (do not override here):**
- `crisis` regime ⇒ do **not** add; pull (handbook Ch.4 §4.2).
- flow toxicity high / `lpSafety: avoid` ⇒ stand aside regardless of APR.
- a stale pool is an **exit** candidate, not a rebalance candidate (INV-9).

### 3.1 Managing impermanent loss

IL is the *cost side* of the range-width tradeoff (handbook Ch.6 §6.6 defines it; this is how to
operate on it). The rule of thumb: **concentration buys fee efficiency and sells IL protection.** Tune
the balance to the regime.

**Track these each cycle (feed the Performance Ledger, INV-11):**
- **IL-only PnL** — absolute and as % of hold value.
- **Fee PnL** — absolute and as % of deployed capital.
- **Fee-to-IL ratio** — the headline health metric (> 1 means fees are covering divergence).
- **Time in-range vs out-of-range** — out-of-range time is realized-IL time earning no fees.
- **Capital efficiency** — fees earned per dollar deployed.
- **Net after gas.**

**Width by regime (HODLMM levers only — width, recenter cadence, dynamic fees; no shapes/keepers):**

| Regime / view | Lever | Rationale |
|---|---|---|
| Low-vol / ranging | Narrower range near active bin; recenter rarely | Max fee efficiency while price cooperates; IL stays small |
| High-vol / trending | Wider range; recenter proactively near edges (or stand aside) | Avoid fast one-sided conversion (realized IL) |
| Strong directional view | Narrow range aligned with the view | Express conviction while still earning fees |
| BTC-hold focus | Wider, balanced range; lean on automation cadence | Keep more balanced exposure, accept lower fee APR |
| High-fee event (launch/volume spike) | Tighter bins to capture elevated/variable fees | Fee capture can outpace IL during the spike |

**Mitigation available to the agent:**
- Match range width / bin spread to expected volatility.
- **Recenter proactively** as price approaches a range edge (`hodlmm-move-liquidity`); use its `auto`
  cadence — this is the only "keeper" HODLMM has (handbook §1.7).
- Prefer **stable or correlated pairs** when IL minimization is the priority.
- Only layer extra incentives into a position if they **meaningfully exceed** expected IL.

**The operating rule (ties INV-9):** if a position has drifted and its **IL-only PnL is outrunning its
fee accrual**, treat it as an **exit** candidate, not a recenter — especially in a stale pool. Recenter
preserves a productive position; it doesn't undo realized divergence.

### 3.2 Volatile major / cash-pair profile (asymmetric inventory)

For a volatile major asset **V** vs a cash stablecoin **C** (sBTC/USDCx, STX/USDCx). IL here is large and
one-directional, so this profile manages **directional inventory risk**, not a symmetric ratio. Doctrine:
handbook Ch.4 §4.4 (asymmetric inventory) + INV-13 (divergence gate).

**Numéraire.** Measure risk in USD. C ≈ $1 riskless (with a fixed peg-break halt); V carries all drawdown.

**The four continuous knobs (place resting liquidity; cost is gas only):**
- **Center** on the active bin. Don't offset toward external — that quotes a guess and pays to chase.
- **Skew** toward selling the overweight leg (lean to the V-selling side when long V). Rebalances
 passively by waiting to be filled on the favorable side.
- **Width** scales with σ (wider in higher vol). Floor = max(bin granularity, fee + gas + expected
 adverse cost); cap so capital isn't uselessly thin.
- **Size** = deployed fraction; decreases with σ; **never 100%**. Make the floor *conditional* — when
 expected adverse cost at the floor width exceeds expected fee, the right size is 0 (pull). Reserve = C
 + gas asset; hold no idle V (except an unavoidable gas buffer when V *is* the gas asset, e.g. STX).

**The V-only risk cap (asymmetric; ordering invariant `f* < f_soft < f_hard`):**
- `f` = V-value ÷ (V-value + C-value), incl. reserve, **excl.** the gas buffer, marked at `p` (at
 external while the INV-13 tier is defensive).
- **Soft cap** (`f ≥ f_soft`): stop adding V — saturate skew to the sell side, widen, reduce size.
 Passive, costless.
- **Hard cap** (`f ≥ f_hard`): swap V→C back to `f_soft`, **only when the INV-13 tier is aligned/healthy**
 (else halt-and-hold). The one deliberately loss-accepting action; apply hysteresis to avoid thrash.
- **No lower cap on `f`.** Cash-heaviness carries no directional risk; re-accumulate V passively on dips,
 never market-buy.

**Calibration (starting values, tune on live data):** `f_hard ≈ tolerance ÷ stress` — e.g. tolerate a
`[15%]` drawdown against a `[30%]` V stress → `f_hard ≈ [50%]`; `f_soft = f_hard − [6%]`;
`f* = f_hard − [12%]`. A lower tolerance ⇒ lower, more cash-tilted caps.

**Gates & exits (do not override):** run `hodlmm-divergence-safety-runbook` every cycle (INV-13);
`crisis` regime or `lpSafety: avoid` ⇒ stand aside (Ch.4). When **fee-to-IL is persistently < 1**, this
is an **exit**, not a recenter (§3.1 / INV-9). At size, an *external* delta-hedge of the V exposure
(off-venue) is the standard way to neutralize IL — note it adds funding cost and operational surface and
is outside HODLMM. New-pair setup: run `hodlmm-pair-calibration-runbook` first; width/size floors come
from `hodlmm-adverse-selection-runbook`; wrapped/bridged peg safety from the shared `peg-monitor-runbook`.

### 3.3 Cross-cutting safety & recovery runbooks (not strategy profiles)

Run alongside whatever profile you pick — the first gates every write, the second recovers a failed one.

| Runbook | Run it | Role |
|---|---|---|
| `hodlmm-divergence-safety-runbook` | Every cycle, and before any write | Read-only gate → `proceed` / `force-defensive` / `halt`. Distinguishes feed lag from a decoupled/manipulated pool. |
| `hodlmm-stuck-transaction-runbook` | A broadcast is stuck / reverted / partial | Triage to root cause (underpriced → RBF; read-ceiling → replace bounded, **not** a fee bump; adversarial → widen/escalate). |
| `peg-monitor-runbook` (shared) | Any pool with a wrapped/bridged leg | Read-only peg monitor with independent refs → `ok/warn/break`; feeds INV-13. |

## 4. Capital routing & allocation

- Idle sBTC: compare HODLMM vs other venues before deploying — see the cross-protocol
  [`shared/` runbooks](../../shared/README.md) (e.g. sBTC yield routing).
- Multi-pool: size each position to its pool's liquidity and your exposure caps; don't fund a stale pool.

## 5. What good operation looks like

- Every write preceded by a passing pre-flight GATE; every action in **both ledgers** (INV-11).
- DLP mark-to-market tracked **separately** from earned fees (INV-8) — never conflated in reporting.
- Positions stay near the active bin (active profile) or within their intended range; inventory near target.
- `blocked` results (cooldowns, confirmations) are normal — they are the brakes working, not failures.
- Escalations are logged and acted on, not swallowed.

## 6. When to stop and escalate

Before escalating **repeated tx failures**, triage the root cause with `hodlmm-stuck-transaction-runbook`
— a read-ceiling or nonce issue has a deterministic fix, not a human one. Hand off to a human on: recovery
attempts exhausted, suspected fund-risk, security/key exposure, or any out-of-scope / ambiguous-authority
situation. See handbook **Ch.3 §3.6** (agent side) and **Ch.5** (operator side). Escalation is a valid end
state — never act unilaterally on those.

---

*This guide is a living document. Strategy profiles and cadences will expand as runbooks are added.
It defers to the handbook on every safety question.*
