"""
Regression tests for anti-skip sample output detection (Lane 1 of
FORMAT-FACTORY-SPEC-AUTHORITY-FULL-HARDENING-BACKFILL-AND-PILOT-MEGA-TRAIN-001).

Root cause addressed:
  Prior sprints stored sample outputs in reports/<run>/sample-outputs/ but
  anti_skip_checker.detect_missing_sample_outputs() looks in:
    1. evidence_root/sample-outputs/  (the .local/evidences/<run_id>/sample-outputs/ dir)
    2. evidence_artifacts with type: sample_output in the declaration
  NOT in reports/*/sample-outputs/.

These tests verify:
  - Outputs in evidence_root/sample-outputs/ are detected.
  - Artifacts with type: sample_output in declaration are detected.
  - Missing outputs trigger the violation.
  - Non-sample-output types do NOT satisfy the check.
  - The check is low-severity (informational only).
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools" / "supervisor"))
from anti_skip_checker import (
    detect_missing_sample_outputs,
    SEVERITY_MAP,
)

# GRE-TC-003: detect_missing_sample_outputs is only active when the declaration
# contains at least one PRODUCT_SOURCE item. Tests that exercise the real check
# must pass this declaration to prevent the governance-only exemption from firing.
_PRODUCT_SOURCE_DECL = {
    "planned_work_items": [
        {"item_id": "WI-TEST-1", "item_type": "PRODUCT_SOURCE"}
    ]
}


class TestSampleOutputDirectoryDetection:
    def test_files_in_evidence_root_sample_outputs_are_detected(self, tmp_path):
        evidence_root = tmp_path / "evidence"
        sample_dir = evidence_root / "sample-outputs"
        sample_dir.mkdir(parents=True)
        (sample_dir / "foo.json").write_text('{"x": 1}')
        result = detect_missing_sample_outputs(evidence_root, declaration=_PRODUCT_SOURCE_DECL)
        assert result["outputs_found"] == 1
        assert result["is_violation"] is False

    def test_missing_sample_outputs_triggers_violation(self, tmp_path):
        evidence_root = tmp_path / "evidence"
        evidence_root.mkdir()
        result = detect_missing_sample_outputs(evidence_root, declaration=_PRODUCT_SOURCE_DECL)
        assert result["is_violation"] is True
        assert result["outputs_found"] == 0

    def test_multiple_files_all_counted(self, tmp_path):
        evidence_root = tmp_path / "evidence"
        sample_dir = evidence_root / "sample-outputs"
        sample_dir.mkdir(parents=True)
        for i in range(5):
            (sample_dir / f"output-{i}.json").write_text("{}")
        result = detect_missing_sample_outputs(evidence_root, declaration=_PRODUCT_SOURCE_DECL)
        assert result["outputs_found"] == 5
        assert result["is_violation"] is False

    def test_empty_sample_outputs_dir_triggers_violation(self, tmp_path):
        evidence_root = tmp_path / "evidence"
        (evidence_root / "sample-outputs").mkdir(parents=True)
        result = detect_missing_sample_outputs(evidence_root, declaration=_PRODUCT_SOURCE_DECL)
        assert result["is_violation"] is True


class TestSampleOutputDeclarationDetection:
    def test_declaration_artifact_type_sample_output_detected(self, tmp_path):
        evidence_root = tmp_path / "evidence"
        evidence_root.mkdir()
        sample_file = tmp_path / "reports" / "run" / "sample.json"
        sample_file.parent.mkdir(parents=True)
        sample_file.write_text("{}")
        declaration = {
            "planned_work_items": [
                {"item_id": "WI-TEST-1", "item_type": "PRODUCT_SOURCE"}
            ],
            "evidence_artifacts": [
                {"path": str(sample_file), "type": "sample_output"}
            ]
        }
        result = detect_missing_sample_outputs(evidence_root, declaration=declaration)
        assert result["is_violation"] is False
        assert result["outputs_found"] >= 1

    def test_non_sample_output_type_does_not_satisfy_check(self, tmp_path):
        evidence_root = tmp_path / "evidence"
        evidence_root.mkdir()
        artifact_file = tmp_path / "foo.json"
        artifact_file.write_text("{}")
        declaration = {
            "planned_work_items": [
                {"item_id": "WI-TEST-1", "item_type": "PRODUCT_SOURCE"}
            ],
            "evidence_artifacts": [
                {"path": str(artifact_file), "type": "proof_graph"},
                {"path": str(artifact_file), "type": "authority_matrix"},
            ]
        }
        result = detect_missing_sample_outputs(evidence_root, declaration=declaration)
        assert result["is_violation"] is True

    def test_mixed_types_with_sample_output_passes(self, tmp_path):
        evidence_root = tmp_path / "evidence"
        evidence_root.mkdir()
        sample_file = tmp_path / "sample.json"
        sample_file.write_text("{}")
        declaration = {
            "evidence_artifacts": [
                {"path": str(sample_file), "type": "proof_graph"},
                {"path": str(sample_file), "type": "sample_output"},
            ]
        }
        result = detect_missing_sample_outputs(evidence_root, declaration=declaration)
        assert result["is_violation"] is False


class TestSampleOutputSeverity:
    def test_missing_sample_outputs_is_low_severity(self):
        assert SEVERITY_MAP.get("missing_sample_outputs") == "low"

    def test_check_key_correct(self, tmp_path):
        evidence_root = tmp_path / "evidence"
        evidence_root.mkdir()
        result = detect_missing_sample_outputs(evidence_root)
        assert result["check"] == "missing_sample_outputs"


class TestRealSprintSampleOutputs:
    """Regression: verify the current sprint has sample outputs in evidence root."""

    def test_current_sprint_evidence_root_has_sample_outputs(self):
        repo_root = Path(__file__).resolve().parents[2]
        run_id = "spec-authority-full-hardening-backfill-20260608-e382e5f"
        evidence_root = repo_root / ".local" / "evidences" / run_id
        if not evidence_root.exists():
            pytest.skip(f"Evidence root not found: {evidence_root}")
        result = detect_missing_sample_outputs(evidence_root)
        assert result["is_violation"] is False, (
            f"Current sprint still missing sample outputs. "
            f"Found: {result['outputs_found']}. "
            f"Fix: copy outputs to .local/evidences/{run_id}/sample-outputs/"
        )

    def test_prior_sprint_pattern_would_fail(self, tmp_path):
        """Confirm that putting outputs only in reports/ fails the check."""
        evidence_root = tmp_path / ".local" / "evidences" / "run-id"
        evidence_root.mkdir(parents=True)
        # simulate reports-only pattern (NOT in evidence_root)
        reports_dir = tmp_path / "reports" / "run-id" / "sample-outputs"
        reports_dir.mkdir(parents=True)
        (reports_dir / "foo.json").write_text("{}")
        result = detect_missing_sample_outputs(evidence_root, declaration=_PRODUCT_SOURCE_DECL)
        assert result["is_violation"] is True, "reports-only pattern should fail"
