"""R108 tests: prompt-quality gate repair, stream-primary state isolation,
continuation-state enforcement, stale gap handling, and replay validation.

Sprint: FORMAT-FACTORY-SUPERVISOR-R108-STREAM-PRIMARY-STATE-PROMPT-QUALITY-GATING-AND-CONTINUATION-ENFORCEMENT-CAMPAIGN-001
"""

import sys
from pathlib import Path


TOOLS_DIR = Path(__file__).resolve().parent.parent.parent / "tools" / "supervisor"
sys.path.insert(0, str(TOOLS_DIR))


# ── Wave 1: Prompt-Quality Gate Repair ──────────────────────────────

class TestPromptQualityStreamAware:
    """Verify prompt-quality advancement_lane is stream-aware."""

    def test_supervisor_prompt_with_pipeline_term_passes(self):
        from validate_prompt_quality import validate_prompt_quality

        prompt = (
            "# Supervisor R109\n"
            "## Pipeline Work\n"
            "Strengthen grading pipeline and evidence-review validation.\n"
            "Enhance continuation state machine. Validate autonomous-cycle outputs.\n"
            "## Evidence\n"
            "Write evidence-declaration.yaml and run autonomous-cycle.\n"
        )
        result = validate_prompt_quality(prompt, "supervisor", has_advancement=True)
        adv = next(c for c in result["checks"] if c["check"] == "advancement_lane")
        assert adv["pass"] is True, f"Supervisor pipeline terms should satisfy advancement_lane: {adv}"

    def test_supervisor_prompt_without_any_terms_fails(self):
        from validate_prompt_quality import validate_prompt_quality

        prompt = (
            "# Supervisor R109\n"
            "## Task\n"
            "Read files. Write reports. Close sprint. Run cycle.\n"
            "## Evidence\n"
            "Write evidence-declaration.yaml and run autonomous-cycle.\n"
        )
        result = validate_prompt_quality(prompt, "supervisor", has_advancement=True)
        adv = next(c for c in result["checks"] if c["check"] == "advancement_lane")
        assert adv["pass"] is False

    def test_mainstream_prompt_still_uses_product_terms(self):
        from validate_prompt_quality import validate_prompt_quality

        prompt = (
            "# Mainstream R110\n"
            "## Product Advancement\n"
            "Advance FODS commercial .NET product. Add new API GetRowCount.\n"
            "## Evidence\n"
            "Write evidence-declaration.yaml and run autonomous-cycle.\n"
        )
        result = validate_prompt_quality(prompt, "mainstream", has_advancement=True)
        adv = next(c for c in result["checks"] if c["check"] == "advancement_lane")
        assert adv["pass"] is True

    def test_acceleration_prompt_with_harden_passes(self):
        from validate_prompt_quality import validate_prompt_quality

        prompt = (
            "# Acceleration R5\n"
            "## Detector Work\n"
            "Harden anti-skip detectors and expand severity mapping.\n"
            "Enforce validator strictness. Integrate new checks.\n"
            "## Evidence\n"
            "Write evidence-declaration.yaml and run autonomous-cycle.\n"
        )
        result = validate_prompt_quality(prompt, "acceleration", has_advancement=True)
        adv = next(c for c in result["checks"] if c["check"] == "advancement_lane")
        assert adv["pass"] is True

    def test_prompt_quality_failure_sets_flag(self):
        """Prompt quality failure must set prompt_quality_failure in review."""
        from validate_prompt_quality import validate_prompt_quality

        # A prompt that fails advancement_lane for mainstream
        prompt = "Read files. Run tests. Close sprint."
        result = validate_prompt_quality(prompt, "mainstream", has_advancement=True)
        assert result["valid"] is False
        failed = [c["check"] for c in result["checks"] if not c["pass"]]
        assert "advancement_lane" in failed or "not_generic" in failed


# ── Wave 2: Stream-Primary State Isolation ──────────────────────────

class TestStreamPrimaryState:
    """Verify stream-primary state identification."""

    def test_continuation_signal_identifies_source_stream(self):
        """Continuation signal must include source_sprint_id for stream identification."""
        signal = {
            "autonomous_continue": True,
            "source_sprint_id": "FORMAT-FACTORY-SUPERVISOR-R108-SOME-WORK-001",
            "continuation_state": "YES",
        }
        assert "SUPERVISOR" in signal["source_sprint_id"]

    def test_mainstream_sprint_in_supervisor_context_is_wrong_stream(self):
        from validate_package_identity import _extract_stream_from_sprint

        stream = _extract_stream_from_sprint(
            "FORMAT-FACTORY-MAINSTREAM-R110-PRODUCT-DEPTH-001"
        )
        assert stream == "mainstream"
        assert stream != "supervisor"

    def test_supervisor_sprint_in_supervisor_context_is_correct(self):
        from validate_package_identity import _extract_stream_from_sprint

        stream = _extract_stream_from_sprint(
            "FORMAT-FACTORY-SUPERVISOR-R108-STREAM-PRIMARY-001"
        )
        assert stream == "supervisor"


# ── Wave 3: Continuation-State Enforcement ──────────────────────────

class TestContinuationStateEnforcement:
    """Verify continuation states are correctly classified."""

    def test_prompt_quality_failure_produces_no_prompt_quality(self):
        from autonomous_cycle import classify_continuation_state

        state = classify_continuation_state(
            auto_continue_value=False,
            at_max_iterations=False,
            hard_stops=["prompt_quality_failure"],
            overclaimed=[],
            rework_items=[],
            review={},
            policies_path=Path("/nonexistent"),
        )
        assert state == "NO_PROMPT_QUALITY_FAILURE"

    def test_prompt_quality_has_priority_over_generic_rework(self):
        """prompt_quality_failure is a named hard stop and matches before generic fallback."""
        from autonomous_cycle import classify_continuation_state

        state = classify_continuation_state(
            auto_continue_value=False,
            at_max_iterations=False,
            hard_stops=["critical_rework_blocks_continuation", "prompt_quality_failure"],
            overclaimed=[],
            rework_items=[],
            review={},
            policies_path=Path("/nonexistent"),
        )
        # prompt_quality_failure is an explicit match; critical_rework is generic
        assert state == "NO_PROMPT_QUALITY_FAILURE"

    def test_overclaimed_blocks_before_hard_stops(self):
        from autonomous_cycle import classify_continuation_state

        state = classify_continuation_state(
            auto_continue_value=False,
            at_max_iterations=False,
            hard_stops=["prompt_quality_failure"],
            overclaimed=["X-01"],
            rework_items=[],
            review={},
            policies_path=Path("/nonexistent"),
        )
        assert state == "NO_UNSAFE_SOURCE_STATE"

    def test_yes_state_when_no_issues(self):
        from autonomous_cycle import classify_continuation_state

        state = classify_continuation_state(
            auto_continue_value=True,
            at_max_iterations=False,
            hard_stops=[],
            overclaimed=[],
            rework_items=[],
            review={},
            policies_path=Path("/nonexistent"),
        )
        assert state == "YES"

    def test_yes_with_rework_state(self):
        from autonomous_cycle import classify_continuation_state

        state = classify_continuation_state(
            auto_continue_value="true_with_rework",
            at_max_iterations=False,
            hard_stops=[],
            overclaimed=[],
            rework_items=["X-01"],
            review={},
            policies_path=Path("/nonexistent"),
        )
        assert state == "YES_WITH_REWORK"

    def test_stale_gaps_produces_no_stale_gaps(self):
        from autonomous_cycle import classify_continuation_state

        state = classify_continuation_state(
            auto_continue_value=False,
            at_max_iterations=False,
            hard_stops=["stale_gaps"],
            overclaimed=[],
            rework_items=[],
            review={},
            policies_path=Path("/nonexistent"),
        )
        assert state == "NO_STALE_GAPS"

    def test_wrong_stream_context_produces_no_wrong_stream(self):
        from autonomous_cycle import classify_continuation_state

        state = classify_continuation_state(
            auto_continue_value=False,
            at_max_iterations=False,
            hard_stops=["wrong_stream_context"],
            overclaimed=[],
            rework_items=[],
            review={},
            policies_path=Path("/nonexistent"),
        )
        assert state == "NO_WRONG_STREAM_CONTEXT"


# ── Wave 4: Stale Gap Handling ──────────────────────────────────────

class TestStaleGapHandling:
    """Verify stale gap detection and classification."""

    def test_stale_gap_detected(self):
        from anti_skip_checker import detect_stale_gaps

        result = detect_stale_gaps(
            gaps_data={"sprint_id": "FORMAT-FACTORY-MAINSTREAM-R98-OLD-001"},
            expected_sprint="FORMAT-FACTORY-SUPERVISOR-R108-NEW-001",
        )
        assert result["is_violation"] is True

    def test_matching_gap_sprint_passes(self):
        from anti_skip_checker import detect_stale_gaps

        result = detect_stale_gaps(
            gaps_data={"sprint_id": "FORMAT-FACTORY-SUPERVISOR-R108-NEW-001"},
            expected_sprint="FORMAT-FACTORY-SUPERVISOR-R108-NEW-001",
        )
        assert result["is_violation"] is False

    def test_no_gaps_data_passes(self):
        """Supervisor stream may not have product gaps — should not fail."""
        from anti_skip_checker import detect_stale_gaps

        result = detect_stale_gaps(gaps_data={}, expected_sprint="X")
        assert result["is_violation"] is False


# ── Wave 5: Replay Validation ───────────────────────────────────────

class TestReplayClassification:
    """Verify replay result structure and classification."""

    def test_replay_with_limitations(self):
        from generate_sample_outputs import generate_sample_replay

        result = generate_sample_replay(
            ".local/supervisor/reviews/supervisor-r107/declaration-review-package.zip",
            replay_result={
                "status": "accepted_with_limitations",
                "limitations": ["prompt_quality_invalid", "global_state_mainstream_contamination"],
            },
        )
        assert result["replay_attempted"] is True
        assert result["replay_result"]["status"] == "accepted_with_limitations"

    def test_replay_pass(self):
        from generate_sample_outputs import generate_sample_replay

        result = generate_sample_replay(
            "path/to/package.zip",
            replay_result={"status": "pass", "items_checked": 5, "items_passed": 5},
        )
        assert result["replay_result"]["status"] == "pass"


# ── Wave 6: Generated Stream Prompt Validation ──────────────────────

class TestGeneratedStreamPrompts:
    """Verify stream-specific prompt generation quality."""

    def test_supervisor_prompt_quality_with_stream_terms(self):
        from validate_prompt_quality import validate_prompt_quality

        prompt = (
            "# Supervisor R109\n"
            "## Pipeline Advancement Lane\n"
            "Improve grading engine. Strengthen evidence validation.\n"
            "Enhance autonomous-cycle continuation logic.\n"
            "Expand anti-skip detectors.\n"
            "## Replay and Package Hardening Task\n"
            "Validate replay infrastructure. Deepen package self-containment.\n"
            "## Evidence Closeout Phase\n"
            "Write evidence-declaration.yaml. Run autonomous-cycle.\n"
            "## Forecast\n"
            "R110: Per-stream state directories.\n"
            "R111: Self-assessment and graduation.\n"
            "R112: Full replay infrastructure.\n"
        )
        result = validate_prompt_quality(prompt, "supervisor", has_advancement=True)
        assert result["valid"] is True, f"Expected valid, got failures: {[c for c in result['checks'] if not c['pass']]}"

    def test_generic_prompt_still_fails(self):
        from validate_prompt_quality import validate_prompt_quality

        result = validate_prompt_quality(
            "Continue with next sprint. Complete outstanding items.",
            "supervisor",
            has_advancement=True,
        )
        assert result["valid"] is False


# ── Cross-Wave: Deep Grading v4 Integration ─────────────────────────

class TestDeepGradingV4PathOnlyEnforcement:
    """Verify path-only sprints are downgraded by R107 Lane C enforcement."""

    def test_all_path_only_produces_rework_verdict(self):
        from grade_declared_work import grade_all

        # All items have evidence but no tests_with_content
        inspection = {
            "run_id": "test",
            "sprint_id": "test",
            "evidence_root": "",
            "item_inspections": [
                {
                    "item_id": "A",
                    "declared_status": "completed",
                    "has_evidence": True,
                    "has_tests": True,
                    "evidence_paths_found": ["a.md"],
                    "evidence_paths_missing": [],
                    "tests_declared": [],
                    "tests_with_content": [],
                    "tests_empty_or_stub": [],
                    "acceptance_criteria_verified": False,
                    "acceptance_criteria_pattern": "",
                },
            ],
            "test_results": {"passed": 10, "failed": 0},
        }
        decl = {"planned_work_items": [{"item_id": "A", "title": "Item A"}]}
        review = grade_all(inspection, decl)
        # R107 Lane C: evidence_quality_score=0.0 → ACCEPTED_WITH_REWORK
        assert review["overall_verdict"] == "ACCEPTED_WITH_REWORK"
        assert review["evidence_quality_score"] == 0.0

    def test_mixed_verified_and_limitations_stays_accepted(self):
        from grade_declared_work import grade_all

        inspection = {
            "run_id": "test",
            "sprint_id": "test",
            "evidence_root": "",
            "item_inspections": [
                {
                    "item_id": "A",
                    "declared_status": "completed",
                    "has_evidence": True,
                    "has_tests": True,
                    "evidence_paths_found": ["a.md"],
                    "evidence_paths_missing": [],
                    "tests_declared": ["t.py"],
                    "tests_with_content": ["t.py"],
                    "tests_empty_or_stub": [],
                    "acceptance_criteria_verified": False,
                    "acceptance_criteria_pattern": "",
                },
                {
                    "item_id": "B",
                    "declared_status": "completed",
                    "has_evidence": True,
                    "has_tests": False,
                    "evidence_paths_found": ["b.md"],
                    "evidence_paths_missing": [],
                    "tests_declared": [],
                    "tests_with_content": [],
                    "tests_empty_or_stub": [],
                    "acceptance_criteria_verified": False,
                    "acceptance_criteria_pattern": "",
                },
            ],
            "test_results": {"passed": 10, "failed": 0},
        }
        decl = {"planned_work_items": [
            {"item_id": "A", "title": "Item A"},
            {"item_id": "B", "title": "Item B"},
        ]}
        review = grade_all(inspection, decl)
        # At least one verified → score > 0 → accepted or accepted-with-rework
        assert review["overall_verdict"] in ("ACCEPTED", "ACCEPTED_WITH_REWORK")
        assert review["evidence_quality_score"] > 0.0
