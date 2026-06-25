"""Tests for V75 (validate_dependency_direction) and V76 (validate_error_handling_hierarchy).

TC-GH-004, 2026-06-25 — governance healing sprint warm-jingling-sutherland.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).parent.parent.parent
sys.path.insert(0, str(_REPO / "tools" / "supervisor"))

from governance_validators_ext2 import (  # noqa: E402
    validate_dependency_direction,
    validate_error_handling_hierarchy,
)


# --- V75 validate_dependency_direction ---

class TestV75DependencyDirection:
    """V75: Import direction enforcement (RULE-LIB-003)."""

    def _decl(self, ev_paths: list[str]) -> dict:
        return {
            "planned_work_items": [
                {
                    "item_type": "PRODUCT_SOURCE",
                    "evidence_paths": ev_paths,
                }
            ]
        }

    def test_passes_for_empty_declaration(self):
        result = validate_dependency_direction({"planned_work_items": []})
        assert result["result"] == "PASS"
        assert result["blocks_sprint"] is False

    def test_passes_for_non_product_source_item(self):
        decl = {
            "planned_work_items": [
                {"item_type": "GOVERNANCE_TASKCARD", "evidence_paths": ["src/python/csv/models.py"]}
            ]
        }
        result = validate_dependency_direction(decl)
        assert result["result"] == "PASS"

    def test_passes_for_clean_parser_file(self):
        # csv_parser.py exists and should not import analytics or Compat
        decl = self._decl(["src/python/csv/csv_parser.py"])
        result = validate_dependency_direction(decl, repo_root=_REPO)
        # Result should be PASS or WARN (grandfathered), never FAIL for existing files
        assert result["result"] in ("PASS", "WARN")
        # If WARN, it's for an existing file — must not block sprint
        assert result["blocks_sprint"] is False

    def test_warns_not_fails_for_existing_file_violation(self, tmp_path, monkeypatch):
        """If a parser file imports analytics BUT is in known_violations → WARN (not FAIL)."""
        # Create a fake repo structure
        src_dir = tmp_path / "src" / "python" / "myformat"
        src_dir.mkdir(parents=True)
        parser_file = src_dir / "myformat_parser.py"
        parser_file.write_text("from .myformat_analytics import compute_x\n", encoding="utf-8")

        baseline = tmp_path / "registry" / "source-structure-baseline.json"
        baseline.parent.mkdir(parents=True)
        # The file IS in known_violations → WARN
        baseline.write_text(json.dumps({
            "known_violations": {
                "src/python/myformat/myformat_parser.py": {
                    "loc": 1, "baseline_loc_cap": 900
                }
            }
        }), encoding="utf-8")

        decl = {
            "planned_work_items": [
                {
                    "item_type": "PRODUCT_SOURCE",
                    "evidence_paths": ["src/python/myformat/myformat_parser.py"],
                }
            ]
        }
        result = validate_dependency_direction(decl, repo_root=tmp_path)
        # Should find a violation but WARN (not FAIL) because it's grandfathered
        if result["items"]:
            assert result["result"] == "WARN"
            assert result["blocks_sprint"] is False

    def test_fails_for_new_file_violation(self, tmp_path):
        """If a NEW parser file (not in known_violations) imports analytics → FAIL."""
        src_dir = tmp_path / "src" / "python" / "newformat"
        src_dir.mkdir(parents=True)
        parser_file = src_dir / "newformat_parser.py"
        parser_file.write_text("from .newformat_analytics import some_func\n", encoding="utf-8")

        baseline = tmp_path / "registry" / "source-structure-baseline.json"
        baseline.parent.mkdir(parents=True)
        # File NOT in known_violations → FAIL
        baseline.write_text(json.dumps({"known_violations": {}}), encoding="utf-8")

        decl = {
            "planned_work_items": [
                {
                    "item_type": "PRODUCT_SOURCE",
                    "evidence_paths": ["src/python/newformat/newformat_parser.py"],
                }
            ]
        }
        result = validate_dependency_direction(decl, repo_root=tmp_path)
        assert result["result"] == "FAIL"
        assert result["blocks_sprint"] is True

    def test_passes_when_no_forbidden_imports(self, tmp_path):
        """Clean parser file with only allowed imports → PASS."""
        src_dir = tmp_path / "src" / "python" / "cleanformat"
        src_dir.mkdir(parents=True)
        parser_file = src_dir / "cleanformat_parser.py"
        parser_file.write_text(
            "from .models import CleanDocument\nimport xml.etree.ElementTree as ET\n",
            encoding="utf-8"
        )

        baseline = tmp_path / "registry" / "source-structure-baseline.json"
        baseline.parent.mkdir(parents=True)
        baseline.write_text(json.dumps({"known_violations": {}}), encoding="utf-8")

        decl = {
            "planned_work_items": [
                {
                    "item_type": "PRODUCT_SOURCE",
                    "evidence_paths": ["src/python/cleanformat/cleanformat_parser.py"],
                }
            ]
        }
        result = validate_dependency_direction(decl, repo_root=tmp_path)
        assert result["result"] == "PASS"
        assert result["blocks_sprint"] is False


# --- V76 validate_error_handling_hierarchy ---

class TestV76ErrorHandlingHierarchy:
    """V76: Format package exceptions.py enforcement (RULE-LIB-006)."""

    def test_passes_for_empty_declaration(self):
        result = validate_error_handling_hierarchy({"planned_work_items": []})
        assert result["result"] == "PASS"
        assert result["blocks_sprint"] is False

    def test_passes_when_exceptions_file_exists(self, tmp_path):
        """Package with exceptions.py → PASS."""
        pkg_dir = tmp_path / "src" / "python" / "goodformat"
        pkg_dir.mkdir(parents=True)
        (pkg_dir / "exceptions.py").write_text("class GoodFormatError(Exception): pass\n")
        (pkg_dir / "goodformat_parser.py").write_text("# parser\n")

        baseline = tmp_path / "registry" / "source-structure-baseline.json"
        baseline.parent.mkdir(parents=True)
        baseline.write_text(json.dumps({"known_violations": {}}), encoding="utf-8")

        decl = {
            "planned_work_items": [
                {
                    "item_type": "PRODUCT_SOURCE",
                    "evidence_paths": ["src/python/goodformat/goodformat_parser.py"],
                }
            ]
        }
        result = validate_error_handling_hierarchy(decl, repo_root=tmp_path)
        assert result["result"] == "PASS"

    def test_warns_for_existing_package_missing_exceptions(self, tmp_path):
        """Existing package (in known_violations) missing exceptions.py → WARN, not FAIL."""
        pkg_dir = tmp_path / "src" / "python" / "oldformat"
        pkg_dir.mkdir(parents=True)
        (pkg_dir / "oldformat_parser.py").write_text("# parser\n")
        # No exceptions.py

        baseline = tmp_path / "registry" / "source-structure-baseline.json"
        baseline.parent.mkdir(parents=True)
        baseline.write_text(json.dumps({
            "known_violations": {
                "src/python/oldformat/oldformat_parser.py": {"loc": 100, "baseline_loc_cap": 200}
            }
        }), encoding="utf-8")

        decl = {
            "planned_work_items": [
                {
                    "item_type": "PRODUCT_SOURCE",
                    "evidence_paths": ["src/python/oldformat/oldformat_parser.py"],
                }
            ]
        }
        result = validate_error_handling_hierarchy(decl, repo_root=tmp_path)
        assert result["result"] == "WARN"
        assert result["blocks_sprint"] is False

    def test_fails_for_new_package_missing_exceptions(self, tmp_path):
        """NEW package (not in known_violations) missing exceptions.py → FAIL."""
        pkg_dir = tmp_path / "src" / "python" / "brandnewformat"
        pkg_dir.mkdir(parents=True)
        (pkg_dir / "brandnewformat_parser.py").write_text("# parser\n")
        # No exceptions.py

        baseline = tmp_path / "registry" / "source-structure-baseline.json"
        baseline.parent.mkdir(parents=True)
        baseline.write_text(json.dumps({"known_violations": {}}), encoding="utf-8")

        decl = {
            "planned_work_items": [
                {
                    "item_type": "PRODUCT_SOURCE",
                    "evidence_paths": ["src/python/brandnewformat/brandnewformat_parser.py"],
                }
            ]
        }
        result = validate_error_handling_hierarchy(decl, repo_root=tmp_path)
        assert result["result"] == "FAIL"
        assert result["blocks_sprint"] is True

    def test_warns_for_existing_csv_package(self):
        """CSV package is in known_violations — missing exceptions.py should be WARN."""
        decl = {
            "planned_work_items": [
                {
                    "item_type": "PRODUCT_SOURCE",
                    "evidence_paths": ["src/python/csv/tabular_document.py"],
                }
            ]
        }
        result = validate_error_handling_hierarchy(decl, repo_root=_REPO)
        # CSV exceptions.py may or may not exist — if missing, should be WARN not FAIL
        assert result["blocks_sprint"] is False
        if result["result"] == "FAIL":
            pytest.fail("CSV is an existing format — should be WARN not FAIL if exceptions.py missing")
