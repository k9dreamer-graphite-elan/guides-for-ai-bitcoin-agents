# HODLMM Operating Guide

> The field manual: how to operate on HODLMM day-to-day, and **which runbook to run when**.
> Conforms to the [HODLMM Agent Handbook](../handbook/HODLMM-Agent-Handbook.md) **v0.6** — this guide
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
  cycle is stale — re-derive it (INV-7).

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

Hand off to a human on: repeated tx failures, suspected fund-risk, security/key exposure, or any
out-of-scope / ambiguous-authority situation. See handbook **Ch.3 §3.6** (agent side) and **Ch.5**
(operator side). Escalation is a valid end state — never act unilaterally on those.

---

*This guide is a living document. Strategy profiles and cadences will expand as runbooks are added.
It defers to the handbook on every safety question.*
