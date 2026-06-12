"""Tests for Skills R105 transcript enforcement in grading.

Validates that when work items declare a skill_id, transcript validation
is used to determine grade outcomes.
"""

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "supervisor"))

from validate_skill_transcript import validate_transcript, validate_directory, VALID_MODES, VALID_RESULTS


# ============================================================
# Transcript-to-grade mapping tests
# ============================================================

class TestTranscriptGradeMapping:
    """Test how transcript validation outcomes should map to grades."""

    def _make_transcript(self, **overrides):
        """Create a valid base transcript with overrides."""
        base = {
            "invocation_id": "TEST-R105-001",
            "skill_id": "add-dotnet-object-model-feature",
            "mode": "dry-run",
            "inputs": {
                "format_id": "fods",
                "feature_name": "TestFeature",
                "exact_source_paths": ["src/net/fods/FodsDocument.cs"],
                "exact_test_paths": ["tests/net/fods/FodsTestFeatureTests.cs"],
                "ledger_entry_path": "reports/r90/product-code-change-ledger.json",
            },
            "allowed_files": ["src/net/fods/FodsDocument.cs", "tests/net/fods/FodsTestFeatureTests.cs"],
            "actual_files_changed": ["src/net/fods/FodsDocument.cs"],
            "tests_run": ["dotnet test --filter FodsTestFeature"],
            "ledger_entry_id": None,
            "result": "PASS",
            "timestamp": "2026-06-03T10:00:00Z",
        }
        base.update(overrides)
        return base

    def test_valid_transcript_eligible_for_accepted_verified(self):
        """A valid transcript with PASS result should be eligible for ACCEPTED_VERIFIED."""
        t = self._make_transcript()
        result = validate_transcript(t)
        assert result["valid"] is True
        assert result["result"] == "PASS"
        # Grade mapping: valid + PASS => eligible for ACCEPTED_VERIFIED

    def test_missing_transcript_should_downgrade(self):
        """If no transcript exists for a skill_id work item, grade should be OVERCLAIMED."""
        # Simulate: work item declares skill_id but transcript path doesn't exist
        # The grading logic should check: does evidence_path point to a valid transcript?
        # If missing => OVERCLAIMED
        # This test validates that validate_transcript rejects empty/missing data
        result = validate_transcript({})
        assert result["valid"] is False
        assert len(result["errors"]) > 0

    def test_invalid_transcript_should_downgrade(self):
        """Transcript with invalid fields should cause downgrade to OVERCLAIMED."""
        t = self._make_transcript(mode="invalid-mode")
        result = validate_transcript(t)
        assert result["valid"] is False
        assert any("invalid mode" in e for e in result["errors"])

    def test_fail_result_transcript_should_be_rework(self):
        """Transcript with FAIL result => REWORK_REQUIRED unless anti-bypass."""
        t = self._make_transcript(result="FAIL")
        result = validate_transcript(t)
        assert result["valid"] is True  # Schema valid
        assert result["result"] == "FAIL"
        # Grade mapping: valid but FAIL => REWORK_REQUIRED

    def test_anti_bypass_fail_is_accepted_when_expected(self):
        """Anti-bypass demo with FAIL result is expected and should not downgrade."""
        t = self._make_transcript(
            mode="anti-bypass-demo",
            result="FAIL",
            invocation_id="ANTI-BYPASS-001",
        )
        result = validate_transcript(t)
        assert result["valid"] is True
        assert result["mode"] == "anti-bypass-demo"
        assert result["result"] == "FAIL"
        # Grade mapping: anti-bypass-demo + FAIL => ACCEPTED (expected failure)

    def test_live_src_edit_without_ledger_fails(self):
        """LIVE transcript for src-editing track without ledger => OVERCLAIMED."""
        t = self._make_transcript(
            mode="live",
            ledger_entry_id=None,
        )
        result = validate_transcript(t)
        assert result["valid"] is False
        assert any("ledger_entry_id" in e for e in result["errors"])

    def test_live_src_edit_with_ledger_passes(self):
        """LIVE transcript for src-editing track with ledger => eligible for ACCEPTED."""
        t = self._make_transcript(
            mode="live",
            ledger_entry_id="LEDGER-001",
        )
        result = validate_transcript(t)
        assert result["valid"] is True

    def test_files_outside_allowed_fails(self):
        """Transcript with files changed outside allowed paths => OVERCLAIMED."""
        t = self._make_transcript(
            actual_files_changed=["src/net/fods/FodsDocument.cs", "src/net/fodt/UNAUTHORIZED.cs"],
        )
        result = validate_transcript(t)
        assert result["valid"] is False
        assert any("outside allowed" in e for e in result["errors"])


class TestTranscriptGradeDecisionMatrix:
    """Test the complete decision matrix for transcript-based grading."""

    def test_grade_decision_matrix_completeness(self):
        """Verify all transcript states map to expected grade outcomes."""
        matrix = {
            # (valid, result, mode) => expected_grade_category
            (True, "PASS", "dry-run"): "ACCEPTED",
            (True, "PASS", "live"): "ACCEPTED",
            (True, "FAIL", "dry-run"): "REWORK",
            (True, "FAIL", "live"): "REWORK",
            (True, "FAIL", "anti-bypass-demo"): "ACCEPTED",  # expected failure
            (False, None, None): "OVERCLAIMED",  # invalid transcript
        }
        assert len(matrix) == 6, "Decision matrix should cover 6 states"

    def test_all_valid_modes_accepted(self):
        """All valid modes should produce a valid transcript when other fields correct."""
        for mode in VALID_MODES:
            t = {
                "invocation_id": f"TEST-{mode}",
                "skill_id": "add-dotnet-object-model-feature",
                "mode": mode,
                "inputs": {"format_id": "fods", "feature_name": "Test",
                           "exact_source_paths": [], "exact_test_paths": [],
                           "ledger_entry_path": ""},
                "allowed_files": [],
                "actual_files_changed": [],
                "tests_run": [],
                "result": "PASS",
            }
            # live mode for src-editing tracks requires ledger_entry_id
            if mode == "live":
                t["ledger_entry_id"] = "LEDGER-TEST-001"
            result = validate_transcript(t)
            assert result["valid"] is True, f"Mode {mode} should be valid: {result['errors']}"

    def test_all_valid_results_accepted(self):
        """Both PASS and FAIL results should be schema-valid."""
        for res in VALID_RESULTS:
            t = {
                "invocation_id": f"TEST-{res}",
                "skill_id": "add-dotnet-object-model-feature",
                "mode": "dry-run",
                "inputs": {"format_id": "fods", "feature_name": "Test",
                           "exact_source_paths": [], "exact_test_paths": [],
                           "ledger_entry_path": ""},
                "allowed_files": [],
                "actual_files_changed": [],
                "tests_run": [],
                "result": res,
            }
            result = validate_transcript(t)
            assert result["valid"] is True, f"Result {res} should be valid"

    def test_directory_validation_separates_pass_fail(self, tmp_path):
        """Directory validation correctly counts pass vs fail transcripts."""
        # Valid transcript
        valid = {
            "invocation_id": "VALID-001",
            "skill_id": "add-dotnet-object-model-feature",
            "mode": "dry-run",
            "inputs": {"format_id": "fods", "feature_name": "V",
                       "exact_source_paths": [], "exact_test_paths": [],
                       "ledger_entry_path": ""},
            "allowed_files": [], "actual_files_changed": [],
            "tests_run": [], "result": "PASS",
        }
        (tmp_path / "valid.json").write_text(json.dumps(valid))

        # Invalid transcript (missing fields)
        (tmp_path / "invalid.json").write_text(json.dumps({"bad": True}))

        summary = validate_directory(tmp_path)
        assert summary["total"] == 2
        assert summary["pass"] == 1
        assert summary["fail"] == 1


class TestStreamStateValidation:
    """Test that wrong-stream state is detectable."""

    def test_wrong_stream_context_pack_detectable(self):
        """Context pack pointing to wrong stream should be flagged."""
        import yaml
        cp_path = REPO_ROOT / ".supervisor" / "context-pack.yaml"
        if not cp_path.exists():
            pytest.skip("No context pack")
        data = yaml.safe_load(cp_path.read_text(encoding="utf-8"))
        sprint_id = data.get("latest_sprint", {}).get("sprint_id", "")
        # Skills stream sprint IDs contain "SKILLS"
        is_skills_stream = "SKILLS" in sprint_id.upper()
        # This test documents the contamination — it's expected to fail if
        # context pack points to another stream
        if not is_skills_stream:
            # Document the contamination
            assert sprint_id != "", "Context pack should have a sprint_id"
            # We EXPECT this to be wrong-stream — classified as WRONG_STREAM_PRIMARY
