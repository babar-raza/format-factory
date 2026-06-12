"""
tests/skills/test_planning_bundle_runtime.py

Tests for planning_bundle_runtime.py — Lane F CONWAY-R7R8.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "skills"))

from planning_bundle_runtime import build_planning_bundle


class TestPlanningBundleStructure:
    def test_bundle_type_is_planning_bundle(self):
        result = build_planning_bundle(sprint_id="TEST-BUNDLE-001")
        assert result["bundle_type"] == "planning_bundle"

    def test_dry_run_only_always_true(self):
        result = build_planning_bundle(sprint_id="TEST-BUNDLE-001")
        assert result["dry_run_only"] is True

    def test_governance_commercial_ready_false(self):
        result = build_planning_bundle(sprint_id="TEST-BUNDLE-001")
        assert result["governance"]["commercial_product_ready"] is False

    def test_governance_no_prior_zip(self):
        result = build_planning_bundle(sprint_id="TEST-BUNDLE-001")
        assert result["governance"]["no_prior_zip_inclusion"] is True

    def test_has_required_top_level_keys(self):
        result = build_planning_bundle(sprint_id="TEST-BUNDLE-001")
        required = {"bundle_type", "sprint_id", "timestamp", "formats",
                    "per_format_summary", "global_fingerprints", "stale_verdicts",
                    "selected_lanes", "evidence_contract_refs", "governance",
                    "dry_run_only", "estimated_json_bytes"}
        for key in required:
            assert key in result, f"Missing key: {key}"


class TestPlanningBundleLive:
    def test_default_formats_fods_fodt(self):
        result = build_planning_bundle(sprint_id="TEST-BUNDLE-001")
        assert "fods" in result["formats"]
        assert "fodt" in result["formats"]

    def test_both_formats_in_per_format_summary(self):
        result = build_planning_bundle(sprint_id="TEST-BUNDLE-001")
        assert "fods" in result["per_format_summary"]
        assert "fodt" in result["per_format_summary"]

    def test_fods_accepted_count_20(self):
        result = build_planning_bundle(sprint_id="TEST-BUNDLE-001")
        assert result["per_format_summary"]["fods"]["accepted_count"] == 20

    def test_fodt_accepted_count_20(self):
        result = build_planning_bundle(sprint_id="TEST-BUNDLE-001")
        assert result["per_format_summary"]["fodt"]["accepted_count"] == 20

    def test_stale_verdicts_not_blocked_live(self):
        result = build_planning_bundle(sprint_id="TEST-BUNDLE-001")
        for fmt, verdict in result["stale_verdicts"].items():
            assert verdict != "STALE_BLOCKED", f"{fmt} is unexpectedly STALE_BLOCKED"

    def test_global_fingerprints_present(self):
        result = build_planning_bundle(sprint_id="TEST-BUNDLE-001")
        for fmt in result["formats"]:
            fp = result["global_fingerprints"].get(fmt)
            assert fp is not None
            assert isinstance(fp, dict)

    def test_evidence_contract_refs_present(self):
        result = build_planning_bundle(sprint_id="TEST-BUNDLE-001")
        for fmt in result["formats"]:
            ref = result["evidence_contract_refs"].get(fmt)
            assert ref is not None
            assert "test-bundle-001" in ref.lower()

    def test_bundle_not_size_warning_live(self):
        result = build_planning_bundle(sprint_id="TEST-BUNDLE-001")
        assert result["bundle_size_warning"] is False, (
            f"Bundle exceeded 50 KB: {result['estimated_json_bytes']} bytes"
        )

    def test_sprint_id_preserved(self):
        result = build_planning_bundle(sprint_id="MY-CUSTOM-SPRINT-001")
        assert result["sprint_id"] == "MY-CUSTOM-SPRINT-001"

    def test_single_format_bundle(self):
        result = build_planning_bundle(formats=["fods"], sprint_id="TEST-BUNDLE-FODS-001")
        assert result["formats"] == ["fods"]
        assert "fods" in result["per_format_summary"]
        assert "fodt" not in result["per_format_summary"]

    def test_bundle_json_serializable(self):
        result = build_planning_bundle(sprint_id="TEST-BUNDLE-001")
        json.dumps(result)  # Should not raise

    def test_bundle_deterministic(self):
        """Two calls with same sprint_id should produce identical fingerprints."""
        r1 = build_planning_bundle(sprint_id="DETERMINISTIC-TEST-001")
        r2 = build_planning_bundle(sprint_id="DETERMINISTIC-TEST-001")
        # Fingerprints must be identical
        assert r1["global_fingerprints"] == r2["global_fingerprints"]
        # Stale verdicts must be identical
        assert r1["stale_verdicts"] == r2["stale_verdicts"]
        # Selected lanes must be identical
        assert r1["selected_lanes"] == r2["selected_lanes"]

    def test_selected_lanes_non_empty(self):
        result = build_planning_bundle(sprint_id="TEST-BUNDLE-001")
        for fmt in result["formats"]:
            lanes = result["selected_lanes"].get(fmt, [])
            assert len(lanes) > 0, f"No lanes selected for {fmt}"


class TestPlanningBundleGovernance:
    def test_implementation_requires_human_authorization(self):
        result = build_planning_bundle(sprint_id="TEST-BUNDLE-001")
        assert result["governance"]["implementation_requires_human_authorization"] is True

    def test_dec034_iv_required_before_promotion(self):
        result = build_planning_bundle(sprint_id="TEST-BUNDLE-001")
        assert result["governance"]["dec034_iv_required_before_promotion"] is True

    def test_autonomous_execution_not_allowed(self):
        result = build_planning_bundle(sprint_id="TEST-BUNDLE-001")
        assert result["governance"]["autonomous_execution_allowed"] is False
