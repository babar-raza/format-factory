"""Tests for dom_maturity_promoter.py — TC-DL2-008."""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools" / "supervisor"))
from dom_maturity_promoter import check_promotion, promote


def _make_ledger(fmt="fods", maturity="D2", ceiling="D5"):
    entries = [{
        "product_id": f"{fmt.upper()}-PYTHON", "format": fmt, "runtime": "python",
        "dom_applicability": "FULL", "lane_a_maturity": "A1",
        "lane_b_maturity": maturity, "lane_b_ceiling": ceiling,
        "execution_mode": "AUTO", "lane_a_consecutive": 0,
        "lane_b_consecutive": 0, "lane_starvation_threshold": 3,
    }]
    tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False, encoding="utf-8")
    yaml.dump(entries, tmp, default_flow_style=False)
    tmp.close()
    return Path(tmp.name)


class TestDomMaturityPromoter:

    def test_eligible_promotion_succeeds(self):
        """Eligible promotion succeeds and updates ledger."""
        lp = _make_ledger("fods", "D2", "D5")
        result = promote("fods", "D3", lp)
        assert result["promoted"] is True
        assert result["new_level"] == "D3"
        # Verify ledger updated
        updated = yaml.safe_load(lp.read_text(encoding="utf-8"))
        assert updated[0]["lane_b_maturity"] == "D3"

    def test_ineligible_promotion_rejected(self):
        """Ineligible promotion (failed criteria) rejected."""
        lp = _make_ledger("fods", "D3", "D5")
        # D4 requires mutation API which FODS doesn't have
        result = check_promotion("fods", "D4", lp)
        assert result["eligible"] is False

    def test_idempotent_re_promotion(self):
        """Re-promoting an already-at-level format is a no-op."""
        lp = _make_ledger("fods", "D3", "D5")
        result = promote("fods", "D3", lp)
        assert result["promoted"] is False
        assert result.get("reason") == "already_at_or_above_target"

    def test_cannot_promote_beyond_ceiling(self):
        """Cannot promote beyond ceiling."""
        lp = _make_ledger("fods", "D3", "D3")
        result = check_promotion("fods", "D4", lp)
        assert result["eligible"] is False
        assert result.get("reason") == "exceeds_ceiling"

    def test_dry_run_no_write(self):
        """Dry-run does not write ledger."""
        lp = _make_ledger("fods", "D2", "D5")
        result = promote("fods", "D3", lp, dry_run=True)
        assert result["promoted"] is False
        assert result["dry_run"] is True
        # Ledger unchanged
        data = yaml.safe_load(lp.read_text(encoding="utf-8"))
        assert data[0]["lane_b_maturity"] == "D2"

    def test_missing_format_error(self):
        """Missing format returns error."""
        lp = _make_ledger("fods", "D2", "D5")
        result = check_promotion("nonexistent", "D3", lp)
        assert result["eligible"] is False
        assert "error" in result
