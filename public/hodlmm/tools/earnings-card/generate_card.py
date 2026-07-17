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

See ../../runbooks/hodlmm-pnl-runbook.md ("Data provenance") and README.md.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from urllib.parse import quote

sys.path.insert(0, str(Path(__file__).parent))
from card_model import adapt_step6_report, build_card_model, safe_name
from render_card import render_card

TOOL_DIR = Path(__file__).parent
ICON_DIR = TOOL_DIR / "icons"
OUTPUT_DIR = TOOL_DIR / "output"

BFF_BASE = "https://bff.bitflowapis.finance/api/app/v1"
PERIOD_MAP = {"1d": "1d", "7d": "7d", "30d": "30d",
              "1D": "1d", "7D": "7d", "30D": "30d"}


def fetch_bff_context(wallet: str, pool: str, period: str) -> dict | None:
    """Fetch ONLY the subordinate context chips from Bitflow. Never raises —
    returns None on any failure so the card degrades to ledger-only."""
    try:
        import requests  # lazy: only the optional enrichment needs it

        url = f"{BFF_BASE}/users/{quote(wallet, safe='')}/earnings/pnl/{quote(pool, safe='')}"
        resp = requests.get(url, params={"period_type": PERIOD_MAP.get(period, period)}, timeout=15)
        resp.raise_for_status()
        raw = resp.json()
    except Exception as e:  # noqa: BLE001 — enrichment is best-effort
        print(f"Warning: BFF enrichment unavailable ({e}); rendering ledger-only.", file=sys.stderr)
        return None

    def _f(*paths):
        """Extract a float via dotted paths — the BFF response nests values
        (earnings.earningsUsd, feeTvl.percentage, tvl.usd); flat keys kept as
        fallback for the old response shape."""
        for path in paths:
            node = raw
            for part in path.split("."):
                node = node.get(part) if isinstance(node, dict) else None
                if node is None:
                    break
            if node in (None, "") or isinstance(node, dict):
                continue
            try:
                return float(node)
            except (TypeError, ValueError):
                return None  # unparseable enrichment value — drop, never render raw
        return None

    return {
        "earnings_usd": _f("earnings.earningsUsd", "earningsUsd", "earnings_usd"),
        "fee_tvl_pct": _f("feeTvl.percentage", "feeTvl", "fee_tvl"),
        "tvl_usd": _f("tvl.usd", "tvlUsd", "tvl_usd"),
        # BFF only serves preset windows (1d/7d/30d) — record which one so the
        # chips can disclose it when it differs from the card's period.
        "bff_period": PERIOD_MAP.get(period, str(period)),
        # Bitflow's figure is app-level fee attribution: context-only, not realized.
        "realized": False,
    }


def fetch_icon(url: str, name: str) -> Path | None:
    ICON_DIR.mkdir(parents=True, exist_ok=True)
    fragment = safe_name(name, "token")
    if fragment != str(name):
        # Sanitization is lossy — suffix a short digest of the original so two
        # distinct symbols can never share a cached icon file.
        fragment += "-" + hashlib.sha256(str(name).encode()).hexdigest()[:8]
    icon_path = ICON_DIR / f"{fragment}.png"
    if icon_path.exists():
        return icon_path
    if not url:
        return None
    try:
        import requests  # lazy: only icon fetching needs it

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

    report = adapt_step6_report(load_report(args.report))

    # Optional BFF enrichment — only if the report doesn't already carry context.
    bff_context = None
    if not args.no_bff and not report.get("context"):
        wallet = args.wallet or report.get("wallet")
        pool = args.pool or report.get("pool")
        # Never fabricate a window: use an explicit --period or the report's own
        # preset. A campaign-basis report has no 1d/7d/30d window to request —
        # skip enrichment rather than pin chips to a period the card isn't about.
        period = args.period or (report.get("period") or {}).get("preset")
        if wallet and pool and period:
            bff_context = fetch_bff_context(wallet, pool, period)
        elif wallet and pool:
            print("Note: no report-basis period (--period / period.preset); "
                  "skipping BFF enrichment — chips render from the report or grey out.",
                  file=sys.stderr)

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
        cid = safe_name(report.get("campaign_id"), "card")
        out_path = OUTPUT_DIR / f"bitflow-pnl-card-{cid}.png"

    result = render_card(model, out_path, icon_x_path=icon_x, icon_y_path=icon_y)
    print(f"Card: {result}")

    # Text summary — hero first, attribution clearly subordinate.
    print(f"\n  NET PnL (after gas): {model['hero']['text']}   {model['pct_line']}")
    for label, value in model["rows"]:
        print(f"  {label}: {value}")
    chips = "   ".join(c["label"] for c in model["chips"])
    print(f"  context (not additive): {chips}")
    print(f"  {model['footer']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
