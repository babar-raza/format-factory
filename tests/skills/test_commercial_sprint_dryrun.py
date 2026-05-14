"""
test_commercial_sprint_dryrun.py

Tests for tools/skills/commercial_sprint_dryrun.py

Run:
  PYTHONPATH=... python -m pytest tests/skills/test_commercial_sprint_dryrun.py -v
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import patch

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "skills"))

from commercial_sprint_dryrun import run_dryrun


class TestDryRunLive:
    """Live tests against actual repo FODS/FODT data."""

    def test_fods_dryrun_passes(self):
        result = run_dryrun("fods", "TEST-001", "Test mission.")
        assert result["dryrun_status"] == "DRY_RUN_PASS"

    def test_fodt_dryrun_passes(self):
        result = run_dryrun("fodt", "TEST-001", "Test mission.")
        assert result["dryrun_status"] == "DRY_RUN_PASS"

    def test_fods_quality_gate_pass(self):
        result = run_dryrun("fods", "TEST-001", "m")
        assert result["prompt_quality_gate_status"] == "PASS"
        assert result["quality_score"] == 10

    def test_fodt_quality_gate_pass(self):
        result = run_dryrun("fodt", "TEST-001", "m")
        assert result["prompt_quality_gate_status"] == "PASS"
        assert result["quality_score"] == 10

    def test_fods_accepted_count_20(self):
        result = run_dryrun("fods", "TEST-001", "m")
        assert result["accepted_count"] == 20

    def test_fodt_accepted_count_20(self):
        result = run_dryrun("fodt", "TEST-001", "m")
        assert result["accepted_count"] == 20

    def test_commercial_product_ready_always_false(self):
        for fmt in ["fods", "fodt"]:
            result = run_dryrun(fmt, "TEST-001", "m")
            assert result["governance"]["commercial_product_ready"] is False

    def test_dry_run_only_flag_true(self):
        result = run_dryrun("fods", "TEST-001", "m")
        assert result["governance"]["dry_run_only"] is True

    def test_gate_self_approval_always_false(self):
        result = run_dryrun("fods", "TEST-001", "m")
        assert result["governance"]["gate_self_approval_allowed"] is False

    def test_autonomous_implementation_always_false(self):
        result = run_dryrun("fods", "TEST-001", "m")
        assert result["governance"]["autonomous_implementation_allowed"] is False

    def test_dec034_iv_required_before_promotion(self):
        result = run_dryrun("fods", "TEST-001", "m")
        assert result["governance"]["dec034_iv_required_before_promotion"] is True

    def test_implementation_requires_human_authorization(self):
        result = run_dryrun("fods", "TEST-001", "m")
        assert result["governance"]["implementation_requires_human_authorization"] is True

    def test_evidence_contract_metadata_planned_only(self):
        result = run_dryrun("fods", "TEST-001", "m")
        meta = result["evidence_contract_metadata"]
        assert "planned_contract_path" in meta
        assert "note" in meta
        assert "Dry-run only" in meta["note"] or "dry-run" in meta["note"].lower()

    def test_selected_lanes_contain_implementation_lanes(self):
        result = run_dryrun("fods", "TEST-001", "m")
        assert "LANE-I-LOAD" in result["selected_lanes"]
        assert "LANE-I-TESTS" in result["selected_lanes"]

    def test_result_has_required_keys(self):
        result = run_dryrun("fods", "TEST-001", "m")
        required = ["format_id", "sprint_id", "dryrun_status", "requirements_state",
                    "accepted_count", "selected_lanes", "blocked_lanes",
                    "prompt_quality_gate_status", "quality_score", "governance",
                    "evidence_contract_metadata", "timestamp"]
        for key in required:
            assert key in result, f"Missing key: {key}"

    def test_no_source_files_written(self):
        """Dry-run must not touch src/net/ or src/python/."""
        src_net = REPO_ROOT / "src" / "net"
        src_py = REPO_ROOT / "src" / "python"
        before_net = {f.stat().st_mtime for f in src_net.rglob("*") if f.is_file()}
        before_py = {f.stat().st_mtime for f in src_py.rglob("*") if f.is_file()}

        run_dryrun("fods", "TEST-001", "m")

        after_net = {f.stat().st_mtime for f in src_net.rglob("*") if f.is_file()}
        after_py = {f.stat().st_mtime for f in src_py.rglob("*") if f.is_file()}
        assert before_net == after_net, "Dry-run modified src/net/ files"
        assert before_py == after_py, "Dry-run modified src/python/ files"


class TestDryRunBlocked:
    """Tests for blocked states."""

    def _make_blocked_context(self, state: str):
        return {
            "format_id": "testfmt",
            "requirements_state": {
                "status": state,
                "iv_status": None,
                "verifier_result": None,
                "accepted_count": 0,
                "missing_files": [],
                "stale": None,
                "blocker_reason": f"Blocked: {state}",
            },
            "gate_state": {
                "gates_passed": 10,
                "commercial_product_ready": False,
                "gate_11_status": "commercial_readiness_in_progress",
            },
            "known_constraints": [],
            "governance": {
                "commercial_product_ready": False,
                "gate_self_approval_allowed": False,
                "autonomous_implementation_allowed": False,
                "authority_files": [],
            },
        }

    def test_requirements_missing_yields_blocked(self):
        import format_context_resolver as r
        import lane_selector as s
        ctx = self._make_blocked_context("REQUIREMENTS_MISSING")
        lane_res = {"selected_lanes": [], "blocked_lanes": [], "lane_details": {},
                    "requirements_state": "REQUIREMENTS_MISSING", "blocker": "b",
                    "governance": {"commercial_product_ready": False,
                                   "gate_self_approval_allowed": False,
                                   "autonomous_implementation_allowed": False},
                    "format_id": "testfmt", "selector_version": "1.0"}
        with patch.object(r, "resolve_format_context", return_value=ctx), \
             patch.object(s, "select_lanes", return_value=lane_res):
            result = run_dryrun("testfmt", "TEST-001", "m")
        assert result["dryrun_status"] == "DRY_RUN_BLOCKED"

    def test_verified_no_iv_yields_blocked(self):
        import format_context_resolver as r
        import lane_selector as s
        ctx = self._make_blocked_context("REQUIREMENTS_VERIFIED_NO_IV")
        lane_res = {"selected_lanes": [], "blocked_lanes": [], "lane_details": {},
                    "requirements_state": "REQUIREMENTS_VERIFIED_NO_IV", "blocker": "b",
                    "governance": {"commercial_product_ready": False,
                                   "gate_self_approval_allowed": False,
                                   "autonomous_implementation_allowed": False},
                    "format_id": "testfmt", "selector_version": "1.0"}
        with patch.object(r, "resolve_format_context", return_value=ctx), \
             patch.object(s, "select_lanes", return_value=lane_res):
            result = run_dryrun("testfmt", "TEST-001", "m")
        assert result["dryrun_status"] == "DRY_RUN_BLOCKED"
