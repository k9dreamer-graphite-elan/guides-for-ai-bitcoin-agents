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

import re
from datetime import datetime, timezone

# ---------------------------------------------------------------------------
# Report object schema — the inputs this module consumes
# ---------------------------------------------------------------------------
# Card shape (v1, this tool's native input):
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
#   "fee_confidence": "high",                               # optional; "low" ⇒ guardrail
#   "period": {"source": "campaign",                        # or "report"
#              "entry_ts": "2026-07-03T04:03:00Z",
#              "exit_ts":  "2026-07-10T00:03:00Z",
#              "preset": null,                              # "1d"/"7d"/"30d"/custom
#              "label": null},                              # explicit override
#   "context": {"earnings_usd": 24.16, "fee_tvl_pct": 39.70,
#               "tvl_usd": null, "realized": false}          # optional (BFF)
# }
#
# Canonical hodlmm-pnl-runbook Step-6 shape ("Expected outputs") is ALSO
# accepted and adapted automatically (see adapt_step6_report):
# { cost_basis, v_hold, v_position_no_fees, il_only_pnl,
#   fee_pnl, fee_confidence, gas, net_pnl,                  # net_pnl is a SCALAR
#   fee_to_il_ratio, time_in_range_pct,
#   final_inventory_mark, report_period, period_source }

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


def safe_name(value, fallback: str) -> str:
    """Reduce untrusted report values (campaign ids, token symbols) to a safe
    filename fragment — they may originate from on-chain memo data and must
    never traverse out of the tool's output/icons directories."""
    cleaned = re.sub(r"[^A-Za-z0-9._-]", "_", str(value or "")).strip("._") or fallback
    return cleaned[:80]


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


def _is_low_confidence(fee_confidence) -> bool:
    """The runbook's display-only guardrail trigger: an explicit low `fee_confidence`."""
    return fee_confidence is not None and str(fee_confidence).strip().lower() == "low"


def _build_chips(gas: dict, context: dict | None, fee_confidence=None) -> list[dict]:
    context = context or {}

    earnings = context.get("earnings_usd")
    realized = bool(context.get("realized", False))
    # Runbook guardrail: low fee_confidence OR display-derived (not realized)
    # ⇒ Earnings is context-only. A card must never render a realized-looking
    # earnings figure that the report would caveat (INV-8).
    context_only = (not realized) or _is_low_confidence(fee_confidence)
    if earnings is not None:
        earn_chip = _chip(f"Earnings {_money(earnings)}", True, context_only=context_only)
    else:
        # BFF absent/failed — render honestly rather than block.
        earn_chip = _chip("Earnings n/a", False, context_only=True)

    fee_tvl = context.get("fee_tvl_pct")
    fee_chip = (_chip(f"Fee/TVL {float(fee_tvl):.2f}%", True) if fee_tvl is not None
                else _chip("Fee/TVL n/a", False))

    gas = gas or {}
    stx = gas.get("stx")
    if stx is not None and gas.get("usd") is not None:
        gas_chip = _chip(f"Gas {_num(stx)} STX (~{_money(gas['usd'])})", True)
    elif stx is not None:
        gas_chip = _chip(f"Gas {_num(stx)} STX", True)
    elif gas.get("usd") is not None:
        gas_chip = _chip(f"Gas {_money(gas['usd'])}", True)
    else:
        gas_chip = _chip("Gas n/a", False)

    # Order matters: Earnings and Fee/TVL are Bitflow attribution; Gas is a
    # real cost already inside net — it sits here only to keep net uncluttered.
    return [earn_chip, fee_chip, gas_chip]


# ---------------------------------------------------------------------------
# Canonical Step-6 report adapter
# ---------------------------------------------------------------------------
def adapt_step6_report(report: dict) -> dict:
    """Adapt the canonical `hodlmm-pnl-runbook` Step-6 output object (scalar
    `net_pnl`, top-level `v_hold` / `final_inventory_mark` / `report_period` /
    `period_source`) into this tool's card shape. Reports already in the card
    shape (dict `net_pnl`) pass through unchanged.
    """
    if not isinstance(report, dict) or isinstance(report.get("net_pnl"), dict):
        return report
    if not any(k in report for k in ("v_hold", "final_inventory_mark",
                                     "report_period", "period_source")):
        return report  # card shape with a malformed net_pnl — let validation speak

    adapted = dict(report)
    net_usd = float(report["net_pnl"]) if report.get("net_pnl") is not None else None
    v_hold = report.get("v_hold")
    net = {"usd": net_usd}
    if net_usd is not None and v_hold:
        # Deployed basis (`v_hold`) is the only basis for percentages
        # (component-basis addendum).
        net["pct_vs_hold"] = net_usd / float(v_hold) * 100.0
    adapted["net_pnl"] = net

    if v_hold is not None and "deployed_hold_baseline" not in adapted:
        adapted["deployed_hold_baseline"] = {"usd": float(v_hold)}
    if report.get("final_inventory_mark") is not None and "final_inventory" not in adapted:
        adapted["final_inventory"] = {"usd": float(report["final_inventory_mark"])}

    gas = report.get("gas")
    if gas is not None and not isinstance(gas, dict):
        # Canonical NET = IL + fees − gas is computed in the numeraire, so a
        # scalar gas is a numeraire (USD) mark, not an STX quantity.
        adapted["gas"] = {"usd": float(gas)}

    if "period" not in adapted:
        adapted["period"] = {"source": report.get("period_source") or "report",
                             "label": report.get("report_period")}
    return adapted


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------
def build_card_model(report: dict, bff_context: dict | None = None) -> dict:
    """Compose the render-ready card model from a ledger-derived report object.

    Accepts either the card shape or the canonical Step-6 object (see
    adapt_step6_report). `bff_context`, if given, is merged over
    `report['context']` — it only ever fills the subordinate chips, never the
    hero or core rows.
    """
    report = adapt_step6_report(report)
    if not report or report.get("net_pnl") is None:
        raise ValueError(
            "report object missing 'net_pnl' — the card hero is net-vs-hold and "
            "MUST come from the agent's ledger (hodlmm-pnl-runbook Step 6), not "
            "from any endpoint."
        )

    net = report["net_pnl"]
    if not isinstance(net, dict) or net.get("usd") is None:
        raise ValueError(
            "report 'net_pnl' must carry a numeraire value ('usd') — a ledger-"
            "derived net-vs-hold figure is required (hodlmm-pnl-runbook Step 6)."
        )
    net_usd = float(net["usd"])
    pct = net.get("pct_vs_hold")
    fee_confidence = report.get("fee_confidence")

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

    chips = _build_chips(report.get("gas"), context, fee_confidence)

    # Footer mirrors the report contract's caveat line:
    # `fee_confidence: <level> · period source: campaign`
    footer_bits = []
    if fee_confidence is not None:
        footer_bits.append(f"fee_confidence: {fee_confidence}")
    footer_bits.append(f"period source: {period['source']}")

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
        "fee_confidence": fee_confidence,
        "footer": " · ".join(footer_bits),
        "earnings_context_only": any(
            c["available"] and c["context_only"] and c["label"].startswith("Earnings")
            for c in chips
        ),
    }
