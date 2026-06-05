---
name: HODLMM PnL Runbook
type: runbook
handbook: v0.6
enforces: [INV-7, INV-8, INV-10, INV-11, INV-12]
skills: [defi-portfolio-scanner, bitflow, query, bitflow-earnings-card]
status: draft
---

# HODLMM PnL Runbook

> Conforms to the [HODLMM Agent Handbook](../handbook/HODLMM-Agent-Handbook.md) **v0.6**.
> Enforces: INV-7, INV-8, INV-10, INV-11, INV-12.

## Purpose

Produce honest PnL accounting for a HODLMM LP position — separating **earned fees** from
**impermanent loss** from **gas** — so the agent never reports DLP mark-to-market as profit (INV-8).
Read-only: this runbook **never broadcasts**.

## When to run / when NOT to run

- **Run when:** end of a campaign, before/after an exit, or on the regular MEASURE cycle to refresh
  the Performance Ledger; whenever you need a true profit number rather than a balance.
- **Do NOT run when:** you actually want to *act* (recenter, rebalance, exit) — this runbook only
  measures. It produces no transaction and grants no authority.
- Reads the IL definition from handbook **§6.6** (and fee attribution from **§6.2**); it does not
  restate the math.

## Inputs

| Param | Meaning | Default |
|---|---|---|
| `wallet` | position-holding address | — |
| `pool-id` | pool to account for | — |
| `numeraire` | asset to value everything in (e.g. the pool's base token) | pool base asset |
| `since` | campaign start / cost-basis epoch | first deposit in the Transaction Ledger |

## Required Approval Scope (INV-1)

- **None.** This is a read-only accounting pass — no signing, no broadcast, no scope required.
- It reads on-chain position state, public quote data, and the agent's own ledgers. It must **never**
  unlock a signer or submit a transaction. If asked to "fix" PnL, hand off to the relevant action
  runbook (recenter / inventory-balancing / exit) — accounting does not act.

## Gates — run BEFORE compute

The read-only subset of the handbook pre-flight GATE (link, don't restate):

```
[ ] Fresh scan this iteration; indexer lag checked — stale ⇒ wait/flag (INV-7)
[ ] Cost-basis source present (Transaction Ledger); else flag low confidence (INV-11/12)
[ ] Numeraire + current price resolved from a live quote (INV-7)
[ ] No signer touched — read-only confirmed
[ ] Performance Ledger row prepared (INV-11)
```

## Procedure

Read-only — no `--confirm`, no broadcast. Cites handbook §6.6 for the IL definition.

1. **COST BASIS** — from the Transaction Ledger (INV-11), get the original deposited amounts for the
   position; value them at the **current** price → `V_hold`. `query` / `defi-portfolio-scanner` for
   ledger + balances; `bitflow get-quote` (or `GET /pools/{id}` mid) for current price.
2. **POSITION VALUE (excluding fees)** — read current per-bin token amounts
   (`GET /users/{addr}/positions/{pool}/bins`, handbook §1.4) and value them at the current price →
   `V_position(no fees)`. Per-bin, never aggregate DLP (INV-8). `defi-portfolio-scanner` / `bitflow
   get-hodlmm-position-bins`.
3. **IL-ONLY PnL** = `V_position(no fees) − V_hold` *(per handbook §6.6).* This is divergence, not a
   fee and not a cost line.
4. **FEE PnL** — attribute earned fees from the growth in the bins' reserves net of price moves, and
   record a **`fee_confidence`** (§6.2, INV-8). There is no claim/FT-transfer event — attribution is
   derived. **Never read DLP balance as fees.**
5. **NET PnL** = `IL-only PnL + Fee PnL − gas` (cumulative gas from the Transaction Ledger).
6. **REPORT** — emit every component **separately** plus the headline ratios. `MUST NOT` collapse them
   into one number or present DLP mark-to-market as profit (INV-8). Re-read once if indexer lag is
   suspected rather than trusting a single snapshot (INV-10).
7. **EARNINGS CARD** *(optional, recommended for sharing)* — generate a visual Bitflow-style earnings
   card for the position. This is a branded PNG matching the official Bitflow app "share" card
   layout (see procedure below). Generate when the user asks for earnings, for periodic campaign
   reports, or for social sharing. The card shows **Bitflow app-level fee attribution only** — always
   pair it with the full component breakdown from step 6 so DLP mark-to-market is never presented
   as profit (INV-8).
8. **REMEMBER** — write the Performance Ledger row + memory (running cost basis, `fee_confidence`
   trend, time-in-range) (INV-11/12).

## Expected outputs

A PnL report object — components never netted into one figure:

```
{ cost_basis, v_hold, v_position_no_fees, il_only_pnl,
  fee_pnl, fee_confidence, gas, net_pnl,
  fee_to_il_ratio, time_in_range_pct }
```

- `fee_to_il_ratio > 1` ⇒ fees are covering divergence (the health signal the operating guide §3.1
  tracks).
- A **low `fee_confidence`** or missing cost basis is a reported caveat, not a fabricated number.

## Failure handling

| Symptom | Handbook |
|---|---|
| Stale reads / lagging position or price | Ch.3 §3.4 (re-read after lag clears — never act on it) |
| Missing/partial ledger or cost-basis data | flag + report **low confidence**; never fabricate a basis |
| Position shows balances inconsistent with ledger | Ch.3 §3.4 (indexing latency — reconcile, don't assume loss) |
| Quote API returns empty `execution_path` / no DLMM price | fall back to `GET /pools/{id}` mid; flag pricing confidence |

## Earnings Card — Visual Reporting

Generate a branded PNG card matching the Bitflow app "share earnings" style. Read-only — uses the
same `GET /users/{wallet}/earnings/pnl/{pool}?period_type={period}` endpoint as step 4.

### API

```
GET https://bff.bitflowapis.finance/api/app/v1/users/{wallet}/earnings/pnl/{pool}?period_type={period}
```

Periods: `1d`, `7d`, `30d`. Returns `earningsUsd`, `earningsBtc`, `feeTvl`, `tvlUsd`, range, binStep,
baseFee.

### Generation

```bash
cd <workspace>/skills/bitflow-earnings-card
python3 generate_card.py --wallet <SP-address> --pool <pool-id> --period <1d|7d|30d>
```

Output: `output/bitflow-earnings-card-{pool}-{period}.png`

The script fetches live data → caches token icons → renders the card (1200×675 dark theme, green hero
earnings figure, overlapping token icons, footer stat chips: FEE/TVL %, YOUR TVL, RANGE, BIN STEP, FEE).

### When to generate

- User asks for earnings, PnL, or "share my performance"
- End-of-campaign wrap-up (pair with the full PnL component breakdown)
- Periodic reports (daily/weekly summaries)
- Social content (X threads, Discord, Telegram)

### Guardrails

- The card shows **Bitflow app fee attribution** — it is NOT the full PnL picture.
- **Always pair** the card image with the component PnL report from step 6 (IL, fees, gas, net).
- Never present the card's earnings figure as campaign profit without the hold-baseline context (INV-8).
- The API is read-only and keyless (beta). Cache results ≥5 min to be respectful of rate limits.

### Dependencies

```bash
pip install Pillow requests
```

Token icons are auto-cached in `skills/bitflow-earnings-card/icons/` on first run.

## Idempotency / cooldown

- **Always safe to re-run** — read-only, no state mutation, no cooldown. Each run is a fresh snapshot;
  persist the series, don't overwrite history.
- Never let an accounting pass trigger a write. If the numbers argue for action, that's a *separate*
  runbook with its own scope + GATE.

## Notes

- **Earnings Card** requires `Pillow` and `requests` — both are standard Python packages. The
  `generate_card.py` script is self-contained: API fetch → icon cache → PNG render. No wallet
  unlock or signing needed.
- The `impermanentLossEstimatePct` from `hodlmm-risk` is a **monitoring proxy** (`driftScore × 0.08`,
  handbook §6.3/§6.6), not a true price-ratio IL — use the empirical per-bin computation here for
  reporting, the proxy only for cheap cycle-to-cycle monitoring.
- Out of range, IL is **realized**: the position has converted to one side (above active = Y only,
  below = X only — handbook §1.3 / V5). Reflect that in `V_position(no fees)` rather than assuming a
  balanced pair.
- Pair with [`hodlmm-exit-runbook.md`](./hodlmm-exit-runbook.md) for end-of-campaign: account first
  (this runbook), then exit.
