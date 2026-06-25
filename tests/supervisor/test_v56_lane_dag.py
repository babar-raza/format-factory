"""TC-FL-007: Tests for V71 validate_lane_dag_ordering.

The plan called this 'V56' but V56 was already used; the validator is V71.
This test file is named test_v56 per plan requirement for traceability.

Tests assert:
1. V71 PASSes when no open system-healing gaps exist for a format
2. V71 WARNs when P3-P4 open system-healing gaps exist
3. V71 FAILs (blocks_sprint=True) when P2+ open system-healing gaps exist
4. V71 PASSes for non-PRODUCT_SOURCE items regardless of gap state
5. Closed/DEFERRED gaps do NOT trigger V71
6. V71 is registered in run_all_governance_validators
"""

import sys
import json
from pathlib import Path

_REPO = Path(__file__).parent.parent.parent
sys.path.insert(0, str(_REPO / "tools" / "supervisor"))
sys.path.insert(0, str(_REPO))

import pytest


def _make_product_item(fmt: str, item_type: str = "PRODUCT_SOURCE") -> dict:
    return {
        "item_id": f"TEST-{fmt.upper()}",
        "item_type": item_type,
        "format_id": fmt,
        "title": f"Test {fmt} product source item",
    }


class TestLaneDagOrderingValidator:
    """V71 validator behavior tests."""

    def test_passes_when_no_system_healing_gaps(self, tmp_path):
        """No system-healing gaps → PASS."""
        from governance_validators_ext import validate_lane_dag_ordering
        # Create an empty gap-ledger in tmp_path
        gl = [{"gap_id": "GAP-CSV-FOSS-LOAD-001", "format": "csv", "status": "closed", "priority": "P0"}]
        (tmp_path / "reports" / "capability-layer").mkdir(parents=True)
        (tmp_path / "reports" / "capability-layer" / "gap-ledger.json").write_text(json.dumps(gl))
        decl = {"planned_work_items": [_make_product_item("csv")]}
        result = validate_lane_dag_ordering(decl, tmp_path)
        assert result["result"] == "PASS"
        assert result["blocks_sprint"] is False

    def test_warns_for_p4_system_healing_gap(self, tmp_path):
        """P4 open system-healing gap → WARN, not block."""
        from governance_validators_ext import validate_lane_dag_ordering
        gl = [{
            "gap_id": "GAP-CHAIN-CSV-SAL-MRH-001",
            "format": "csv",
            "status": "open",
            "priority": "P4",
        }]
        (tmp_path / "reports" / "capability-layer").mkdir(parents=True)
        (tmp_path / "reports" / "capability-layer" / "gap-ledger.json").write_text(json.dumps(gl))
        decl = {"planned_work_items": [_make_product_item("csv")]}
        result = validate_lane_dag_ordering(decl, tmp_path)
        assert result["result"] == "WARN"
        assert result["blocks_sprint"] is False

    def test_fails_for_p2_system_healing_gap(self, tmp_path):
        """P2 open system-healing gap → FAIL, blocks sprint."""
        from governance_validators_ext import validate_lane_dag_ordering
        gl = [{
            "gap_id": "GAP-FORENSICS-001",
            "format": "xcf",
            "status": "open",
            "priority": "P2",
        }]
        (tmp_path / "reports" / "capability-layer").mkdir(parents=True)
        (tmp_path / "reports" / "capability-layer" / "gap-ledger.json").write_text(json.dumps(gl))
        decl = {"planned_work_items": [_make_product_item("xcf")]}
        result = validate_lane_dag_ordering(decl, tmp_path)
        assert result["result"] == "FAIL"
        assert result["blocks_sprint"] is True

    def test_deferred_gap_does_not_trigger(self, tmp_path):
        """DEFERRED_BY_DESIGN gaps must NOT block product work."""
        from governance_validators_ext import validate_lane_dag_ordering
        gl = [{
            "gap_id": "GAP-CHAIN-CSV-SAL-MRH-001",
            "format": "csv",
            "status": "DEFERRED_BY_DESIGN",
            "priority": "P3",
        }]
        (tmp_path / "reports" / "capability-layer").mkdir(parents=True)
        (tmp_path / "reports" / "capability-layer" / "gap-ledger.json").write_text(json.dumps(gl))
        decl = {"planned_work_items": [_make_product_item("csv")]}
        result = validate_lane_dag_ordering(decl, tmp_path)
        assert result["result"] == "PASS"

    def test_non_product_items_not_checked(self, tmp_path):
        """Documentation/governance items are not subject to lane DAG."""
        from governance_validators_ext import validate_lane_dag_ordering
        gl = [{"gap_id": "GAP-FORENSICS-001", "format": "csv", "status": "open", "priority": "P2"}]
        (tmp_path / "reports" / "capability-layer").mkdir(parents=True)
        (tmp_path / "reports" / "capability-layer" / "gap-ledger.json").write_text(json.dumps(gl))
        decl = {"planned_work_items": [_make_product_item("csv", item_type="DOCUMENTATION")]}
        result = validate_lane_dag_ordering(decl, tmp_path)
        assert result["result"] == "PASS"

    def test_passes_when_ledger_unavailable(self, tmp_path):
        """No gap-ledger → graceful PASS (non-blocking)."""
        from governance_validators_ext import validate_lane_dag_ordering
        decl = {"planned_work_items": [_make_product_item("csv")]}
        result = validate_lane_dag_ordering(decl, tmp_path)
        assert result["result"] == "PASS"
        assert result["blocks_sprint"] is False

    def test_real_ledger_all_pass(self):
        """Real gap-ledger — all system-healing gaps are closed/deferred → PASS."""
        from governance_validators_ext import validate_lane_dag_ordering
        decl = {"planned_work_items": [
            _make_product_item("csv"),
            _make_product_item("xcf"),
            _make_product_item("ndjson"),
        ]}
        result = validate_lane_dag_ordering(decl, _REPO)
        # All GAP-CHAIN-* gaps are DEFERRED_BY_DESIGN so should PASS
        assert result["blocks_sprint"] is False

    def test_v71_registered_in_runner(self):
        """V71 must be wired into run_all_governance_validators."""
        from governance_validator_runner import run_all_governance_validators
        decl = {"planned_work_items": []}
        output = run_all_governance_validators(decl, _REPO)
        validator_names = [r["validator"] for r in output.get("validators", [])]
        assert "validate_lane_dag_ordering" in validator_names
