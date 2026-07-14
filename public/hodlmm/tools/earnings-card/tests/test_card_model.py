"""Card-model tests. Stdlib unittest (no pytest needed):

    python3 -m unittest discover -s tests -v

Covers the report-contract acceptance criteria from guides issue #37:
campaign-duration / preset / custom-period labels, net-PnL hero, BFF-absent
greying, non-additivity, Fee/TVL spelling, and gas STX+USD.
"""
import json
import sys
import tempfile
import unittest
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL_DIR))

from card_model import (  # noqa: E402
    adapt_step6_report,
    build_card_model,
    derive_period,
    safe_name,
)


def base_report(**over):
    r = {
        "campaign_id": "HODLMM-DLMM1-20260702-003",
        "pair": {"x": {"symbol": "sBTC"}, "y": {"symbol": "USDCx"}},
        "net_pnl": {"usd": 9.05, "pct_vs_hold": 11.6},
        "deployed_hold_baseline": {"usd": 78.21, "native": "123,853 sats + 0.111788 USDCx"},
        "final_inventory": {"usd": 87.76},
        "gas": {"stx": 3.0, "usd": 0.49},
        "period": {"source": "campaign",
                   "entry_ts": "2026-07-03T04:03:00Z", "exit_ts": "2026-07-10T00:03:00Z"},
        "context": {"earnings_usd": 24.16, "fee_tvl_pct": 39.70, "realized": False},
    }
    r.update(over)
    return r


class TestHero(unittest.TestCase):
    def test_net_pnl_is_hero(self):
        m = build_card_model(base_report())
        self.assertEqual(m["hero"]["text"], "+$9.05")
        self.assertTrue(m["hero"]["positive"])
        self.assertEqual(m["pct_line"], "+11.6% vs hold, after gas")

    def test_negative_net(self):
        m = build_card_model(base_report(net_pnl={"usd": -1.25, "pct_vs_hold": -1.6}))
        self.assertEqual(m["hero"]["text"], "−$1.25")
        self.assertFalse(m["hero"]["positive"])
        self.assertEqual(m["pct_line"], "−1.6% vs hold, after gas")

    def test_report_missing_net_pnl_raises(self):
        bad = base_report()
        del bad["net_pnl"]
        with self.assertRaises(ValueError):
            build_card_model(bad)

    def test_net_pnl_without_usd_raises_value_error(self):
        with self.assertRaises(ValueError):
            build_card_model(base_report(net_pnl={}))


class TestStep6Adapter(unittest.TestCase):
    """The canonical hodlmm-pnl-runbook Step-6 object renders without transform."""

    def step6_report(self, **over):
        r = {
            "campaign_id": "HODLMM-DLMM1-20260702-003",
            "pair": {"x": {"symbol": "sBTC"}, "y": {"symbol": "USDCx"}},
            "cost_basis": "123,853 sats + 0.111788 USDCx",
            "v_hold": 78.21,
            "v_position_no_fees": 80.09,
            "il_only_pnl": 1.88,
            "fee_pnl": 7.66,
            "fee_confidence": "high",
            "gas": 0.49,
            "net_pnl": 9.05,
            "fee_to_il_ratio": 4.07,
            "time_in_range_pct": 92.0,
            "final_inventory_mark": 87.76,
            "report_period": "Jul 3–Jul 10 · 6d 20h",
            "period_source": "campaign",
        }
        r.update(over)
        return r

    def test_scalar_net_pnl_becomes_hero(self):
        m = build_card_model(self.step6_report())
        self.assertEqual(m["hero"]["text"], "+$9.05")
        # pct derived on the deployed basis (v_hold): 9.05 / 78.21 ≈ 11.6%
        self.assertEqual(m["pct_line"], "+11.6% vs hold, after gas")

    def test_core_rows_mapped(self):
        m = build_card_model(self.step6_report())
        rows = dict(m["rows"])
        self.assertIn("$78.21", rows["Deployed hold baseline"])
        self.assertEqual(rows["Final inventory"], "$87.76")
        self.assertIn("Campaign", rows["Period"])
        self.assertEqual(m["period_source"], "campaign")

    def test_scalar_gas_is_numeraire_mark(self):
        m = build_card_model(self.step6_report())
        gas = next(c for c in m["chips"] if c["label"].startswith("Gas"))
        self.assertEqual(gas["label"], "Gas $0.49")

    def test_card_shape_passthrough(self):
        r = base_report()
        self.assertIs(adapt_step6_report(r), r)

    def test_dict_gas_passes_through_untouched(self):
        m = build_card_model(self.step6_report(gas={"stx": 3.0, "usd": 0.49}))
        gas = next(c for c in m["chips"] if c["label"].startswith("Gas"))
        self.assertEqual(gas["label"], "Gas 3 STX (~$0.49)")

    def test_explicit_period_wins_over_report_period(self):
        m = build_card_model(self.step6_report(
            period={"source": "report", "preset": "7d"}))
        self.assertEqual(m["period_source"], "report")


class TestFeeConfidenceGuardrail(unittest.TestCase):
    """Low fee_confidence ⇒ Earnings is context-only even if 'realized' claims
    otherwise, and the caveat is surfaced in the footer (runbook display-only
    guardrail, INV-8)."""

    def test_low_confidence_forces_context_only(self):
        m = build_card_model(base_report(
            fee_confidence="low",
            context={"earnings_usd": 5.0, "realized": True},
        ))
        earn = next(c for c in m["chips"] if c["label"].startswith("Earnings"))
        self.assertTrue(earn["context_only"])
        self.assertTrue(m["earnings_context_only"])

    def test_confidence_rendered_in_footer(self):
        m = build_card_model(base_report(fee_confidence="low"))
        self.assertIn("fee_confidence: low", m["footer"])
        self.assertIn("period source: campaign", m["footer"])

    def test_high_confidence_realized_stays_green(self):
        m = build_card_model(base_report(
            fee_confidence="high",
            context={"earnings_usd": 5.0, "realized": True},
        ))
        earn = next(c for c in m["chips"] if c["label"].startswith("Earnings"))
        self.assertFalse(earn["context_only"])


class TestSafeName(unittest.TestCase):
    """Untrusted campaign ids / token symbols must not traverse output paths."""

    def test_traversal_neutralized(self):
        self.assertNotIn("/", safe_name("../../../../etc/passwd", "card"))
        self.assertNotIn("..", safe_name("../../x", "card"))

    def test_empty_falls_back(self):
        self.assertEqual(safe_name("", "card"), "card")
        self.assertEqual(safe_name(None, "card"), "card")

    def test_normal_id_preserved(self):
        self.assertEqual(safe_name("HODLMM-DLMM1-20260702-003", "card"),
                         "HODLMM-DLMM1-20260702-003")


class TestPeriodLabel(unittest.TestCase):
    def test_campaign_basis_duration(self):
        p = derive_period({"source": "campaign",
                           "entry_ts": "2026-07-03T04:03:00Z", "exit_ts": "2026-07-10T00:03:00Z"})
        self.assertEqual(p["source"], "campaign")
        self.assertIn("Campaign", p["label"])
        self.assertIn("6d 20h", p["label"])
        self.assertIn("Jul 3", p["label"])

    def test_report_preset_not_hardcoded(self):
        p = derive_period({"source": "report", "preset": "7d"})
        self.assertEqual(p["label"], "Report · 7D")

    def test_report_custom_range(self):
        p = derive_period({"source": "report",
                           "entry_ts": "2026-07-03T00:00:00Z", "exit_ts": "2026-07-05T12:00:00Z"})
        self.assertIn("Report", p["label"])
        self.assertIn("2d 12h", p["label"])

    def test_no_assumed_7d_when_unknown(self):
        p = derive_period({"source": "report"})
        self.assertEqual(p["label"], "Report")
        self.assertNotIn("7D", p["label"])

    def test_source_recorded_in_model(self):
        self.assertEqual(build_card_model(base_report())["period_source"], "campaign")


class TestChips(unittest.TestCase):
    def _chip(self, model, prefix):
        return next(c for c in model["chips"] if c["label"].startswith(prefix))

    def test_earnings_present_but_context_only(self):
        m = build_card_model(base_report())
        earn = self._chip(m, "Earnings")
        self.assertTrue(earn["available"])
        self.assertTrue(earn["context_only"])  # realized=False -> attribution
        self.assertTrue(m["earnings_context_only"])

    def test_bff_absent_greys_earnings(self):
        r = base_report()
        r.pop("context")
        m = build_card_model(r, bff_context=None)
        earn = self._chip(m, "Earnings")
        self.assertFalse(earn["available"])
        self.assertIn("n/a", earn["label"])

    def test_fee_tvl_spelling(self):
        m = build_card_model(base_report())
        fee = self._chip(m, "Fee/TVL")
        self.assertTrue(fee["label"].startswith("Fee/TVL "))
        # no misspelling anywhere in the model
        blob = json.dumps(m)
        self.assertNotIn("Feel/TVL", blob)

    def test_gas_shows_stx_and_usd(self):
        m = build_card_model(base_report())
        gas = self._chip(m, "Gas")
        self.assertEqual(gas["label"], "Gas 3 STX (~$0.49)")

    def test_gas_stx_only_when_no_usd(self):
        m = build_card_model(base_report(gas={"stx": 2.5}))
        self.assertEqual(self._chip(m, "Gas")["label"], "Gas 2.5 STX")

    def test_realized_earnings_not_flagged_context(self):
        m = build_card_model(base_report(context={"earnings_usd": 5.0, "realized": True}))
        self.assertFalse(self._chip(m, "Earnings")["context_only"])


class TestNonAdditive(unittest.TestCase):
    def test_divider_and_separation(self):
        m = build_card_model(base_report())
        self.assertIn("not additive", m["context_divider"])
        # hero equals net only; earnings ($24.16) is NOT folded into it
        self.assertEqual(m["hero"]["text"], "+$9.05")

    def test_core_rows_present(self):
        m = build_card_model(base_report())
        labels = [r[0] for r in m["rows"]]
        self.assertIn("Deployed hold baseline", labels)
        self.assertIn("Final inventory", labels)
        # baseline carries both USD and native inventory
        baseline = dict(m["rows"])["Deployed hold baseline"]
        self.assertIn("$78.21", baseline)
        self.assertIn("sats", baseline)


class TestBffEnrichmentMerge(unittest.TestCase):
    def test_bff_fills_only_when_missing(self):
        r = base_report()
        r.pop("context")
        m = build_card_model(r, bff_context={"earnings_usd": 24.16, "fee_tvl_pct": 39.7, "realized": False})
        self.assertTrue(next(c for c in m["chips"] if c["label"].startswith("Earnings"))["available"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
