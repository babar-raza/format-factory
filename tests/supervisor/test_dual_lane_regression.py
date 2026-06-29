"""Dual-lane regression test suite — TC-DL2-020.

Comprehensive regression tests covering the full dual-lane system.
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools" / "supervisor"))
from lane_selector import select_lane, check_starvation
from capability_feature_compiler import _classify_deepening_lane, _lane_balance_penalty, _score
from dom_contract_checker import check_contract
from lane_dependency_checker import check_feature_prerequisites

REPO_ROOT = Path(__file__).resolve().parents[2]


def _make_entry(fmt="fods", **overrides):
    base = {
        "product_id": f"{fmt.upper()}-PYTHON", "format": fmt, "runtime": "python",
        "dom_applicability": "FULL", "lane_a_maturity": "A1",
        "lane_b_maturity": "D3", "lane_b_ceiling": "D5",
        "execution_mode": "AUTO", "lane_a_consecutive": 0,
        "lane_b_consecutive": 0, "lane_starvation_threshold": 3,
    }
    base.update(overrides)
    return base


def _write_ledger(entries):
    tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False, encoding="utf-8")
    yaml.dump(entries, tmp, default_flow_style=False)
    tmp.close()
    return Path(tmp.name)


class TestDualLaneRegression:

    # 1. Lane classification
    def test_lane_classification_dom(self):
        """spec_parity_gap → DOM."""
        assert _classify_deepening_lane({"gap_type": "spec_parity_gap"}) == "dom"

    def test_lane_classification_feature(self):
        """missing_test_coverage → feature."""
        assert _classify_deepening_lane({"gap_type": "missing_test_coverage", "capability_name": "export"}) == "feature"

    # 2. Score direction
    def test_score_direction_lower_wins(self):
        """Lower score = higher priority. +15 HURTS."""
        gap_p1 = {"priority": "P1", "format": "X", "gap_type": "t", "capability_name": "c",
                  "commercial_impact": "NONE", "foss_impact": "NONE"}
        gap_p3 = {"priority": "P3", "format": "X", "gap_type": "t", "capability_name": "c",
                  "commercial_impact": "NONE", "foss_impact": "NONE"}
        assert _score(gap_p1) < _score(gap_p3)

    # 3. Starvation preference
    def test_starvation_at_threshold(self):
        """Threshold=3, consecutive=3 → must_switch=True."""
        lp = _write_ledger([_make_entry(lane_a_consecutive=3)])
        r = check_starvation("fods", lp)
        assert r["must_switch"] is True

    # 4. Ceiling filtering
    def test_at_ceiling_feature_only(self):
        """At-ceiling format → no DOM items eligible."""
        lp = _write_ledger([_make_entry(lane_b_maturity="D5", lane_b_ceiling="D5")])
        r = select_lane("fods", ledger_path=lp)
        assert r["selected_lane"] == "feature"

    # 5. FEATURE_ONLY exclusion
    def test_feature_only_excludes_dom(self):
        """FEATURE_ONLY: DOM work ineligible."""
        lp = _write_ledger([_make_entry(execution_mode="FEATURE_ONLY")])
        r = select_lane("fods", ledger_path=lp)
        assert r["selected_lane"] == "feature"

    # 6. DOM_ONLY exclusion
    def test_dom_only_excludes_feature(self):
        """DOM_ONLY: feature work ineligible."""
        lp = _write_ledger([_make_entry(execution_mode="DOM_ONLY")])
        r = select_lane("fods", ledger_path=lp)
        assert r["selected_lane"] == "dom"

    # 7. AUTO selects based on gap ratio
    def test_auto_dom_when_b_gap_larger(self):
        """AUTO: B gap larger → dom selected."""
        lp = _write_ledger([_make_entry(lane_b_maturity="D1", lane_b_ceiling="D5", lane_a_maturity="A4")])
        r = select_lane("fods", ledger_path=lp)
        assert r["selected_lane"] == "dom"

    # 8. Starvation override works
    def test_starvation_override_dom(self):
        """Starvation forces DOM selection."""
        lp = _write_ledger([_make_entry(lane_a_consecutive=3)])
        r = select_lane("fods", ledger_path=lp)
        assert r["selected_lane"] == "dom"

    # 9. Fair return to Lane A
    def test_fair_return_to_feature(self):
        """After DOM sprint, feature selectable again."""
        lp = _write_ledger([_make_entry(lane_a_consecutive=0, lane_b_consecutive=1)])
        r = select_lane("fods", ledger_path=lp)
        assert r["selected_lane"] == "feature"

    # 10. PARALLEL returns both
    def test_parallel_both_lanes(self):
        """PARALLEL mode returns list of both lanes."""
        lp = _write_ledger([_make_entry(execution_mode="PARALLEL")])
        r = select_lane("fods", ledger_path=lp)
        assert isinstance(r["selected_lane"], list)

    # 11. Contract checker works for FODS
    def test_fods_d2_contract_passes(self):
        """FODS passes D2 contract."""
        r = check_contract("fods", "D2")
        assert r["passed"] is True

    # 12. Dependency checker blocks correctly
    def test_dependency_blocks_mutation_at_d2(self):
        """Sheet mutation blocked when format at D2."""
        lp = _write_ledger([_make_entry(lane_b_maturity="D2")])
        r = check_feature_prerequisites("sheet_mutation", "fods", lp)
        assert r["allowed"] is False

    # 13. Replay safety — TC-DL2-021 fixed
    def test_replay_protection_prevents_double_increment(self):
        """TC-DL2-021: Replay protection prevents double-increment."""
        from autonomous_cycle_extensions import update_lane_counters
        lp = _write_ledger([_make_entry()])
        decl = {"sprint_id": "s1", "planned_work_items": [
            {"format": "fods", "status": "completed", "deepening_lane": "feature"}
        ]}
        update_lane_counters(decl, lp)
        update_lane_counters(decl, lp)
        data = yaml.safe_load(lp.read_text(encoding="utf-8"))
        assert data[0]["lane_a_consecutive"] == 1  # Fixed by TC-DL2-021 replay protection

    # 14. FLAT format handling
    def test_flat_format_always_feature(self):
        """FLAT format → always feature."""
        lp = _write_ledger([_make_entry("csv", dom_applicability="FLAT")])
        r = select_lane("csv", ledger_path=lp)
        assert r["selected_lane"] == "feature"

    # 15. METRICS_ONLY format handling
    def test_metrics_only_always_feature(self):
        """METRICS_ONLY → always feature."""
        lp = _write_ledger([_make_entry("zst", dom_applicability="METRICS_ONLY")])
        r = select_lane("zst", ledger_path=lp)
        assert r["selected_lane"] == "feature"

    # 16. Lane selector idempotent
    def test_lane_selector_idempotent(self):
        """Same input → same output (idempotent)."""
        lp = _write_ledger([_make_entry()])
        r1 = select_lane("fods", ledger_path=lp)
        r2 = select_lane("fods", ledger_path=lp)
        assert r1["selected_lane"] == r2["selected_lane"]
        assert r1["reason"] == r2["reason"]

    # 17. Contract checker idempotent
    def test_contract_checker_idempotent(self):
        """Contract check is idempotent."""
        r1 = check_contract("fods", "D3")
        r2 = check_contract("fods", "D3")
        assert r1["passed"] == r2["passed"]
        assert len(r1["criteria"]) == len(r2["criteria"])

    # 18. Missing format graceful
    def test_missing_format_graceful(self):
        """Missing format handled gracefully."""
        lp = _write_ledger([_make_entry()])
        r = select_lane("nonexistent_xyz", ledger_path=lp)
        assert r.get("error") is not None
