---
name: HODLMM PnL Runbook
type: runbook
handbook: v0.8
enforces: [INV-7, INV-8, INV-10, INV-11, INV-12]
skills: [defi-portfolio-scanner, bitflow, query]
status: active
---

# HODLMM PnL Runbook

> Conforms to the [HODLMM Agent Handbook](../handbook/HODLMM-Agent-Handbook.md) **v0.8**.
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
6. **REPORT** — emit the **Campaign PnL Report** (medium-agnostic text/markdown; see "Report
   contract" below). This is the **primary, always-shipped deliverable** whenever the operator asks
   to run PnL or see campaign results, in **every** channel (CLI, Claude Code, an LLM turn, a GitHub
   issue, chat). Emit every component **separately** plus the headline ratios; `MUST NOT` collapse
   them into one number or present DLP mark-to-market as profit (INV-8). Re-read once if indexer lag
   is suspected rather than trusting a single snapshot (INV-10).
7. **EARNINGS CARD** *(optional; image channels only — TG/Discord/social)* — render the Step-6 report
   object as a branded Bitflow-style PNG. The card is **one renderer of the same object**, never a
   substitute for the text report: a PNG can only be seen where images render, so it must never be
   the sole output in a text channel. It is subordinate garnish, and it must show the **same
   hierarchy** as the report (net-vs-hold-after-gas as the hero; earnings/Fee-TVL as subordinate,
   non-additive context). See "Earnings Card" below. The card shows **Bitflow app-level fee
   attribution only** — always paired with the full component breakdown from step 6 (INV-8).
8. **REMEMBER** — write the Performance Ledger row + memory (running cost basis, `fee_confidence`
   trend, time-in-range) (INV-11/12).

## Expected outputs

A PnL report object — components never netted into one figure:

```
{ cost_basis, v_hold, v_position_no_fees, il_only_pnl,
  fee_pnl, fee_confidence, gas, net_pnl,
  fee_to_il_ratio, time_in_range_pct,
  final_inventory_mark, report_period, period_source }
```

- `v_hold` here is the **deployed-basis** value (the sole basis for `net_pnl` percentages — see the
  component-basis addendum). `report_period` is the elapsed/labeled window; `period_source` is
  `campaign` or `report`. `final_inventory_mark` is the exit/withdrawal-leg value.

- `fee_to_il_ratio > 1` ⇒ fees are covering divergence (the health signal the operating guide §3.1
  tracks).
- A **low `fee_confidence`** or missing cost basis is a reported caveat, not a fabricated number.

## Campaign PnL Report — contract (canonical output)

> The **honesty lives in the report, not in the card.** The card is only viewable where images
> render (TG/Discord); in CLI, Claude Code, an LLM turn, or a GitHub issue a PNG cannot be seen.
> So the text/markdown report below is the **primary deliverable** every time the operator asks to
> run PnL or see results, and the card (if any) renders this same object. Source: campaign-003
> closeout methodology sign-off ([#28](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/28)) and card-semantics proposal ([#37](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/37)).

**Visual/textual hierarchy — the same in every medium:**

1. **Hero — the sole headline metric:** `NET PnL after gas`, in the numeraire, with sign.
2. **Supporting line:** the percentage, explicitly labeled **`vs hold, after gas`**. The percentage
   denominator is the **deployed-basis `V_hold`** (tokens actually deposited, at closeout marks) —
   the only basis for percentages per the component-basis addendum below. Never the notional/intended
   size, never campaign-total basis.
3. **Core campaign rows:** campaign ID · report period + elapsed duration (see period label) ·
   **deployed hold baseline** (both the USD mark *and* the original native token inventory) · final
   inventory mark.
4. **Subordinate context — visibly non-additive to net:** `Earnings` (Bitflow app fee attribution) ·
   `Fee/TVL %` · `Gas` (STX *and* its marked USD value when price is available).

**Non-additivity is load-bearing.** `Earnings` and `Fee/TVL` are Bitflow's app-reported
fee-attribution flow, **not** components of campaign PnL, and must never be laid out so a reader
could add them to (or read them as) net. The canonical worked example makes this self-evident
precisely because earnings ≫ net:

```
HODLMM-DLMM1-20260702-003 · Campaign earnings · Jul 3–Jul 9 (6d 20h)

  NET PnL after gas:  +$9.05   (+11.6% vs hold, after gas)      ← hero
  Deployed hold baseline: $78.21   (123,853 sats + 0.111788 USDCx)
  Final inventory:        $87.76
  ── context — Bitflow attribution, NOT additive to net ──
  Earnings: $24.16    Fee/TVL: 39.70%    Gas: 3.0 STX (~$0.49)

  fee_confidence: <level>   ·   period source: campaign
```

Note `Earnings $24.16` ≫ `NET $9.05`: earnings is gross attributed fee flow; net is after IL and
gas. Presenting them as peers or summable would overstate the result.

**Period label — never hardcode `7D`.** Derive it from the source and record which:

- **Campaign basis** — entry timestamp → exit/report timestamp, e.g. `Campaign earnings · 6d 20h`.
- **Report basis** — the selected `1d`/`7d`/`30d` or a custom date range, e.g. `Report earnings · 7D`
  or `Report earnings · Jul 3–Jul 9`.
- The report header (and any card metadata) records the **period source** as `campaign` or `report`
  so a reviewer can tell which clock produced the earnings figure.

**Low-confidence / display-only guardrail.** If `fee_confidence` is low, or the earnings figure is
DLP/display-derived rather than realized, the `Earnings` line carries an explicit
**context-only, not realized** label (the dlmm_6 rule below). A card must never render a
realized-looking earnings figure that the report would caveat.

### Data provenance — the ledger is authoritative, the endpoint is context-only

There is **no endpoint for net-vs-hold** — Bitflow does not know your cost basis, deployed baseline,
gas, or campaign clock. Those come from the agent's **Transaction Ledger + memory** (INV-11/12),
written at OPEN and EXIT. Every field of the report maps to exactly one source, and the hierarchy is
strict:

| Report field | Source | Authority |
|---|---|---|
| net PnL after gas · `% vs hold` · deployed hold baseline (native amounts) · gas · entry/exit timestamps → period · final inventory | **agent ledger + memory** (OPEN/EXIT rows) | **authoritative — hero + core rows** |
| current per-bin token amounts · closeout price marks | on-chain reads + live quote | values the ledger amounts |
| `earningsUsd` / `feeTvl` / `tvlUsd` | **BFF `earnings/pnl` endpoint** | **subordinate context chips — optional** |

**Generator input contract.** The earnings-card script consumes the **Step-6 report object** (which
is ledger-derived) as its input; the BFF call is an *optional enrichment* for the two context chips
only. It **must not** derive the hero or any core row from the endpoint. If BFF is unavailable, times
out, or returns display-only figures, render the net-PnL card from the ledger alone and omit/grey the
earnings chip — never block, and never let the load-bearing number depend on an endpoint.

**Ledger prerequisite (OPEN/EXIT).** The closeout report/card is only constructible if the campaign
lifecycle wrote: at **OPEN** — deposited native amounts (cost basis), entry bins, entry timestamp;
across the run — cumulative gas; at **EXIT** — withdrawn/final amounts and exit timestamp. These are
INV-11 ledger fields; the entry and exit runbooks' `REMEMBER` steps persist them. A missing field is
a **reported low-confidence caveat**, never a fabricated value (INV-8).

## Failure handling

| Symptom | Handbook |
|---|---|
| Stale reads / lagging position or price | Ch.3 §3.4 (re-read after lag clears — never act on it) |
| Missing/partial ledger or cost-basis data | flag + report **low confidence**; never fabricate a basis |
| Position shows balances inconsistent with ledger | Ch.3 §3.4 (indexing latency — reconcile, don't assume loss) |
| Quote API returns empty `execution_path` / no DLMM price | fall back to `GET /pools/{id}` mid; flag pricing confidence |

## Earnings Card — Visual Reporting

Render a branded PNG of the **Step-6 Campaign PnL Report object** in the Bitflow app "share earnings"
style. Read-only — uses the same `GET /users/{wallet}/earnings/pnl/{pool}?period_type={period}`
endpoint as step 4. The card is **one renderer of the report, not a second source of truth**: it
must show the same hierarchy as the report contract (net-vs-hold-after-gas hero; earnings/Fee-TVL
subordinate and non-additive) so the two can never diverge.

> **Optional, and image-channels only.** A PNG is viewable only where images render (TG, Discord,
> social, a human opening the file). It is **never** the deliverable on its own in CLI, Claude Code,
> an LLM turn, or a GitHub issue — there the text report from step 6 is what ships. Generate the card
> as an *addition* when the channel supports images, never as a substitute.

> **Not a registry skill.** The card is produced directly from the BFF API below by a self-contained
> local render script (Pillow) — there is no `bitflow-earnings-card` entry in `aibtcdev/skills`, so it
> is not listed in this runbook's `skills:` frontmatter. Card layout, dynamic period label, spelling,
> and renderer tests live in that script (agent workspace `tools/earnings-card/`), not in this repo;
> this runbook governs the **data semantics** the script must honor.

### API

```
GET https://bff.bitflowapis.finance/api/app/v1/users/{wallet}/earnings/pnl/{pool}?period_type={period}
```

Periods: `1d`, `7d`, `30d`. Returns `earningsUsd`, `earningsBtc`, `feeTvl`, `tvlUsd`, range, binStep,
baseFee. **This endpoint supplies only the subordinate context chips** (`Earnings`, `Fee/TVL`) — it
knows nothing of your cost basis, hold baseline, gas, or campaign clock, so the hero and core rows
come from the ledger, never from here (see "Data provenance" above). **The displayed period is never
hardcoded** — it is derived per the report contract's period-label rule (campaign basis =
entry→exit timestamps from the ledger; report basis = the selected preset or custom range), and the
card records the period source (`campaign` / `report`).

### Generation

```bash
cd <workspace>/tools/earnings-card
python3 generate_card.py --wallet <SP-address> --pool <pool-id> --period <1d|7d|30d>
```

Output: `output/earnings-card-{pool}-{period}.png`

The script takes the **Step-6 report object** (ledger-derived) as its input, *optionally* calls the
BFF endpoint above for the two context chips, caches token icons, and renders the card (1200×675 dark
theme, overlapping token icons). Per the report contract, the **hero is `NET PnL after gas`** (from
the ledger) with a `vs hold, after gas` supporting line; the deployed hold baseline and final
inventory are core rows; and `Earnings` / `Fee/TVL %` / `Gas` are **subordinate footer chips laid out
so they cannot read as additive to net**. If the BFF call fails, render from the ledger and omit/grey
the earnings chip — never block. Spell the label **`Fee/TVL`** everywhere (no `Feel/TVL`).

### When to generate

Only as an *addition* to the step-6 text report, and only in an image-capable channel:

- User asks to "share my performance" / wants a visual for TG, Discord, or a social thread
- End-of-campaign wrap-up posted to an image channel (the text report still leads)
- Periodic visual summaries where images render

Do **not** generate a card as the answer in CLI, Claude Code, an LLM turn, or a GitHub issue — ship
the text report there. The card never travels without its report.

### Guardrails

- The card's `Earnings`/`Fee/TVL` show **Bitflow app fee attribution** — NOT the full PnL picture and
  NOT additive to net (they are subordinate chips; net-vs-hold-after-gas is the only hero).
- **Always pair** the card image with the component PnL report from step 6 (IL, fees, gas, net); the
  card renders that same object and must not diverge from it.
- Never present the card's earnings figure as campaign profit without the hold-baseline context (INV-8).
- Period label is derived, never assumed `7D`; the card records the period source (`campaign`/`report`).
- The API is read-only and keyless (beta). Cache results ≥5 min to be respectful of rate limits.

### Dependencies

```bash
pip install Pillow requests
```

Token icons are auto-cached in `tools/earnings-card/icons/` on first run.

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
- Out of range, IL is **realized**: the position has converted to one side (bins above active hold X
  only, bins below hold Y only — handbook §1.3 / V5; price rising past your range leaves you all-Y).
  Reflect that in `V_position(no fees)` rather than assuming a balanced pair.
- Pair with [`hodlmm-exit-runbook.md`](./hodlmm-exit-runbook.md) for end-of-campaign: account first
  (this runbook), then exit.

## Field-confirmed addendum — HODLMM-DLMM6-20260602-001

> Source: K9Dreamer `dlmm_6` closeout (issues #4/#5). Confirms the PnL-confidence direction
> from the Hex Stallion closeout (#1/#3) with a clean, fully-realized exit.

**Headline PnL is net-vs-original-hold after gas, at realized-withdrawal confidence.** This
campaign closed at **net −$1.25 vs holding the original tokens, after gas** (gross −$0.58; gas
3.6 STX / ~$0.667). Roughly flat: fee capture ≈ offset the one-sided/IL drag as STX/USD fell.

**DLP balance and protocol display earnings are context only — never realized fee income.** The
BFF 30-day display read showed `$27.01` / `0.00043235 BTC` while realized net-vs-hold was ≈flat.
Report display earnings separately and labeled; never headline them.

**Closure proof = wallet DLP for the pool is zero AND the withdraw tx is chain-confirmed.**
Protocol status/position endpoints may lag (this campaign's Bitflow status still showed TVL after
a confirmed exit). A lagging status read is advisory and must not trigger a duplicate exit.

**Volatility capture is not yield.** When a campaign's profit comes from price leaving the range
and re-entering it (one-sided ladders converting token→token up the bins and back), the headline
stays net-vs-original-hold after gas at realized confidence — and the report must **name the source
as volatility capture**. Never annualize or project it as baseline APR: the same position under a
one-way move would read materially negative vs hold. Field case (K9Dreamer dlmm_3 campaign-002,
issues #21/#22): net **+$6.31 vs hold after gas, realized** (~+13% on deployed in 7 days), produced
entirely by two full out-of-range round trips monetized with zero recenter spend — reported as
windfall capture, not as a repeatable return.

## Field-confirmed addendum — component basis conventions (HODLMM-DLMM1-20260702-003)

> Source: K9Dreamer `dlmm_1` campaign-003 closeout
> ([#28](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/28),
> methodology sign-off in the follow-up comments). Trigger: a downstream analyzer and the closeout
> report published different hold/exit component values from the same campaign — both internally
> correct, on different bases and different same-day marks.

**State the basis for every PnL component.** Two legitimate bases exist and they answer different
questions:

- **Deployed basis** (attribution): `V_hold` = the tokens actually deposited, at closeout marks;
  `V_exit` = the exit-withdrawal leg. This is the runbook's canonical `V_hold` and the ONLY basis
  for percentages and return-on-capital claims — idle inventory did not earn the result and must
  not dilute (or pad) it.
- **Campaign-total basis** (reconciliation): add the untouched idle reserve to BOTH sides. Use it
  to prove the wallet reconciles and nothing leaked; never for percentages.

The net delta is **identical under both bases at any common mark** (the idle reserve cancels), so
the headline is basis-invariant — but component absolutes are not, and unlabeled components from
different bases (or different same-day marks) will look like an accounting error to any reviewer.
Field case: analyzer components `$51.98/$60.98` vs report components `$78.21/$87.76` reconciled
exactly as deployed-basis vs campaign-total at two BTC marks ~1.4% apart; gross was `+$9` on both.

**Verify "no intermediate legs" at the event level before using the deployed basis naively.**
Atomic native recenters (`move-liquidity-multi`) emit only pool-token/DLP events — zero wallet
inventory movements — so deployed-basis accounting stays clean across any number of them (field
check: two repair txs, 429 and 442 events, zero wallet fungible-token legs). A recenter routed
withdraw→redeposit DOES touch the wallet and must be netted out explicitly (see the dlmm_3
campaign-002 accounting, #21).
