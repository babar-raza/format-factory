"""Tests for lane_dependency_checker.py — TC-DL2-009."""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools" / "supervisor"))
from lane_dependency_checker import check_feature_prerequisites


def _make_ledger(fmt="fods", maturity="D2"):
    entries = [{
        "product_id": f"{fmt.upper()}-PYTHON", "format": fmt, "runtime": "python",
        "dom_applicability": "FULL", "lane_b_maturity": maturity, "lane_b_ceiling": "D5",
    }]
    tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False, encoding="utf-8")
    yaml.dump(entries, tmp, default_flow_style=False)
    tmp.close()
    return Path(tmp.name)


class TestLaneDependencyChecker:

    def test_feature_requiring_d4_at_d2_blocked(self):
        """Feature requiring D4 at D2 format → blocked."""
        lp = _make_ledger("fods", "D2")
        result = check_feature_prerequisites("sheet_mutation", "fods", lp)
        assert result["allowed"] is False
        assert "D4" in result["blocked_reason"]

    def test_feature_requiring_d2_at_d3_allowed(self):
        """Feature requiring D2 at D3 format → allowed."""
        lp = _make_ledger("fods", "D3")
        result = check_feature_prerequisites("typed_cell_access", "fods", lp)
        assert result["allowed"] is True

    def test_feature_with_no_dom_dependency_allowed(self):
        """Feature with no DOM dependency → allowed."""
        lp = _make_ledger("fods", "D1")
        result = check_feature_prerequisites("nonexistent_feature", "fods", lp)
        assert result["allowed"] is True

    def test_unknown_feature_allowed(self):
        """Unknown feature → allowed (no restriction)."""
        lp = _make_ledger("fods", "D0")
        result = check_feature_prerequisites("totally_unknown_xyz", "fods", lp)
        assert result["allowed"] is True
