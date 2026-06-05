"""Tests for validate_skill_transcript.py — positive and negative cases."""
import json
import sys
import tempfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "supervisor"))
from validate_skill_transcript import validate_transcript, validate_directory

REGISTRY = REPO_ROOT / ".supervisor" / "skill-registry.yaml"


def _minimal_valid():
    return {
        "invocation_id": "TEST-INV-001",
        "skill_id": "add-dotnet-object-model-feature",
        "mode": "dry-run",
        "inputs": {"format_id": "fods", "feature_name": "Foo"},
        "allowed_files": ["src/net/fods/FodsDocument.cs"],
        "actual_files_changed": ["src/net/fods/FodsDocument.cs"],
        "tests_run": ["tests/net/fods/FodsTestFoo.cs"],
        "result": "PASS",
    }


# --- Positive tests ---

class TestPositive:
    def test_minimal_valid_transcript_passes(self):
        r = validate_transcript(_minimal_valid(), REGISTRY)
        assert r["valid"] is True
        assert r["errors"] == []

    def test_dry_run_mode_accepted(self):
        t = _minimal_valid()
        t["mode"] = "dry-run"
        assert validate_transcript(t, REGISTRY)["valid"]

    def test_live_mode_accepted(self):
        t = _minimal_valid()
        t["mode"] = "live"
        t["ledger_entry_id"] = "R99-FODS-001"
        assert validate_transcript(t, REGISTRY)["valid"]

    def test_anti_bypass_demo_mode_accepted(self):
        t = _minimal_valid()
        t["mode"] = "anti-bypass-demo"
        assert validate_transcript(t, REGISTRY)["valid"]

    def test_fail_result_accepted(self):
        t = _minimal_valid()
        t["result"] = "FAIL"
        assert validate_transcript(t, REGISTRY)["valid"]

    def test_no_files_changed_passes(self):
        t = _minimal_valid()
        t["actual_files_changed"] = []
        assert validate_transcript(t, REGISTRY)["valid"]

    def test_warnings_do_not_cause_failure(self):
        t = _minimal_valid()
        t["invocation_id"] = "X"  # short ID triggers warning
        r = validate_transcript(t, REGISTRY)
        assert r["valid"] is True
        assert len(r["warnings"]) > 0


# --- Negative tests ---

class TestNegative:
    def test_missing_invocation_id_fails(self):
        t = _minimal_valid()
        del t["invocation_id"]
        r = validate_transcript(t, REGISTRY)
        assert r["valid"] is False
        assert any("missing required fields" in e for e in r["errors"])

    def test_missing_skill_id_fails(self):
        t = _minimal_valid()
        del t["skill_id"]
        r = validate_transcript(t, REGISTRY)
        assert r["valid"] is False

    def test_unregistered_skill_fails(self):
        t = _minimal_valid()
        t["skill_id"] = "nonexistent-skill-xyz"
        r = validate_transcript(t, REGISTRY)
        assert r["valid"] is False
        assert any("not found in registry" in e for e in r["errors"])

    def test_invalid_mode_fails(self):
        t = _minimal_valid()
        t["mode"] = "yolo"
        r = validate_transcript(t, REGISTRY)
        assert r["valid"] is False
        assert any("invalid mode" in e for e in r["errors"])

    def test_invalid_result_fails(self):
        t = _minimal_valid()
        t["result"] = "MAYBE"
        r = validate_transcript(t, REGISTRY)
        assert r["valid"] is False
        assert any("invalid result" in e for e in r["errors"])

    def test_files_outside_allowed_fails(self):
        t = _minimal_valid()
        t["actual_files_changed"] = ["registry/format-registry.yaml"]
        r = validate_transcript(t, REGISTRY)
        assert r["valid"] is False
        assert any("outside allowed" in e for e in r["errors"])

    def test_live_src_track_without_ledger_fails(self):
        t = _minimal_valid()
        t["mode"] = "live"
        # skill add-dotnet-object-model-feature is commercial_dotnet track
        r = validate_transcript(t, REGISTRY)
        assert r["valid"] is False
        assert any("ledger_entry_id" in e for e in r["errors"])

    def test_empty_transcript_fails(self):
        r = validate_transcript({}, REGISTRY)
        assert r["valid"] is False
        assert len(r["errors"]) > 0


# --- Directory validation ---

class TestDirectoryValidation:
    def test_validate_directory_counts(self, tmp_path):
        good = _minimal_valid()
        bad = _minimal_valid()
        del bad["skill_id"]

        (tmp_path / "good.json").write_text(json.dumps(good))
        (tmp_path / "bad.json").write_text(json.dumps(bad))

        result = validate_directory(tmp_path, REGISTRY)
        assert result["total"] == 2
        assert result["pass"] == 1
        assert result["fail"] == 1

    def test_validate_empty_directory(self, tmp_path):
        result = validate_directory(tmp_path, REGISTRY)
        assert result["total"] == 0
        assert result["pass"] == 0
        assert result["fail"] == 0
