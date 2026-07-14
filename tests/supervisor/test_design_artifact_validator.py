"""Tests for tools/supervisor/design_artifact_validator.py — V153.

TC-SPW-004-06: V153 tests (≥4 cases).
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools" / "supervisor"))

from design_artifact_validator import (
    validate_design_artifact_present,
    _validate_artifact_content,
    _cs_files_in_changed,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_decl(changed_files=None, taskcard_id="TC-TEST-001"):
    return {
        "planned_work_items": [],
        "changed_files": changed_files or [],
        "taskcard_id": taskcard_id,
    }


def _make_valid_artifact(is_partial_class=False, estimated_loc=150, no_dict=True, no_const=True, spec_fact="FACT-FODS-001"):
    return {
        "taskcard_id": "TC-TEST-001",
        "format_id": "fods",
        "language": "dotnet",
        "target_file": "src/net/fods/FodsCellFormula.cs",
        "primary_class": {
            "name": "FodsCellFormula",
            "is_partial_class": is_partial_class,
            "spec_qname": "table:table-cell",
            "estimated_loc": estimated_loc,
        },
        "public_api": [{
            "name": "GetCellFormula",
            "spec_fact": spec_fact,
            "parser_source": "XElement.Attribute('table:formula')",
            "writer_path": "SetAttributeValue('table:formula', value)",
            "has_xml_doc": True,
        }],
        "no_dictionary_state": no_dict,
        "no_constant_returns": no_const,
    }


def _write_artifact(tmp_path: Path, tc_id: str, content: dict) -> Path:
    import yaml
    art_dir = tmp_path / ".local" / "design-artifacts"
    art_dir.mkdir(parents=True, exist_ok=True)
    art_file = art_dir / f"{tc_id}.yaml"
    art_file.write_text(yaml.dump(content), encoding="utf-8")
    return art_file


# ---------------------------------------------------------------------------
# Test 1: No .cs files in changed_files → fast PASS
# ---------------------------------------------------------------------------

class TestV153FastPath:

    def test_no_cs_files_returns_pass(self, tmp_path):
        """No .cs files in changed_files → V153 PASS immediately."""
        decl = _make_decl(changed_files=["src/python/fods/fods_parser.py"])
        result = validate_design_artifact_present(decl, tmp_path)
        assert result["result"] == "PASS"
        assert result["blocks_sprint"] is False
        assert "skip" in result["summary"].lower()

    def test_only_test_cs_file_not_in_src_net_passes(self, tmp_path):
        """C# file not under src/net/ is not caught (test files in tests/net/ are ok)."""
        decl = _make_decl(changed_files=["tests/net/fods/RoundtripTest.cs"])
        result = validate_design_artifact_present(decl, tmp_path)
        assert result["result"] == "PASS"
        assert result["blocks_sprint"] is False

    def test_src_net_cs_without_artifact_fails(self, tmp_path):
        """src/net/*.cs in changed_files + no artifact → V153 FAIL."""
        decl = _make_decl(changed_files=["src/net/fods/FodsCellFormula.cs"])
        result = validate_design_artifact_present(decl, tmp_path)
        assert result["result"] == "FAIL"
        assert result["blocks_sprint"] is True
        assert any(i["issue"] == "ARTIFACT_MISSING" for i in result["items"])


# ---------------------------------------------------------------------------
# Test 2: Artifact with is_partial_class=true → FAIL
# ---------------------------------------------------------------------------

class TestV153PartialClassForbidden:

    def test_partial_class_artifact_fails(self, tmp_path):
        """Artifact with is_partial_class=True → V153 FAIL, blocks_sprint=True."""
        art = _make_valid_artifact(is_partial_class=True)
        _write_artifact(tmp_path, "TC-TEST-001", art)
        decl = _make_decl(changed_files=["src/net/fods/FodsCellFormula.cs"])
        result = validate_design_artifact_present(decl, tmp_path)
        assert result["result"] == "FAIL"
        assert result["blocks_sprint"] is True
        assert any(i["issue"] == "PARTIAL_CLASS_FORBIDDEN" for i in result["items"])

    def test_non_partial_class_artifact_passes(self, tmp_path):
        """Artifact with is_partial_class=False → not a partial class violation."""
        art = _make_valid_artifact(is_partial_class=False)
        _write_artifact(tmp_path, "TC-TEST-001", art)
        decl = _make_decl(changed_files=["src/net/fods/FodsCellFormula.cs"])
        result = validate_design_artifact_present(decl, tmp_path)
        # Should not fail due to partial class
        partial_fails = [i for i in result["items"] if i.get("issue") == "PARTIAL_CLASS_FORBIDDEN"]
        assert len(partial_fails) == 0


# ---------------------------------------------------------------------------
# Test 3: spec_fact not in SAL → WARN (not FAIL)
# ---------------------------------------------------------------------------

class TestV153SpecFactSALWarn:

    def test_unknown_spec_fact_warns_not_fails(self, tmp_path):
        """spec_fact not in SAL → V153 WARN, blocks_sprint=False."""
        art = _make_valid_artifact(spec_fact="FACT-NONEXISTENT-99999")
        _write_artifact(tmp_path, "TC-TEST-001", art)
        # Write a fake SAL that doesn't contain the fact
        sal_dir = tmp_path / ".local" / "sal-output"
        sal_dir.mkdir(parents=True, exist_ok=True)
        (sal_dir / "sal-facts-latest.json").write_text(
            json.dumps([{"fact_id": "FACT-FODS-001", "text": "dummy fact"}]),
            encoding="utf-8",
        )
        decl = _make_decl(changed_files=["src/net/fods/FodsCellFormula.cs"])
        import design_artifact_validator as dav
        import unittest.mock as mock
        with mock.patch.object(dav, "_SAL_LATEST", sal_dir / "sal-facts-latest.json"):
            result = dav.validate_design_artifact_present(decl, tmp_path)
        # Should WARN (not FAIL) because SAL cross-ref is advisory only
        assert result["result"] in ("WARN", "PASS")
        assert result["blocks_sprint"] is False

    def test_known_spec_fact_passes(self, tmp_path):
        """spec_fact found in SAL → no SPEC_FACT_NOT_IN_SAL warning."""
        art = _make_valid_artifact(spec_fact="FACT-FODS-001")
        _write_artifact(tmp_path, "TC-TEST-001", art)
        sal_dir = tmp_path / ".local" / "sal-output"
        sal_dir.mkdir(parents=True, exist_ok=True)
        (sal_dir / "sal-facts-latest.json").write_text(
            json.dumps([{"fact_id": "FACT-FODS-001", "text": "known fact"}]),
            encoding="utf-8",
        )
        decl = _make_decl(changed_files=["src/net/fods/FodsCellFormula.cs"])
        import design_artifact_validator as dav
        import unittest.mock as mock
        with mock.patch.object(dav, "_SAL_LATEST", sal_dir / "sal-facts-latest.json"):
            result = dav.validate_design_artifact_present(decl, tmp_path)
        sal_warns = [i for i in result["items"] if i.get("issue") == "SPEC_FACT_NOT_IN_SAL"]
        assert len(sal_warns) == 0


# ---------------------------------------------------------------------------
# Test 4: Valid artifact, all constraints satisfied → PASS
# ---------------------------------------------------------------------------

class TestV153ValidArtifactPasses:

    def test_valid_artifact_all_constraints_pass(self, tmp_path):
        """Valid artifact with is_partial_class=False, no_dict=True, no_const=True → PASS."""
        art = _make_valid_artifact()
        _write_artifact(tmp_path, "TC-TEST-001", art)
        # Write SAL with the fact so no WARN fires
        sal_dir = tmp_path / ".local" / "sal-output"
        sal_dir.mkdir(parents=True, exist_ok=True)
        (sal_dir / "sal-facts-latest.json").write_text(
            json.dumps([{"fact_id": "FACT-FODS-001", "text": "known fact"}]),
            encoding="utf-8",
        )
        decl = _make_decl(changed_files=["src/net/fods/FodsCellFormula.cs"])
        import design_artifact_validator as dav
        import unittest.mock as mock
        with mock.patch.object(dav, "_SAL_LATEST", sal_dir / "sal-facts-latest.json"):
            result = dav.validate_design_artifact_present(decl, tmp_path)
        assert result["result"] == "PASS"
        assert result["blocks_sprint"] is False

    def test_dictionary_state_false_fails(self, tmp_path):
        """Artifact with no_dictionary_state=False → V153 FAIL."""
        art = _make_valid_artifact(no_dict=False)
        _write_artifact(tmp_path, "TC-TEST-001", art)
        decl = _make_decl(changed_files=["src/net/fods/FodsCellFormula.cs"])
        result = validate_design_artifact_present(decl, tmp_path)
        assert result["result"] == "FAIL"
        assert any(i["issue"] == "DICTIONARY_STATE_FORBIDDEN" for i in result["items"])

    def test_constant_returns_false_fails(self, tmp_path):
        """Artifact with no_constant_returns=False → V153 FAIL."""
        art = _make_valid_artifact(no_const=False)
        _write_artifact(tmp_path, "TC-TEST-001", art)
        decl = _make_decl(changed_files=["src/net/fods/FodsCellFormula.cs"])
        result = validate_design_artifact_present(decl, tmp_path)
        assert result["result"] == "FAIL"
        assert any(i["issue"] == "CONSTANT_RETURNS_FORBIDDEN" for i in result["items"])

    def test_estimated_loc_too_large_fails(self, tmp_path):
        """Artifact with estimated_loc >= 800 → V153 FAIL (exceeds V78 cap)."""
        art = _make_valid_artifact(estimated_loc=850)
        _write_artifact(tmp_path, "TC-TEST-001", art)
        decl = _make_decl(changed_files=["src/net/fods/FodsCellFormula.cs"])
        result = validate_design_artifact_present(decl, tmp_path)
        assert result["result"] == "FAIL"
        assert any(i["issue"] == "LOC_EXCEEDS_CAP" for i in result["items"])


# ---------------------------------------------------------------------------
# Helpers tests
# ---------------------------------------------------------------------------

def test_cs_files_in_changed_filters_correctly():
    """_cs_files_in_changed returns only src/net/*.cs entries."""
    decl = {
        "changed_files": [
            "src/net/fods/FodsDocument.cs",
            "src/python/fods/fods_parser.py",
            "tests/net/fods/RoundtripTest.cs",
        ]
    }
    result = _cs_files_in_changed(decl)
    assert result == ["src/net/fods/FodsDocument.cs"]
