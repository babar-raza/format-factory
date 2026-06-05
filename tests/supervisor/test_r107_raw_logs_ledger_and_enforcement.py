"""R107 tests: raw log capture, lane execution ledger, sample outputs,
anti-skip gating, stream-state isolation, and deep grading enforcement.

Sprint: FORMAT-FACTORY-SUPERVISOR-R107-RAW-LOG-CAPTURE-STREAM-STATE-ISOLATION-CONTINUATION-GATING-CAMPAIGN-001
"""

import json
import sys
import textwrap
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
import yaml

TOOLS_DIR = Path(__file__).resolve().parent.parent.parent / "tools" / "supervisor"
sys.path.insert(0, str(TOOLS_DIR))

# ── Wave 1: Raw Log Capture ─────────────────────────────────────────

class TestRawLogCapture:
    """Verify capture_raw_logs.py produces expected output structure."""

    def test_capture_creates_output_files(self, tmp_path):
        from capture_raw_logs import capture_test_logs

        evidence_root = tmp_path / "evidence"
        evidence_root.mkdir()

        # Capture a trivial command
        result = capture_test_logs(
            evidence_root=evidence_root,
            command=[sys.executable, "-c", "print('hello'); import sys; sys.stderr.write('warn\\n')"],
            timeout=30,
        )

        assert result["exit_code"] == 0
        assert (evidence_root / "raw-logs" / "raw-test-log.txt").exists()
        assert (evidence_root / "raw-logs" / "stdout.txt").exists()
        assert (evidence_root / "raw-logs" / "stderr.txt").exists()
        assert (evidence_root / "raw-logs" / "capture-meta.json").exists()

    def test_capture_meta_has_required_fields(self, tmp_path):
        from capture_raw_logs import capture_test_logs

        evidence_root = tmp_path / "evidence"
        evidence_root.mkdir()

        result = capture_test_logs(
            evidence_root=evidence_root,
            command=[sys.executable, "-c", "print('ok')"],
            timeout=10,
        )

        meta = json.loads((evidence_root / "raw-logs" / "capture-meta.json").read_text())
        assert "command" in meta
        assert "exit_code" in meta
        assert "duration_seconds" in meta
        assert "timestamp" in meta
        assert "stdout_path" in meta
        assert "stderr_path" in meta
        assert "combined_path" in meta

    def test_capture_records_nonzero_exit(self, tmp_path):
        from capture_raw_logs import capture_test_logs

        evidence_root = tmp_path / "evidence"
        evidence_root.mkdir()

        result = capture_test_logs(
            evidence_root=evidence_root,
            command=[sys.executable, "-c", "import sys; sys.exit(42)"],
            timeout=10,
        )

        assert result["exit_code"] == 42
        meta = json.loads((evidence_root / "raw-logs" / "capture-meta.json").read_text())
        assert meta["exit_code"] == 42

    def test_capture_combined_has_both_streams(self, tmp_path):
        from capture_raw_logs import capture_test_logs

        evidence_root = tmp_path / "evidence"
        evidence_root.mkdir()

        capture_test_logs(
            evidence_root=evidence_root,
            command=[sys.executable, "-c", "import sys; print('OUT'); sys.stderr.write('ERR\\n')"],
            timeout=10,
        )

        combined = (evidence_root / "raw-logs" / "raw-test-log.txt").read_text()
        assert "STDOUT" in combined
        assert "STDERR" in combined
        assert "OUT" in combined
        assert "ERR" in combined


# ── Wave 2: Lane Execution Ledger ───────────────────────────────────

class TestLaneExecutionLedger:
    """Verify lane_execution_ledger.py schema and operations."""

    def test_create_ledger(self):
        from lane_execution_ledger import create_ledger

        ledger = create_ledger("SPRINT-001", "run-001")
        assert ledger["sprint_id"] == "SPRINT-001"
        assert ledger["run_id"] == "run-001"
        assert ledger["lanes"] == []

    def test_add_lane(self):
        from lane_execution_ledger import create_ledger, add_lane

        ledger = create_ledger("SPRINT-001", "run-001")
        entry = add_lane(ledger, "LANE-A", "First lane", status="completed", exit_code=0)
        assert len(ledger["lanes"]) == 1
        assert entry["lane_id"] == "LANE-A"
        assert entry["status"] == "completed"

    def test_validate_valid_ledger(self):
        from lane_execution_ledger import create_ledger, add_lane, validate_ledger

        ledger = create_ledger("SPRINT-001", "run-001")
        add_lane(ledger, "LANE-A", "Test", status="completed")
        result = validate_ledger(ledger)
        assert result["valid"] is True
        assert result["lane_count"] == 1

    def test_validate_empty_ledger_fails(self):
        from lane_execution_ledger import create_ledger, validate_ledger

        ledger = create_ledger("SPRINT-001", "run-001")
        result = validate_ledger(ledger)
        assert result["valid"] is False
        assert "No lanes in ledger" in result["errors"]

    def test_validate_invalid_status_fails(self):
        from lane_execution_ledger import create_ledger, add_lane, validate_ledger

        ledger = create_ledger("SPRINT-001", "run-001")
        add_lane(ledger, "LANE-A", "Test", status="bogus")
        result = validate_ledger(ledger)
        assert result["valid"] is False
        assert any("invalid status" in e for e in result["errors"])

    def test_write_and_load_roundtrip(self, tmp_path):
        from lane_execution_ledger import create_ledger, add_lane, write_ledger, load_ledger

        ledger = create_ledger("SPRINT-001", "run-001")
        add_lane(ledger, "LANE-A", "Test lane", status="completed", exit_code=0)

        path = tmp_path / "ledger.yaml"
        write_ledger(ledger, path)
        loaded = load_ledger(path)

        assert loaded["sprint_id"] == "SPRINT-001"
        assert len(loaded["lanes"]) == 1
        assert loaded["lanes"][0]["lane_id"] == "LANE-A"

    def test_generate_from_declaration(self, tmp_path):
        from lane_execution_ledger import generate_from_declaration

        decl = {
            "sprint_id": "SPRINT-001",
            "run_id": "run-001",
            "test_results": {"passed": 50, "failed": 0, "skipped": 1},
            "planned_work_items": [
                {
                    "item_id": "ITEM-01",
                    "title": "First item",
                    "status": "completed",
                    "evidence_paths": ["tests/test_a.py"],
                    "test_references": ["tests/test_a.py::test_one"],
                },
            ],
        }

        ledger = generate_from_declaration(decl, tmp_path)
        assert ledger["sprint_id"] == "SPRINT-001"
        assert len(ledger["lanes"]) == 2  # 1 work item + 1 test execution
        assert ledger["lanes"][0]["lane_id"] == "ITEM-01"
        assert ledger["lanes"][1]["lane_id"] == "TEST-EXECUTION"


# ── Wave 3: Sample Output Packaging ─────────────────────────────────

class TestSampleOutputPackaging:
    """Verify generate_sample_outputs.py produces all 5 required samples."""

    def test_generate_all_samples_creates_5_files(self, tmp_path):
        from generate_sample_outputs import generate_all_samples

        output_dir = tmp_path / "sample-outputs"
        review = {
            "overall_verdict": "ACCEPTED",
            "item_grades": [{"item_id": "X-01", "supervisor_grade": "ACCEPTED_VERIFIED"}],
            "accepted_items": ["X-01"],
            "rework_items": [],
        }
        signal = {"autonomous_continue": True, "continuation_state": "YES", "iteration": 1}

        written = generate_all_samples(
            output_dir=output_dir,
            review=review,
            continuation_signal=signal,
            prompt_text="# Next Sprint\nSupervisor R108...",
            target_stream="supervisor",
        )

        assert len(written) == 5
        assert all(p.exists() for p in written)
        assert (output_dir / "sample-grades.json").exists()
        assert (output_dir / "sample-continuation.json").exists()
        assert (output_dir / "sample-prompt.json").exists()
        assert (output_dir / "sample-wrong-stream-warning.json").exists()
        assert (output_dir / "sample-replay.json").exists()

    def test_sample_grades_has_structure(self, tmp_path):
        from generate_sample_outputs import generate_sample_grades

        review = {
            "overall_verdict": "ACCEPTED",
            "item_grades": [
                {"item_id": "A-01", "supervisor_grade": "ACCEPTED_VERIFIED"},
                {"item_id": "A-02", "supervisor_grade": "ACCEPTED_WITH_LIMITATIONS", "required_rework": "fix X"},
            ],
            "accepted_items": ["A-01", "A-02"],
            "rework_items": [],
        }

        result = generate_sample_grades(review)
        assert result["sample_type"] == "grades"
        assert result["item_count"] == 2
        assert result["accepted_count"] == 2

    def test_sample_prompt_detects_stream_markers(self, tmp_path):
        from generate_sample_outputs import generate_sample_prompt

        result = generate_sample_prompt("# Supervisor R108\nContinue supervisor work...")
        assert result["sample_type"] == "prompt"
        assert result["contains_stream_markers"] is True

        result2 = generate_sample_prompt("Do some stuff")
        assert result2["contains_stream_markers"] is False


# ── Wave 4: Anti-Skip Gating Integration ────────────────────────────

class TestAntiSkipGatingIntegration:
    """Verify anti-skip violations affect continuation correctly."""

    def test_anti_skip_raw_logs_in_subdirectory_passes(self, tmp_path):
        from anti_skip_checker import detect_missing_raw_logs

        evidence_root = tmp_path / "evidence"
        raw_logs = evidence_root / "raw-logs"
        raw_logs.mkdir(parents=True)
        (raw_logs / "raw-test-log.txt").write_text("test output here")

        result = detect_missing_raw_logs(evidence_root)
        assert result["is_violation"] is False
        assert len(result["logs_found"]) >= 1

    def test_anti_skip_ledger_yaml_detected(self, tmp_path):
        from anti_skip_checker import detect_missing_lane_ledger

        evidence_root = tmp_path / "evidence"
        evidence_root.mkdir(parents=True)
        (evidence_root / "lane-execution-ledger.yaml").write_text("lanes: []")

        result = detect_missing_lane_ledger(evidence_root)
        assert result["is_violation"] is False

    def test_anti_skip_sample_outputs_detected(self, tmp_path):
        from anti_skip_checker import detect_missing_sample_outputs

        evidence_root = tmp_path / "evidence"
        samples = evidence_root / "sample-outputs"
        samples.mkdir(parents=True)
        (samples / "sample-grades.json").write_text("{}")
        (samples / "sample-continuation.json").write_text("{}")

        result = detect_missing_sample_outputs(evidence_root)
        assert result["is_violation"] is False
        assert result["outputs_found"] >= 2

    def test_classify_violation_impact_critical_blocks(self):
        from anti_skip_checker import classify_violation_impact

        checks = [
            {"check": "stale_gaps", "is_violation": True},
            {"check": "missing_raw_logs", "is_violation": True},
        ]
        impact = classify_violation_impact(checks)
        assert impact["block"] is True
        assert "stale_gaps" in impact["block_items"]

    def test_classify_violation_impact_high_downgrades(self):
        from anti_skip_checker import classify_violation_impact

        checks = [
            {"check": "generic_prompt", "is_violation": True},
            {"check": "missing_raw_logs", "is_violation": False},
        ]
        impact = classify_violation_impact(checks)
        assert impact["block"] is False
        assert impact["downgrade"] is True
        assert "generic_prompt" in impact["downgrade_items"]

    def test_classify_violation_impact_medium_caveats_only(self):
        from anti_skip_checker import classify_violation_impact

        checks = [
            {"check": "missing_raw_logs", "is_violation": True},
        ]
        impact = classify_violation_impact(checks)
        assert impact["block"] is False
        assert impact["downgrade"] is False
        assert "missing_raw_logs" in impact["caveats"]

    def test_r106_anti_skip_was_correctly_non_blocking(self):
        """Verify the R106 violations (medium+low) correctly did not block."""
        from anti_skip_checker import classify_violation_impact

        # Simulate R106's exact violations
        r106_checks = [
            {"check": "missing_raw_logs", "is_violation": True},
            {"check": "missing_lane_ledger", "is_violation": True},
            {"check": "missing_sample_outputs", "is_violation": True},
        ]
        impact = classify_violation_impact(r106_checks)
        assert impact["block"] is False
        assert impact["downgrade"] is False
        # missing_raw_logs=medium, missing_lane_ledger=medium → caveats
        assert "missing_raw_logs" in impact["caveats"]
        assert "missing_lane_ledger" in impact["caveats"]
        # missing_sample_outputs=low → notes
        assert "missing_sample_outputs" in impact["notes"]


# ── Wave 5: Stream-State Isolation ──────────────────────────────────

class TestStreamStateIsolation:
    """Verify stream identity detection and wrong-stream warnings."""

    def test_extract_stream_from_supervisor_sprint(self):
        from validate_package_identity import _extract_stream_from_sprint

        stream = _extract_stream_from_sprint(
            "FORMAT-FACTORY-SUPERVISOR-R107-RAW-LOG-CAPTURE-001"
        )
        assert stream == "supervisor"

    def test_extract_stream_from_mainstream_sprint(self):
        from validate_package_identity import _extract_stream_from_sprint

        stream = _extract_stream_from_sprint(
            "FORMAT-FACTORY-MAINSTREAM-R109-SOME-WORK-001"
        )
        assert stream == "mainstream"

    def test_wrong_stream_warning_sample_generated(self, tmp_path):
        from generate_sample_outputs import generate_sample_wrong_stream_warning

        result = generate_sample_wrong_stream_warning(
            target_stream="supervisor",
            state_files_checked=["session-resume.md", "next-sprint.md"],
            warnings_found=["session-resume.md references MAINSTREAM-R109"],
        )
        assert result["sample_type"] == "wrong_stream_warning"
        assert result["is_clean"] is False
        assert len(result["warnings_found"]) == 1


# ── Wave 6: Deep Grading v4 ─────────────────────────────────────────

class TestDeepGradingV4:
    """Verify grading engine handles raw logs, ledger, and sample output presence."""

    def test_grade_completed_with_content_gets_verified(self):
        from grade_declared_work import grade_item

        inspection = {
            "item_id": "X-01",
            "declared_status": "completed",
            "has_evidence": True,
            "has_tests": True,
            "evidence_paths_missing": [],
            "evidence_paths_found": ["tests/test_x.py"],
            "tests_declared": ["tests/test_x.py::test_one"],
            "tests_with_content": ["tests/test_x.py"],
            "tests_empty_or_stub": [],
            "acceptance_criteria_verified": False,
            "acceptance_criteria_pattern": "",
        }

        grade = grade_item(inspection, {"passed": 10, "failed": 0})
        assert grade["supervisor_grade"] == "ACCEPTED_VERIFIED"

    def test_grade_path_only_gets_limitations(self):
        from grade_declared_work import grade_item

        inspection = {
            "item_id": "X-02",
            "declared_status": "completed",
            "has_evidence": True,
            "has_tests": True,
            "evidence_paths_missing": [],
            "evidence_paths_found": ["tests/test_x.py"],
            "tests_declared": ["tests/test_x.py"],
            "tests_with_content": [],
            "tests_empty_or_stub": [],
            "acceptance_criteria_verified": False,
            "acceptance_criteria_pattern": "",
        }

        grade = grade_item(inspection, {"passed": 10, "failed": 0})
        assert grade["supervisor_grade"] == "ACCEPTED_WITH_LIMITATIONS"

    def test_grade_overclaimed_no_evidence(self):
        from grade_declared_work import grade_item

        inspection = {
            "item_id": "X-03",
            "declared_status": "completed",
            "has_evidence": False,
            "has_tests": False,
            "evidence_paths_missing": ["missing.py"],
            "evidence_paths_found": [],
            "tests_declared": [],
        }

        grade = grade_item(inspection, {"passed": 10, "failed": 0})
        assert grade["supervisor_grade"] == "OVERCLAIMED"


# ── Wave 7: Replay Validation ───────────────────────────────────────

class TestReplayValidation:
    """Verify replay sample output structure and content."""

    def test_replay_sample_not_attempted(self):
        from generate_sample_outputs import generate_sample_replay

        result = generate_sample_replay("path/to/package.zip")
        assert result["sample_type"] == "replay"
        assert result["replay_attempted"] is False
        assert result["replay_result"]["status"] == "not_attempted"

    def test_replay_sample_with_result(self):
        from generate_sample_outputs import generate_sample_replay

        result = generate_sample_replay(
            "path/to/package.zip",
            replay_result={"status": "pass", "items_checked": 5, "items_passed": 5},
        )
        assert result["replay_attempted"] is True
        assert result["replay_result"]["status"] == "pass"


# ── Wave 8: Stream-Specific Prompt Generation ───────────────────────

class TestStreamSpecificPromptGeneration:
    """Verify prompts contain stream-specific content."""

    def test_supervisor_prompt_has_stream_identity(self):
        """A supervisor prompt must reference the supervisor stream."""
        prompt = "# Supervisor R108\nContinue supervisor control-plane work.\n"
        lower = prompt.lower()
        assert "supervisor" in lower

    def test_generic_prompt_detection(self):
        from anti_skip_checker import detect_generic_prompt

        # Generic prompt (no stream markers)
        result = detect_generic_prompt("Continue with next sprint. Complete outstanding items.")
        assert result["is_violation"] is True

        # Stream-specific prompt
        result2 = detect_generic_prompt(
            "Continue supervisor R108 work. Advance mainstream POC targets."
        )
        assert result2["is_violation"] is False


# ── Cross-Wave Integration ──────────────────────────────────────────

class TestCrossWaveIntegration:
    """Verify that all waves work together correctly."""

    def test_full_evidence_with_all_artifacts_passes_anti_skip(self, tmp_path):
        """An evidence root with raw logs, ledger, and samples should pass all checks."""
        from anti_skip_checker import detect_missing_raw_logs, detect_missing_lane_ledger, detect_missing_sample_outputs

        evidence_root = tmp_path / "evidence"
        evidence_root.mkdir()

        # Raw logs
        raw_logs = evidence_root / "raw-logs"
        raw_logs.mkdir()
        (raw_logs / "raw-test-log.txt").write_text("test output")

        # Ledger
        (evidence_root / "lane-execution-ledger.yaml").write_text(
            "sprint_id: X\nlanes:\n  - lane_id: A\n"
        )

        # Samples
        samples = evidence_root / "sample-outputs"
        samples.mkdir()
        for i in range(5):
            (samples / f"sample-{i}.json").write_text("{}")

        r1 = detect_missing_raw_logs(evidence_root)
        r2 = detect_missing_lane_ledger(evidence_root)
        r3 = detect_missing_sample_outputs(evidence_root)

        assert r1["is_violation"] is False
        assert r2["is_violation"] is False
        assert r3["is_violation"] is False

    def test_severity_map_completeness(self):
        """All 18 detectors must have a severity mapping."""
        from anti_skip_checker import SEVERITY_MAP

        expected_checks = {
            "generic_prompt", "stale_gaps", "missing_raw_logs",
            "path_only_acceptance", "missing_evidence_manifest",
            "missing_report_files", "missing_lane_ledger",
            "cross_stream_prompt_contamination", "missing_sample_outputs",
            "dirty_git_state", "wrong_stream_gaps", "evidence_quality_score",
            "declaration_completeness", "test_count_regression",
            "stale_evidence_manifest", "missing_changed_files",
            "stream_local_authority", "wrong_stream_next_sprint",
        }
        assert set(SEVERITY_MAP.keys()) == expected_checks
