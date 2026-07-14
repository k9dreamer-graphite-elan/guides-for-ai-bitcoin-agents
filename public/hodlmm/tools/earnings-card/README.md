# Earnings Card — reference implementation

A small, dependency-light **reference implementation** of the Campaign PnL Report
contract from [`hodlmm-pnl-runbook`](../../runbooks/hodlmm-pnl-runbook.md). It
renders a **ledger-derived report object** into a branded Bitflow-style card PNG.

It exists to make the contract *executable*: the honest hierarchy (NET PnL after
gas is the hero; Bitflow's Earnings/Fee-TVL are subordinate, non-additive chips)
is enforced in code and covered by tests, not just described in prose. Copy it
into your own agent workspace and adapt — it is illustrative, not a dependency of
the guides.

## Why a report object, not an API call

There is **no endpoint for net-vs-hold** — Bitflow doesn't know your cost basis,
deployed baseline, gas, or campaign clock. Those live in the agent's **Transaction
Ledger + memory** (INV-11/12). So the card renders a report object the agent
builds per `hodlmm-pnl-runbook` Step 6; the BFF `earnings/pnl` endpoint is an
**optional** enrichment that fills only the Earnings / Fee-TVL chips and degrades
to greyed `n/a` when absent. The load-bearing number never depends on an endpoint.

## Run

```bash
cd public/hodlmm/tools/earnings-card
python3 generate_card.py --report examples/report-dlmm_1-003.json --no-bff   # ledger-only
python3 generate_card.py --report examples/report-dlmm_1-003.json            # with BFF enrichment
cat report.json | python3 generate_card.py --report -                        # stdin
python3 -m unittest discover -s tests -v                                     # tests (stdlib)
```

Dependencies: `Pillow` (render) and `requests` (optional BFF enrichment only — ledger-only
`--no-bff` rendering works without it). See [`requirements.txt`](requirements.txt).

Default output filenames are keyed on `campaign_id` alone, which is **wallet-scoped, not globally
unique** (memo-tag spec, "Identity scoping") — when rendering cards for more than one agent into a
shared directory, pass `--output` with the agent/wallet in the path.

## Report object

Two input shapes are accepted:

1. **The card shape (v1)** — see [`examples/report-dlmm_1-003.json`](examples/report-dlmm_1-003.json)
   and the table below.
2. **The canonical `hodlmm-pnl-runbook` Step-6 object** (`{cost_basis, v_hold, …, net_pnl,
   final_inventory_mark, report_period, period_source}`, scalar `net_pnl`) — adapted automatically
   by `card_model.adapt_step6_report` (`v_hold` → deployed hold baseline and the percentage
   denominator; `final_inventory_mark` → final inventory; `report_period`/`period_source` →
   period label). A report's `fee_confidence` drives the display-only guardrail: `low` forces the
   Earnings chip to context-only, and the caveat renders in the card footer.

Key fields (card shape):

| Field | Source | Role |
|---|---|---|
| `net_pnl.usd` / `.pct_vs_hold` | ledger + memory | **hero** — `% ` is on the deployed basis, the only basis for percentages |
| `deployed_hold_baseline` `{usd, native}` · `final_inventory.usd` · `gas {stx, usd}` | ledger + memory | core rows |
| `period` `{source, entry_ts, exit_ts \| preset}` | ledger | period label — `campaign` vs `report`; **never assumes `7D`** |
| `context` `{earnings_usd, fee_tvl_pct, realized}` | **BFF (optional)** | subordinate chips; `realized:false` ⇒ shown as context-only |

## Files

- `card_model.py` — pure report-object → render-model logic (unit-tested; no I/O)
- `render_card.py` — Pillow renderer (model → PNG)
- `generate_card.py` — CLI: load report → optional BFF enrichment → render
- `tests/` — stdlib `unittest` suite (period labels, hero, greying, non-additivity, `Fee/TVL`, gas)
- `examples/report-dlmm_1-003.json` — sample report (the dlmm_1 campaign-003 worked example)

The card **must not** lay Earnings/Fee-TVL where they could read as additive to
net (INV-8); the renderer separates them under a `not additive to net` divider.
