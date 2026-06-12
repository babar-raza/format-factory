"""Tests for the skill transcript validator."""

import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "supervisor"))

from validate_skill_transcript import validate_transcript

REGISTRY = REPO_ROOT / ".supervisor" / "skill-registry.yaml"


def _good_transcript(**overrides):
    base = {
        "invocation_id": "R100-DRYRUN-TEST-001",
        "skill_id": "add-dotnet-api",
        "mode": "dry-run",
        "inputs": {
            "format_id": "FODS",
            "api_name": "TestApi",
            "exact_source_paths": ["src/net/fods/FodsDocument.cs"],
            "exact_test_paths": ["tests/net/fods/TestFile.cs"],
            "ledger_entry_path": "reports/r90/product-code-change-ledger.json",
            "focused_test_command": "dotnet test tests/net/fods/",
        },
        "allowed_files": ["src/net/fods/FodsDocument.cs", "tests/net/fods/TestFile.cs"],
        "actual_files_changed": [],
        "tests_run": [],
        "result": "PASS",
        "timestamp": "2026-06-03T08:00:00Z",
    }
    base.update(overrides)
    return base


class TestTranscriptValidatorNegative:

    def test_missing_required_fields(self):
        result = validate_transcript({}, REGISTRY)
        assert not result["valid"]
        assert any("missing required fields" in e for e in result["errors"])

    def test_invalid_mode(self):
        t = _good_transcript(mode="invalid")
        result = validate_transcript(t, REGISTRY)
        assert not result["valid"]
        assert any("invalid mode" in e for e in result["errors"])

    def test_invalid_result(self):
        t = _good_transcript(result="MAYBE")
        result = validate_transcript(t, REGISTRY)
        assert not result["valid"]
        assert any("invalid result" in e for e in result["errors"])

    def test_unregistered_skill(self):
        t = _good_transcript(skill_id="nonexistent-skill")
        result = validate_transcript(t, REGISTRY)
        assert not result["valid"]
        assert any("not found in registry" in e for e in result["errors"])

    def test_files_outside_allowed(self):
        t = _good_transcript(
            actual_files_changed=["src/python/fods/parser.py"],
            allowed_files=["src/net/fods/FodsDocument.cs"],
        )
        result = validate_transcript(t, REGISTRY)
        assert not result["valid"]
        assert any("outside allowed paths" in e for e in result["errors"])

    def test_live_src_editing_without_ledger(self):
        t = _good_transcript(mode="live")
        # No ledger_entry_id for a commercial_dotnet skill
        result = validate_transcript(t, REGISTRY)
        assert not result["valid"]
        assert any("ledger_entry_id" in e for e in result["errors"])


class TestTranscriptValidatorPositive:

    def test_valid_dry_run(self):
        t = _good_transcript()
        result = validate_transcript(t, REGISTRY)
        assert result["valid"]

    def test_valid_live_with_ledger(self):
        t = _good_transcript(
            mode="live",
            ledger_entry_id="R100-TEST-001",
            actual_files_changed=["src/net/fods/FodsDocument.cs"],
        )
        result = validate_transcript(t, REGISTRY)
        assert result["valid"]

    def test_non_src_editing_skill_no_ledger_ok(self):
        t = _good_transcript(
            skill_id="add-roundtrip-test",
            mode="live",
            inputs={"format_id": "FODS", "roundtrip_scope": "test", "exact_test_paths": ["tests/"]},
        )
        result = validate_transcript(t, REGISTRY)
        assert result["valid"]

    def test_planning_skill_no_ledger_ok(self):
        t = _good_transcript(
            skill_id="generate-execution-handoff",
            mode="live",
            inputs={"skill_id": "add-dotnet-api", "target_format": "FODS", "scope": "test"},
        )
        result = validate_transcript(t, REGISTRY)
        assert result["valid"]
