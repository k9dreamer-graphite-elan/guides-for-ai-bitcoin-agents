#!/usr/bin/env python3
"""Bitflow Earnings Card — generator.

Renders a **ledger-derived PnL report object** into a branded card PNG. The hero
is NET PnL after gas (which only the agent's Transaction Ledger + memory know —
there is no endpoint for net-vs-hold). The Bitflow `earnings/pnl` endpoint is an
OPTIONAL enrichment that fills only the subordinate Earnings/Fee-TVL chips; if it
is unavailable the card still renders honestly from the ledger, greying those
chips.

Usage:
    python3 generate_card.py --report report.json [--output card.png]
    python3 generate_card.py --report report.json --no-bff        # ledger only
    cat report.json | python3 generate_card.py --report -          # stdin

`--wallet` / `--pool` / `--period` are used ONLY for the optional BFF enrichment
call (falling back to fields inside the report object if present).

See ../../../guides .../hodlmm-pnl-runbook.md ("Data provenance") and SKILL.md.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).parent))
from card_model import build_card_model
from render_card import render_card

SKILL_DIR = Path(__file__).parent
ICON_DIR = SKILL_DIR / "icons"
OUTPUT_DIR = SKILL_DIR / "output"

BFF_BASE = "https://bff.bitflowapis.finance/api/app/v1"
PERIOD_MAP = {"1d": "1d", "7d": "7d", "30d": "30d",
              "1D": "1d", "7D": "7d", "30D": "30d"}


def fetch_bff_context(wallet: str, pool: str, period: str) -> dict | None:
    """Fetch ONLY the subordinate context chips from Bitflow. Never raises —
    returns None on any failure so the card degrades to ledger-only."""
    try:
        url = f"{BFF_BASE}/users/{wallet}/earnings/pnl/{pool}"
        resp = requests.get(url, params={"period_type": PERIOD_MAP.get(period, period)}, timeout=15)
        resp.raise_for_status()
        raw = resp.json()
    except Exception as e:  # noqa: BLE001 — enrichment is best-effort
        print(f"Warning: BFF enrichment unavailable ({e}); rendering ledger-only.", file=sys.stderr)
        return None

    def _f(*keys):
        for k in keys:
            if k in raw and raw[k] not in (None, ""):
                try:
                    return float(raw[k])
                except (TypeError, ValueError):
                    return raw[k]
        return None

    return {
        "earnings_usd": _f("earningsUsd", "earnings_usd"),
        "fee_tvl_pct": _f("feeTvl", "fee_tvl"),
        "tvl_usd": _f("tvlUsd", "tvl_usd"),
        # Bitflow's figure is app-level fee attribution: context-only, not realized.
        "realized": False,
    }


def fetch_icon(url: str, name: str) -> Path | None:
    ICON_DIR.mkdir(parents=True, exist_ok=True)
    icon_path = ICON_DIR / f"{name}.png"
    if icon_path.exists():
        return icon_path
    if not url:
        return None
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        icon_path.write_bytes(resp.content)
        return icon_path
    except Exception as e:  # noqa: BLE001
        print(f"Warning: could not fetch icon for {name}: {e}", file=sys.stderr)
        return None


def load_report(path: str) -> dict:
    text = sys.stdin.read() if path == "-" else Path(path).read_text()
    return json.loads(text)


def main() -> int:
    p = argparse.ArgumentParser(description="Render a ledger-derived PnL report as a Bitflow card")
    p.add_argument("--report", required=True,
                   help="Path to the ledger-derived PnL report JSON (or '-' for stdin). "
                        "Produced per hodlmm-pnl-runbook Step 6.")
    p.add_argument("--no-bff", action="store_true", help="Skip BFF enrichment; render ledger-only")
    p.add_argument("--wallet", default=None, help="Wallet for the optional BFF enrichment call")
    p.add_argument("--pool", default=None, help="Pool id for the optional BFF enrichment call")
    p.add_argument("--period", default=None, help="Period for the optional BFF enrichment call")
    p.add_argument("--output", default=None, help="Output PNG path (auto-named if omitted)")
    p.add_argument("--model-out", default=None, help="Also write the computed card model JSON here")
    args = p.parse_args()

    report = load_report(args.report)

    # Optional BFF enrichment — only if the report doesn't already carry context.
    bff_context = None
    if not args.no_bff and not report.get("context"):
        wallet = args.wallet or report.get("wallet")
        pool = args.pool or report.get("pool")
        period = args.period or (report.get("period") or {}).get("preset") or "7d"
        if wallet and pool:
            bff_context = fetch_bff_context(wallet, pool, period)

    model = build_card_model(report, bff_context)

    if args.model_out:
        Path(args.model_out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.model_out).write_text(json.dumps(model, indent=2))
        print(f"Model: {args.model_out}")

    # Icons from the pair block (best-effort).
    pair = report.get("pair", {})
    icon_x = fetch_icon(pair.get("x", {}).get("image", ""), pair.get("x", {}).get("symbol", "tokenX"))
    icon_y = fetch_icon(pair.get("y", {}).get("image", ""), pair.get("y", {}).get("symbol", "tokenY"))

    if args.output:
        out_path = Path(args.output)
    else:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        cid = report.get("campaign_id", "card")
        out_path = OUTPUT_DIR / f"bitflow-pnl-card-{cid}.png"

    result = render_card(model, out_path, icon_x_path=icon_x, icon_y_path=icon_y)
    print(f"Card: {result}")

    # Text summary — hero first, attribution clearly subordinate.
    print(f"\n  NET PnL (after gas): {model['hero']['text']}   {model['pct_line']}")
    for label, value in model["rows"]:
        print(f"  {label}: {value}")
    chips = "   ".join(c["label"] for c in model["chips"])
    print(f"  context (not additive): {chips}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
