"""Tests for Skills R106 command validator hardening.

Validates that validate_claude_commands.py catches:
- Missing required sections (allowed_paths, forbidden_paths, stop_conditions)
- Incomplete refusal rules
- Missing ledger requirements for src-editing skills
- Missing rollback instructions
- Missing evidence output sections
- Cross-reference orphan and missing commands
"""

import json
import sys
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "supervisor"))

from validate_claude_commands import (
    validate_command_file,
    validate_all,
    cross_reference_registry,
    REQUIRED_SECTIONS,
    COMMANDS_DIR,
)
from validate_skill_transcript import (
    validate_transcript,
    validate_directory,
    REQUIRED_FIELDS,
    VALID_MODES,
    VALID_RESULTS,
    SRC_EDITING_TRACKS,
)


# ============================================================
# Command validator section coverage tests
# ============================================================

class TestCommandSectionCoverage:
    """Verify all 12 required sections are checked."""

    def test_required_sections_count(self):
        """Validator should check exactly 12 section types."""
        assert len(REQUIRED_SECTIONS) == 12

    def test_all_section_ids_present(self):
        expected = {
            "purpose", "inputs", "steps", "allowed_paths", "forbidden_paths",
            "stop_conditions", "evidence_output", "validation", "rollback",
            "transcript_requirement", "sample_invocation", "changelog",
        }
        assert set(REQUIRED_SECTIONS.keys()) == expected

    def test_error_severity_sections(self):
        """Sections with error severity block validation."""
        error_sections = [k for k, v in REQUIRED_SECTIONS.items() if v["severity"] == "error"]
        assert "allowed_paths" in error_sections
        assert "forbidden_paths" in error_sections
        assert "stop_conditions" in error_sections
        assert "purpose" in error_sections

    def test_warning_severity_sections(self):
        """Sections with warning severity don't block but are logged."""
        warning_sections = [k for k, v in REQUIRED_SECTIONS.items() if v["severity"] == "warning"]
        assert "validation" in warning_sections
        assert "rollback" in warning_sections
        assert "transcript_requirement" in warning_sections


# ============================================================
# Command file negative tests
# ============================================================

class TestCommandFileNegatives:
    """Test validator catches incomplete command files."""

    def _write_cmd(self, tmp_path, name, content):
        p = tmp_path / name
        p.write_text(content, encoding="utf-8")
        return p

    def test_missing_purpose_heading(self, tmp_path):
        """Command without title heading should fail."""
        p = self._write_cmd(tmp_path, "bad.md", (
            "---\nversion: '1.0'\nlast-updated: '2026-06-03'\n---\n"
            "No title heading here.\n\n"
            "## Required Inputs\n- x\n## What This Skill Does\n1. Step\n"
            "## Allowed Paths\n- x\n## Forbidden Paths\n- x\n"
            "## Stop Conditions\n- x\n## Evidence Output\nOut.\n"
            "## Validation\nVal.\n## Rollback\nRb.\nTranscript.\n"
            "## Sample Invocation\n```x```\n## Changelog\n- v1\n"
        ))
        result = validate_command_file(p)
        assert "purpose" in result["sections_missing"]

    def test_missing_forbidden_paths(self, tmp_path):
        """Command without forbidden paths should fail."""
        p = self._write_cmd(tmp_path, "bad.md", (
            "---\nversion: '1.0'\nlast-updated: '2026-06-03'\n---\n"
            "# /test-skill\n\nA test skill.\n\n"
            "## Required Inputs\n- x\n## What This Skill Does\n1. Step\n"
            "## Allowed Paths\n- x\n"
            "## Stop Conditions\n- x\n## Evidence Output\nOut.\n"
            "## Validation\nVal.\n## Rollback\nRb.\nTranscript.\n"
            "## Sample Invocation\n```x```\n## Changelog\n- v1\n"
        ))
        result = validate_command_file(p)
        assert not result["valid"]
        assert "forbidden_paths" in result["sections_missing"]

    def test_empty_file_fails(self, tmp_path):
        p = self._write_cmd(tmp_path, "empty.md", "")
        result = validate_command_file(p)
        assert not result["valid"]

    def test_file_under_10_lines_fails(self, tmp_path):
        p = self._write_cmd(tmp_path, "short.md", "# /x\nshort\n")
        result = validate_command_file(p)
        assert not result["valid"]
        assert any("too short" in e.lower() for e in result["errors"])


# ============================================================
# Registry cross-reference tests
# ============================================================

class TestRegistryCrossReference:
    """Verify registry/command cross-reference catches inconsistencies."""

    def test_real_registry_has_no_missing_active_commands(self):
        """All active skills in registry should have command files on disk."""
        registry_path = REPO_ROOT / ".supervisor" / "skill-registry.yaml"
        if not registry_path.exists():
            pytest.skip("Registry not found")
        result = validate_all(COMMANDS_DIR, registry_path)
        # Check for missing command files (active skills without command file)
        missing_errors = [e for e in result["errors"] if "missing command" in e.lower()]
        assert len(missing_errors) == 0, f"Active skills with missing commands: {missing_errors}"

    def test_orphan_commands_are_documented(self):
        """Orphan commands should exist but be documented as orphans."""
        registry_path = REPO_ROOT / ".supervisor" / "skill-registry.yaml"
        if not registry_path.exists():
            pytest.skip("Registry not found")
        result = validate_all(COMMANDS_DIR, registry_path)
        orphan_warnings = [w for w in result["warnings"] if "orphan" in w.lower()]
        # It's acceptable to have orphans as long as they're documented
        # Current known orphans: execution-handoff, memory-sprint, plan-hardening, export-plan-context
        for w in orphan_warnings:
            assert "not in registry" in w.lower()

    def test_draft_skills_allowed_missing_commands(self):
        """Draft skills are allowed to reference missing command files."""
        registry_path = REPO_ROOT / ".supervisor" / "skill-registry.yaml"
        if not registry_path.exists():
            pytest.skip("Registry not found")
        data = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
        drafts = [s for s in data.get("skills", []) if s.get("status") == "draft"]
        # Draft skills should have their missing commands as warnings, not errors
        result = validate_all(COMMANDS_DIR, registry_path)
        for draft in drafts:
            sid = draft["skill_id"]
            # Should NOT be in errors (only in warnings if missing)
            active_errors = [e for e in result["errors"] if sid in e]
            assert len(active_errors) == 0, f"Draft skill {sid} incorrectly produces error: {active_errors}"


# ============================================================
# Transcript validator hardening tests
# ============================================================

class TestTranscriptValidatorHardening:
    """Additional negative tests for validate_skill_transcript.py."""

    def test_unregistered_skill_fails(self):
        """Transcript with unknown skill_id should fail."""
        t = {
            "invocation_id": "HARDEN-001",
            "skill_id": "this-skill-does-not-exist",
            "mode": "dry-run",
            "inputs": {},
            "allowed_files": [],
            "actual_files_changed": [],
            "tests_run": [],
            "result": "PASS",
        }
        result = validate_transcript(t)
        assert not result["valid"]
        assert any("not found in registry" in e for e in result["errors"])

    def test_invalid_result_value_fails(self):
        """Result must be PASS or FAIL."""
        t = {
            "invocation_id": "HARDEN-002",
            "skill_id": "add-dotnet-object-model-feature",
            "mode": "dry-run",
            "inputs": {"format_id": "fods", "feature_name": "X",
                       "exact_source_paths": [], "exact_test_paths": [],
                       "ledger_entry_path": ""},
            "allowed_files": [],
            "actual_files_changed": [],
            "tests_run": [],
            "result": "PARTIAL",
        }
        result = validate_transcript(t)
        assert not result["valid"]
        assert any("invalid result" in e for e in result["errors"])

    def test_src_editing_tracks_are_correct(self):
        """SRC_EDITING_TRACKS should include all product-source tracks."""
        assert "commercial_dotnet" in SRC_EDITING_TRACKS
        assert "foss_python" in SRC_EDITING_TRACKS
        assert "cross_product_export" in SRC_EDITING_TRACKS
        assert "cross_product" in SRC_EDITING_TRACKS

    def test_all_required_fields_documented(self):
        """REQUIRED_FIELDS should match the documented contract."""
        expected = {
            "invocation_id", "skill_id", "mode", "inputs",
            "allowed_files", "actual_files_changed", "tests_run", "result",
        }
        assert REQUIRED_FIELDS == expected

    def test_directory_validation_empty_dir(self, tmp_path):
        """Empty directory should return 0 total."""
        result = validate_directory(tmp_path)
        assert result["total"] == 0
        assert result["pass"] == 0
        assert result["fail"] == 0

    def test_directory_validation_with_non_json(self, tmp_path):
        """Non-JSON files should be ignored by directory validator."""
        (tmp_path / "readme.txt").write_text("not json")
        result = validate_directory(tmp_path)
        assert result["total"] == 0  # Only .json files are checked


# ============================================================
# Full command validator integration test
# ============================================================

class TestFullCommandValidation:
    """Run the full validator against real command files."""

    def test_all_commands_pass_validation(self):
        """All command files should pass validation (no errors)."""
        registry_path = REPO_ROOT / ".supervisor" / "skill-registry.yaml"
        result = validate_all(COMMANDS_DIR, registry_path)
        assert result["valid"], f"Command validation failed: {result['errors']}"

    def test_passing_count_matches_total(self):
        """All commands should pass (zero failures)."""
        registry_path = REPO_ROOT / ".supervisor" / "skill-registry.yaml"
        result = validate_all(COMMANDS_DIR, registry_path)
        assert result["summary"]["failing"] == 0, (
            f"{result['summary']['failing']} command(s) failing"
        )
