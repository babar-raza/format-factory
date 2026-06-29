"""Tests for AUTO mode end-to-end pilot — TC-DL2-010."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools" / "supervisor"))
from lane_selector import select_lane

REPO_ROOT = Path(__file__).resolve().parents[2]
LEDGER_PATH = REPO_ROOT / "registry" / "product-deepening-ledger.yaml"


@pytest.fixture
def all_formats():
    ledger = yaml.safe_load(LEDGER_PATH.read_text(encoding="utf-8"))
    return [e["format"] for e in ledger if e.get("runtime", "python") == "python"]


@pytest.fixture
def flat_metrics_formats():
    ledger = yaml.safe_load(LEDGER_PATH.read_text(encoding="utf-8"))
    return [e["format"] for e in ledger
            if e.get("dom_applicability") in ("FLAT", "METRICS_ONLY")
            and e.get("runtime", "python") == "python"]


class TestAutoModePilot:

    def test_flat_metrics_formats_select_feature(self, flat_metrics_formats):
        """All FLAT/METRICS_ONLY formats → 'feature'."""
        for fmt in flat_metrics_formats:
            result = select_lane(fmt, ledger_path=LEDGER_PATH)
            assert result["selected_lane"] == "feature", \
                f"{fmt} should select feature but got {result['selected_lane']}"

    def test_all_formats_produce_result(self, all_formats):
        """All formats produce a valid lane selection result."""
        for fmt in all_formats:
            result = select_lane(fmt, ledger_path=LEDGER_PATH)
            assert result["selected_lane"] is not None, f"{fmt} returned None"
            assert result.get("error") is None, f"{fmt} returned error: {result.get('error')}"

    def test_results_reproducible(self, all_formats):
        """Results are reproducible on rerun."""
        results1 = {fmt: select_lane(fmt, ledger_path=LEDGER_PATH) for fmt in all_formats}
        results2 = {fmt: select_lane(fmt, ledger_path=LEDGER_PATH) for fmt in all_formats}
        for fmt in all_formats:
            assert results1[fmt]["selected_lane"] == results2[fmt]["selected_lane"], \
                f"{fmt} not reproducible"
