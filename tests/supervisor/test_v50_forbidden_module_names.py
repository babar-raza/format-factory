"""
tests/supervisor/test_v50_forbidden_module_names.py

Tests for V50 validate_forbidden_module_names (MODULE-NAME-001).
TC-ANAL-SEG-HEAL-001 (2026-06-22).

Covers:
  - 5 negative controls: forbidden suffix files that EXIST on disk → FAIL
  - 5 positive controls: legal module names → PASS
  - 1 deletion-exemption: forbidden file does NOT exist on disk → PASS (deletion allowed)
  - _extra, _misc pattern coverage
"""
from __future__ import annotations

import sys
import tempfile
import os
from pathlib import Path

import pytest

# Load validator from ext module
sys.path.insert(0, str(Path(__file__).parents[2] / "tools" / "supervisor"))
from governance_validators_ext import validate_forbidden_module_names


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _decl(changed_files: list[str]) -> dict:
    return {"changed_files": changed_files, "planned_work_items": []}


class TestV50ForbiddenModuleNames:

    def test_analytics_extra_file_exists_is_blocked(self, tmp_path):
        """Negative control: *_analytics_extra.py that EXISTS → FAIL."""
        target = tmp_path / "src" / "python" / "fodg" / "fodg_analytics_extra.py"
        target.parent.mkdir(parents=True)
        target.write_text("def fodg_extra_fn(): pass\n")
        decl = _decl(["src/python/fodg/fodg_analytics_extra.py"])
        result = validate_forbidden_module_names(decl, repo_root=tmp_path)
        assert result["result"] == "FAIL"
        assert result["blocks_sprint"] is True
        assert any("analytics_extra" in str(v) for v in result["items"])

    def test_extra_file_exists_is_blocked(self, tmp_path):
        """Negative control: *_extra.py that EXISTS → FAIL."""
        target = tmp_path / "src" / "python" / "csv" / "csv_extra.py"
        target.parent.mkdir(parents=True)
        target.write_text("def csv_extra_fn(): pass\n")
        decl = _decl(["src/python/csv/csv_extra.py"])
        result = validate_forbidden_module_names(decl, repo_root=tmp_path)
        assert result["result"] == "FAIL"
        assert result["blocks_sprint"] is True

    def test_misc_file_exists_is_blocked(self, tmp_path):
        """Negative control: *_misc.py that EXISTS → FAIL."""
        target = tmp_path / "src" / "python" / "ods" / "ods_misc.py"
        target.parent.mkdir(parents=True)
        target.write_text("def ods_misc_fn(): pass\n")
        decl = _decl(["src/python/ods/ods_misc.py"])
        result = validate_forbidden_module_names(decl, repo_root=tmp_path)
        assert result["result"] == "FAIL"
        assert result["blocks_sprint"] is True

    def test_multiple_forbidden_files_all_blocked(self, tmp_path):
        """Negative control: multiple forbidden files → FAIL with multiple items."""
        for path in ["src/python/xcf/xcf_extra.py", "src/python/zst/zst_misc.py"]:
            p = tmp_path / path
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text("def fn(): pass\n")
        decl = _decl(["src/python/xcf/xcf_extra.py", "src/python/zst/zst_misc.py"])
        result = validate_forbidden_module_names(decl, repo_root=tmp_path)
        assert result["result"] == "FAIL"
        assert len(result["items"]) == 2

    def test_forbidden_suffix_in_subdirectory_is_blocked(self, tmp_path):
        """Negative control: forbidden suffix in nested path → FAIL."""
        target = tmp_path / "src" / "python" / "gnumeric" / "gnumeric_analytics_extra.py"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("def gnumeric_fn(): pass\n")
        decl = _decl(["src/python/gnumeric/gnumeric_analytics_extra.py"])
        result = validate_forbidden_module_names(decl, repo_root=tmp_path)
        assert result["result"] == "FAIL"

    def test_drawing_document_is_not_blocked(self, tmp_path):
        """Positive control: drawing_document.py is NOT a forbidden name → PASS."""
        target = tmp_path / "src" / "python" / "fodg" / "drawing_document.py"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("spec_qname = 'office:document'\n")
        decl = _decl(["src/python/fodg/drawing_document.py"])
        result = validate_forbidden_module_names(decl, repo_root=tmp_path)
        assert result["result"] == "PASS"
        assert result["blocks_sprint"] is False

    def test_analytics_file_is_blocked(self, tmp_path):
        """Negative control: *_analytics.py → FAIL (extended 2026-06-23, zesty-conjuring-peacock).

        V50 was extended on 2026-06-23 to also block format-prefixed *_analytics.py files
        since the product deepening rotation is suspended and no new analytics should be created.
        """
        target = tmp_path / "src" / "python" / "csv" / "csv_analytics.py"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("def csv_fn(): pass\n")
        decl = _decl(["src/python/csv/csv_analytics.py"])
        result = validate_forbidden_module_names(decl, repo_root=tmp_path)
        assert result["result"] == "FAIL"
        assert result["blocks_sprint"] is True

    def test_codec_file_is_not_blocked(self, tmp_path):
        """Positive control: *_codec.py → PASS."""
        target = tmp_path / "src" / "python" / "fodg" / "fodg_codec.py"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("def load(): pass\n")
        decl = _decl(["src/python/fodg/fodg_codec.py"])
        result = validate_forbidden_module_names(decl, repo_root=tmp_path)
        assert result["result"] == "PASS"

    def test_empty_changed_files_passes(self):
        """Positive control: no changed files → PASS."""
        decl = _decl([])
        result = validate_forbidden_module_names(decl)
        assert result["result"] == "PASS"
        assert result["blocks_sprint"] is False

    def test_non_src_python_path_is_not_blocked(self, tmp_path):
        """Positive control: forbidden suffix outside src/python/ → PASS (not in scope)."""
        target = tmp_path / "tests" / "fodg_extra.py"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("def fn(): pass\n")
        decl = _decl(["tests/fodg_extra.py"])
        result = validate_forbidden_module_names(decl, repo_root=tmp_path)
        assert result["result"] == "PASS"

    def test_deletion_exemption_file_not_on_disk(self, tmp_path):
        """Deletion-exemption: forbidden file does NOT exist on disk → PASS.

        This verifies that deletion sprints are not self-blocked by V50.
        If a sprint is deleting fodg_analytics_extra.py, the file won't exist
        on disk at validation time, so V50 must not flag it.
        """
        # fodg_analytics_extra.py is in changed_files but does NOT exist on disk
        decl = _decl(["src/python/fodg/fodg_analytics_extra.py"])
        result = validate_forbidden_module_names(decl, repo_root=tmp_path)
        assert result["result"] == "PASS", (
            "V50 should PASS when the forbidden file no longer exists on disk "
            "(deletion sprints must not be self-blocked)"
        )
        assert result["blocks_sprint"] is False

    def test_result_structure_has_required_keys(self):
        """Structural test: result dict has all required keys."""
        result = validate_forbidden_module_names({"changed_files": []})
        assert "validator" in result
        assert "result" in result
        assert "blocks_sprint" in result
        assert "items" in result
        assert "summary" in result
        assert result["validator"] == "validate_forbidden_module_names"
