"""Bitflow Earnings Card — card model (pure logic, no I/O).

Turns a **ledger-derived PnL report object** (produced by the agent following
`hodlmm-pnl-runbook` Step 6) into the exact display strings/flags the renderer
draws. Kept free of network and Pillow so it is unit-testable.

Data-provenance contract (see the PnL runbook "Data provenance" section):
  - The hero (NET PnL after gas) and every core row come from the agent's
    Transaction Ledger + memory — there is NO endpoint for net-vs-hold.
  - Bitflow's `earnings/pnl` endpoint supplies ONLY the subordinate context
    chips (Earnings, Fee/TVL). They are optional and NON-ADDITIVE to net.
"""
from __future__ import annotations

from datetime import datetime, timezone

# ---------------------------------------------------------------------------
# Report object schema (v1) — the input this module consumes
# ---------------------------------------------------------------------------
# {
#   "campaign_id": "HODLMM-DLMM1-20260702-003",
#   "wallet": "SP...", "pool": "dlmm_1",
#   "pair": {"x": {"symbol": "sBTC", "image": "..."},
#            "y": {"symbol": "USDCx", "image": "..."}},
#   "numeraire": "USD",
#   "net_pnl":  {"usd": 9.05, "pct_vs_hold": 11.6},         # deployed basis
#   "deployed_hold_baseline": {"usd": 78.21,
#                              "native": "123,853 sats + 0.111788 USDCx"},
#   "final_inventory": {"usd": 87.76},
#   "gas": {"stx": 3.0, "usd": 0.49},
#   "period": {"source": "campaign",                        # or "report"
#              "entry_ts": "2026-07-03T04:03:00Z",
#              "exit_ts":  "2026-07-10T00:03:00Z",
#              "preset": null,                              # "1d"/"7d"/"30d"/custom
#              "label": null},                              # explicit override
#   "context": {"earnings_usd": 24.16, "fee_tvl_pct": 39.70,
#               "tvl_usd": null, "realized": false}          # optional (BFF)
# }

CONTEXT_DIVIDER = "context — Bitflow attribution · not additive to net"


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------
def _money(x) -> str:
    return f"${x:,.2f}"


def _signed_money(x) -> str:
    sign = "+" if x >= 0 else "−"  # U+2212 minus for display
    return f"{sign}{_money(abs(x))}"


def _signed_pct(x) -> str:
    sign = "+" if x >= 0 else "−"
    return f"{sign}{abs(x):.1f}%"


def _num(x) -> str:
    """Trim trailing .0 from whole numbers (3.0 -> '3', 2.5 -> '2.5')."""
    f = float(x)
    return str(int(f)) if f == int(f) else f"{f:g}"


def _parse_ts(s: str) -> datetime:
    """Parse an ISO-8601 timestamp, tolerating a trailing 'Z'."""
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    dt = datetime.fromisoformat(s)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def _fmt_day(dt: datetime) -> str:
    return f"{dt.strftime('%b')} {dt.day}"


def _date_range(a: datetime, b: datetime) -> str:
    return f"{_fmt_day(a)}–{_fmt_day(b)}"


def _elapsed(a: datetime, b: datetime) -> str:
    secs = int((b - a).total_seconds())
    if secs < 0:
        secs = 0
    d, rem = divmod(secs, 86400)
    h, rem = divmod(rem, 3600)
    m = rem // 60
    if d > 0:
        return f"{d}d {h}h"
    if h > 0:
        return f"{h}h {m}m"
    return f"{m}m"


# ---------------------------------------------------------------------------
# Period label — NEVER hardcode "7D"
# ---------------------------------------------------------------------------
def derive_period(period: dict) -> dict:
    """Return {'source', 'label'} for the report/card.

    - campaign basis: entry→exit timestamps -> 'Campaign · Jul 3–Jul 10 · 6d 20h'
    - report basis:   preset -> 'Report · 7D'; custom range -> dates + elapsed
    An explicit `label` override wins but is still prefixed by the source word.
    """
    period = period or {}
    source = (period.get("source") or "report").lower()
    prefix = "Campaign" if source == "campaign" else "Report"

    override = period.get("label")
    if override:
        return {"source": source, "label": f"{prefix} · {override}"}

    entry, exit_ = period.get("entry_ts"), period.get("exit_ts")
    if entry and exit_:
        a, b = _parse_ts(entry), _parse_ts(exit_)
        return {"source": source,
                "label": f"{prefix} · {_date_range(a, b)} · {_elapsed(a, b)}"}

    preset = period.get("preset")
    if preset:
        return {"source": source, "label": f"{prefix} · {str(preset).upper()}"}

    # No timestamps, no preset — honest fallback, still no assumed 7D.
    return {"source": source, "label": prefix}


# ---------------------------------------------------------------------------
# Chips — subordinate context, greyed when unavailable
# ---------------------------------------------------------------------------
def _chip(label: str, available: bool, context_only: bool = False) -> dict:
    return {"label": label, "available": available, "context_only": context_only}


def _build_chips(gas: dict, context: dict | None) -> list[dict]:
    context = context or {}

    earnings = context.get("earnings_usd")
    realized = bool(context.get("realized", False))
    if earnings is not None:
        earn_chip = _chip(f"Earnings {_money(earnings)}", True, context_only=not realized)
    else:
        # BFF absent/failed — render honestly rather than block.
        earn_chip = _chip("Earnings n/a", False, context_only=True)

    fee_tvl = context.get("fee_tvl_pct")
    fee_chip = (_chip(f"Fee/TVL {float(fee_tvl):.2f}%", True) if fee_tvl is not None
                else _chip("Fee/TVL n/a", False))

    gas = gas or {}
    stx = gas.get("stx")
    if stx is None:
        gas_chip = _chip("Gas n/a", False)
    elif gas.get("usd") is not None:
        gas_chip = _chip(f"Gas {_num(stx)} STX (~{_money(gas['usd'])})", True)
    else:
        gas_chip = _chip(f"Gas {_num(stx)} STX", True)

    # Order matters: Earnings and Fee/TVL are Bitflow attribution; Gas is a
    # real cost already inside net — it sits here only to keep net uncluttered.
    return [earn_chip, fee_chip, gas_chip]


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------
def build_card_model(report: dict, bff_context: dict | None = None) -> dict:
    """Compose the render-ready card model from a ledger-derived report object.

    `bff_context`, if given, is merged over `report['context']` — it only ever
    fills the subordinate chips, never the hero or core rows.
    """
    if not report or "net_pnl" not in report:
        raise ValueError(
            "report object missing 'net_pnl' — the card hero is net-vs-hold and "
            "MUST come from the agent's ledger (hodlmm-pnl-runbook Step 6), not "
            "from any endpoint."
        )

    net = report["net_pnl"]
    net_usd = float(net["usd"])
    pct = net.get("pct_vs_hold")

    # Merge context: report's own context first, BFF enrichment over it.
    context = dict(report.get("context") or {})
    if bff_context:
        context.update({k: v for k, v in bff_context.items() if v is not None})

    period = derive_period(report.get("period"))

    hold = report.get("deployed_hold_baseline") or {}
    final = report.get("final_inventory") or {}
    pair = report.get("pair") or {}

    rows = [("Period", period["label"])]
    if hold.get("usd") is not None:
        native = hold.get("native")
        baseline = _money(hold["usd"]) + (f"  ·  {native}" if native else "")
        rows.append(("Deployed hold baseline", baseline))
    if final.get("usd") is not None:
        rows.append(("Final inventory", _money(final["usd"])))

    chips = _build_chips(report.get("gas"), context)

    return {
        "campaign_id": report.get("campaign_id", ""),
        "pair": {
            "x_symbol": pair.get("x", {}).get("symbol", "X"),
            "y_symbol": pair.get("y", {}).get("symbol", "Y"),
            "x_image": pair.get("x", {}).get("image", ""),
            "y_image": pair.get("y", {}).get("image", ""),
        },
        "hero": {"text": _signed_money(net_usd), "positive": net_usd >= 0},
        "hero_label": "NET PnL · after gas",
        "pct_line": (f"{_signed_pct(pct)} vs hold, after gas" if pct is not None
                     else "vs hold, after gas"),
        "rows": rows,
        "context_divider": CONTEXT_DIVIDER,
        "chips": chips,
        "period_source": period["source"],
        "earnings_context_only": any(
            c["context_only"] and c["label"].startswith("Earnings") for c in chips
        ),
    }
