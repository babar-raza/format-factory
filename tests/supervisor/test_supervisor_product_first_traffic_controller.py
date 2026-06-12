"""
test_supervisor_product_first_traffic_controller.py

20 tests for the Supervisor Product-First Traffic Controller sprint.
Tests cover:
- 12 original tests: velocity scoring, Mainstream classification, continuation states, AI advisory
- 8 new tests: external runtime governance (Ruflo, Superpowers, GhidraMCP, task-master-ai)

Sprint: FORMAT-FACTORY-SUPERVISOR-PRODUCT-FIRST-TRAFFIC-CONTROLLER-REPLAN-AND-STREAM-LOCAL-CLOSURE-001
"""

from __future__ import annotations

import sys
from pathlib import Path


# Ensure tools/supervisor is importable
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "tools" / "supervisor"))


# ---------------------------------------------------------------------------
# Original 12 tests
# ---------------------------------------------------------------------------

class TestScoreStreamVelocity:
    """Tests for product_velocity_scorer.score_stream_velocity()"""

    def test_score_supervisor_removes_blocker(self):
        """poc_help_score=1, mainstream_blocker_removed=True for blocker-removed evidence."""
        from product_velocity_scorer import score_stream_velocity
        evidence = {"mainstream_blocker_removed": True}
        result = score_stream_velocity("supervisor", evidence, {}, {})
        assert result["mainstream_blocker_removed"] is True
        assert result["poc_help_score"] >= 1, f"poc_help_score={result['poc_help_score']}"

    def test_score_mainstream_direct_product(self):
        """product_breadth_score >= 2 for sprint with 2+ format families."""
        from product_velocity_scorer import score_stream_velocity
        evidence = {"families_touched": 3, "source_diffs": 3}
        result = score_stream_velocity("mainstream", evidence, {}, {})
        assert result["poc_help_score"] >= 2 or result["product_breadth_score"] >= 2, \
            f"poc={result['poc_help_score']}, breadth={result['product_breadth_score']}"


class TestClassifyMainstreamPackage:
    """Tests for product_velocity_scorer.classify_mainstream_package()"""

    def test_classify_mainstream_clean_pass(self):
        """3+ families/diffs/transcripts/logs/matrix-deltas → CLEAN_PASS."""
        from product_velocity_scorer import classify_mainstream_package
        evidence = {
            "families_touched": 3,
            "source_diffs": 3,
            "governed_transcripts": 3,
            "raw_logs": 3,
            "capability_matrix_deltas": 3,
            "repair_items": 0,
            "product_items": 5,
        }
        result = classify_mainstream_package(evidence)
        assert result == "CLEAN_PASS", f"Got: {result}"

    def test_classify_mainstream_partial_evidence_repair(self):
        """Repair items dominate → PARTIAL_EVIDENCE_REPAIR."""
        from product_velocity_scorer import classify_mainstream_package
        evidence = {
            "families_touched": 3,
            "source_diffs": 3,
            "governed_transcripts": 3,
            "raw_logs": 3,
            "capability_matrix_deltas": 3,
            "repair_items": 6,
            "product_items": 4,
        }
        result = classify_mainstream_package(evidence)
        assert result == "PARTIAL_EVIDENCE_REPAIR", f"Got: {result}"

    def test_classify_mainstream_partial_one_source(self):
        """Only 1 source diff → PARTIAL_ONE_SOURCE."""
        from product_velocity_scorer import classify_mainstream_package
        evidence = {
            "families_touched": 3,
            "source_diffs": 1,
            "governed_transcripts": 3,
            "raw_logs": 3,
            "capability_matrix_deltas": 3,
            "repair_items": 0,
            "product_items": 5,
        }
        result = classify_mainstream_package(evidence)
        assert result == "PARTIAL_ONE_SOURCE", f"Got: {result}"

    def test_classify_mainstream_partial_few_families(self):
        """Only 1 family → PARTIAL_FEW_FAMILIES."""
        from product_velocity_scorer import classify_mainstream_package
        evidence = {"families_touched": 1}
        result = classify_mainstream_package(evidence)
        assert result == "PARTIAL_FEW_FAMILIES", f"Got: {result}"


class TestContinuationStates:
    """Tests for autonomous_cycle.classify_continuation_state() new states."""

    def _classify(self, **kwargs) -> str:
        from autonomous_cycle import classify_continuation_state
        defaults = {
            "auto_continue_value": True,
            "at_max_iterations": False,
            "hard_stops": [],
            "overclaimed": [],
            "rework_items": [],
            "review": {},
            "policies_path": Path("/dev/null"),
        }
        defaults.update(kwargs)
        return classify_continuation_state(**defaults)

    def test_continuation_no_product_output_floor(self):
        """product_output_floor_met=False → NO_PRODUCT_OUTPUT_FLOOR."""
        result = self._classify(product_output_floor_met=False)
        assert result == "NO_PRODUCT_OUTPUT_FLOOR", f"Got: {result}"

    def test_continuation_no_missing_required_artifacts(self):
        """required_artifacts_present=False → NO_MISSING_REQUIRED_ARTIFACTS."""
        result = self._classify(required_artifacts_present=False)
        assert result == "NO_MISSING_REQUIRED_ARTIFACTS", f"Got: {result}"

    def test_continuation_no_unclassified_dirty_state(self):
        """dirty_state_classified=False → NO_UNCLASSIFIED_DIRTY_STATE."""
        result = self._classify(dirty_state_classified=False)
        assert result == "NO_UNCLASSIFIED_DIRTY_STATE", f"Got: {result}"

    def test_continuation_yes_with_defaults(self):
        """All defaults True → YES (backward compatibility preserved)."""
        result = self._classify()
        assert result == "YES", f"Got: {result}"

    def test_continuation_overclaim_still_priority(self):
        """overclaimed list present → NO_UNSAFE_SOURCE_STATE (higher priority than new states)."""
        result = self._classify(
            overclaimed=["item-001"],
            product_output_floor_met=False,
            required_artifacts_present=False,
            dirty_state_classified=False,
        )
        assert result == "NO_UNSAFE_SOURCE_STATE", f"Got: {result}"


class TestAIAdvisory:
    """Tests for ai_supervisor_advisor."""

    def test_ai_advisory_is_non_authoritative(self):
        """create_advisory_output returns non_authoritative=True."""
        from ai_supervisor_advisor import create_advisory_output
        out = create_advisory_output("supervisor", "sprint-001", [], "drift", {"q1": "yes"})
        assert out["non_authoritative"] is True
        assert out["authority_state"] == "ai_draft"
        assert out["advisory_mode"] == "deterministic_advisory"

    def test_deterministic_failure_overrides_ai_pass(self):
        """Deterministic failure → NO_* even if AI says PASS."""
        from ai_supervisor_advisor import handle_ai_deterministic_disagreement
        result = handle_ai_deterministic_disagreement(
            ai_result={"verdict": "PASS"},
            deterministic_result={"valid": False, "reason": "missing_logs"},
        )
        assert result.startswith("NO_"), f"Expected NO_*, got: {result}"

    def test_deterministic_pass_plus_ai_drift_yields_limitations(self):
        """Deterministic PASS + AI drift_flag=True → YES_WITH_LIMITATIONS."""
        from ai_supervisor_advisor import handle_ai_deterministic_disagreement
        result = handle_ai_deterministic_disagreement(
            ai_result={"drift_flag": True},
            deterministic_result={"valid": True},
        )
        assert result == "YES_WITH_LIMITATIONS", f"Got: {result}"

    def test_review_semantic_drift_is_non_authoritative(self):
        """review_semantic_drift() returns non_authoritative=True (exercises import fix)."""
        from ai_supervisor_advisor import review_semantic_drift
        result = review_semantic_drift("mainstream", {"families_touched": 2})
        assert result["non_authoritative"] is True
        assert result["authority_state"] == "ai_draft"
        assert result["advisory_mode"] == "deterministic_advisory"
        assert "drift_risk" in result["content"]


class TestProductOutputFloor:
    """Tests for product_velocity_scorer.compute_product_output_floor()."""

    def test_floor_met_with_families(self):
        """families_touched > 0 and low overhead → floor met."""
        from product_velocity_scorer import compute_product_output_floor
        assert compute_product_output_floor({"families_touched": 1}) is True

    def test_floor_not_met_pure_overhead(self):
        """Pure supervisor machinery (no families, no blocker) → floor not met."""
        from product_velocity_scorer import compute_product_output_floor
        # overhead score 3 (all declared items are supervisor) AND no product output
        declared = [{"type": "supervisor_tooling", "item_id": f"TC-{i}"} for i in range(5)]
        result = compute_product_output_floor({"declared_items": declared, "families_touched": 0})
        assert result is False


class TestClassifyMainstreamPackageExtended:
    """Extended classify_mainstream_package() tests for previously untested verdicts."""

    def test_classify_partial_helper_only(self):
        """High machinery overhead + no product actions → PARTIAL_HELPER_ONLY."""
        from product_velocity_scorer import classify_mainstream_package
        # 5 supervisor items → overhead=3 (ratio=1.0); none of fp/fs/blocker/acc set
        declared = [{"type": "supervisor_tooling", "item_id": f"TC-SUP-{i}"} for i in range(5)]
        evidence = {
            "families_touched": 3,
            "source_diffs": 3,
            "governed_transcripts": 3,
            "raw_logs": 3,
            "capability_matrix_deltas": 3,
            "repair_items": 0,
            "product_items": 5,
            "declared_items": declared,
            "false_pass_prevented": False,
            "false_stop_prevented": False,
            "mainstream_blocker_removed": False,
            "reusable_accelerator_consumed": False,
        }
        result = classify_mainstream_package(evidence)
        assert result == "PARTIAL_HELPER_ONLY", f"Got: {result}"

    def test_classify_partial_no_governed_transcripts(self):
        """families≥3, diffs≥3, 0 governed transcripts → PARTIAL_NO_GOVERNED_TRANSCRIPTS."""
        from product_velocity_scorer import classify_mainstream_package
        evidence = {
            "families_touched": 3,
            "source_diffs": 3,
            "governed_transcripts": 0,
            "raw_logs": 3,
            "capability_matrix_deltas": 3,
            "repair_items": 0,
            "product_items": 5,
        }
        result = classify_mainstream_package(evidence)
        assert result == "PARTIAL_NO_GOVERNED_TRANSCRIPTS", f"Got: {result}"

    def test_classify_partial_no_dogfood(self):
        """families≥3, diffs≥3, transcripts≥1, 0 matrix deltas → PARTIAL_NO_DOGFOOD."""
        from product_velocity_scorer import classify_mainstream_package
        evidence = {
            "families_touched": 3,
            "source_diffs": 3,
            "governed_transcripts": 1,
            "raw_logs": 3,
            "capability_matrix_deltas": 0,
            "repair_items": 0,
            "product_items": 5,
        }
        result = classify_mainstream_package(evidence)
        assert result == "PARTIAL_NO_DOGFOOD", f"Got: {result}"


# ---------------------------------------------------------------------------
# 8 External Governance tests
# ---------------------------------------------------------------------------

class TestRufloGovernance:
    """Tests for external_tool_governance Ruflo/claude-flow functions."""

    def test_ruflo_absent_allows_local_coordinator(self):
        """ABSENT mode → RUFLO_ABSENT_CONTINUE_WITH_LOCAL_COORDINATOR."""
        from external_tool_governance import classify_ruflo_mode, get_ruflo_verdict
        mode = classify_ruflo_mode({
            "claude_flow_ruflo": {"mcp_registered": False, "detected": False, "state_directory_present": False}
        })
        assert mode == "ABSENT", f"Got mode: {mode}"
        verdict = get_ruflo_verdict(mode)
        assert verdict == "RUFLO_ABSENT_CONTINUE_WITH_LOCAL_COORDINATOR", f"Got: {verdict}"

    def test_ruflo_full_loop_requires_approval(self):
        """FULL_LOOP_PRESENT_NOT_APPROVED → RUFLO_FULL_LOOP_BLOCKED_PENDING_APPROVAL."""
        from external_tool_governance import classify_ruflo_mode, get_ruflo_verdict
        mode = classify_ruflo_mode({
            "claude_flow_ruflo": {
                "mcp_registered": True,
                "detected": True,
                "state_directory_present": True,
            }
        })
        assert mode == "FULL_LOOP_PRESENT_NOT_APPROVED", f"Got mode: {mode}"
        verdict = get_ruflo_verdict(mode)
        assert verdict == "RUFLO_FULL_LOOP_BLOCKED_PENDING_APPROVAL", f"Got: {verdict}"

    def test_ruflo_output_cannot_close_taskcard(self):
        """External tool output with closes_taskcard=True → invalid (returns False)."""
        from external_tool_governance import validate_external_tool_output_authority
        result = validate_external_tool_output_authority({"closes_taskcard": True})
        assert result is False, "Expected False for closes_taskcard=True"

    def test_ruflo_detected_not_configured(self):
        """mcp_registered=True, state_dir=False → DETECTED_NOT_CONFIGURED."""
        from external_tool_governance import classify_ruflo_mode
        mode = classify_ruflo_mode({
            "claude_flow_ruflo": {
                "mcp_registered": True,
                "detected": True,
                "state_directory_present": False,
            }
        })
        assert mode == "DETECTED_NOT_CONFIGURED", f"Got: {mode}"


class TestSuperpowersGovernance:
    """Tests for external_tool_governance Superpowers functions."""

    def test_superpowers_install_requires_governance(self):
        """Superpowers detected but not governed → INSTALLED_NOT_GOVERNED."""
        from external_tool_governance import classify_superpowers_mode
        mode = classify_superpowers_mode({
            "superpowers": {
                "detected": True,
                "sessionstart_injection_detected": True,
            }
        })
        assert mode == "INSTALLED_NOT_GOVERNED", f"Got: {mode}"

    def test_superpowers_sessionstart_injection_detected(self):
        """SessionStart injection present → not governed."""
        from external_tool_governance import classify_superpowers_mode
        mode = classify_superpowers_mode({
            "superpowers": {
                "detected": True,
                "sessionstart_injection_detected": True,
            }
        })
        # Must not be INSTALLED_GOVERNED when injection detected
        assert mode != "INSTALLED_GOVERNED", "Got unexpected INSTALLED_GOVERNED"


class TestGhidraMCPGovernance:
    """Tests for external_tool_governance GhidraMCP functions."""

    def test_ghidra_mcp_disabled_by_default(self):
        """Not detected → ABSENT or DISABLED_DEFAULT."""
        from external_tool_governance import classify_ghidramcp_mode
        mode = classify_ghidramcp_mode({
            "ghidra_mcp": {"detected": False, "mcp_registered": False}
        })
        assert mode in ("ABSENT", "DISABLED_DEFAULT"), f"Got: {mode}"

    def test_ghidra_mcp_requires_authorized_input(self):
        """Registered but no authorized binary → BLOCKED_NEEDS_AUTHORIZATION."""
        from external_tool_governance import classify_ghidramcp_mode
        mode = classify_ghidramcp_mode({
            "ghidra_mcp": {
                "detected": True,
                "mcp_registered": True,
                "authorized_binary_present": False,
            }
        })
        assert mode == "BLOCKED_NEEDS_AUTHORIZATION", f"Got: {mode}"


class TestExternalToolDetectionSchema:
    """Tests for external_tool_governance detect + verdict functions."""

    def test_external_tool_mode_detection_json_schema(self):
        """build_external_tool_governance_verdict has all 4 required keys."""
        from external_tool_governance import build_external_tool_governance_verdict
        detections = {
            "claude_flow_ruflo": {
                "detected": True,
                "mcp_registered": True,
                "state_directory_present": False,
            },
            "task_master_ai": {
                "detected": True,
                "mcp_registered": True,
            },
            "superpowers": {
                "detected": False,
            },
            "ghidra_mcp": {
                "detected": False,
                "mcp_registered": False,
            },
        }
        verdict = build_external_tool_governance_verdict(detections)
        assert "claude_flow_ruflo" in verdict
        assert "task_master_ai" in verdict
        assert "superpowers" in verdict
        assert "ghidra_mcp" in verdict
        assert verdict["deterministic_supervisor_retains_authority"] is True
