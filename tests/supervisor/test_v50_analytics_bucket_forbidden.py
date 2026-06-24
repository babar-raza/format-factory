"""
test_v50_analytics_bucket_forbidden.py — Tests for V50 MODULE-NAME-001 extension.

Validates that *_analytics.py, *_analytics_extra.py, *_extra.py, *_misc.py,
and bare analytics.py are all blocked by V50.

Sprint: zesty-conjuring-peacock (2026-06-23)
"""
from __future__ import annotations

import sys
from pathlib import Path
from unittest import mock

import pytest

_REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO / "tools" / "supervisor"))

from governance_validators_ext import validate_forbidden_module_names


class TestV50AnalyticsBucketForbidden:
    """V50 must block *_analytics.py and related bucket patterns."""

    def _make_declaration(self, changed_files: list[str]) -> dict:
        return {"changed_files": changed_files, "planned_work_items": []}

    def test_format_prefixed_analytics_blocks_when_exists(self, tmp_path):
        """Sprint modifying abw_analytics.py while it exists -> FAIL."""
        repo = tmp_path / "repo"
        (repo / "src" / "python" / "abw").mkdir(parents=True)
        (repo / "src" / "python" / "abw" / "abw_analytics.py").write_text("x = 1\n")
        decl = self._make_declaration(["src/python/abw/abw_analytics.py"])
        result = validate_forbidden_module_names(decl, repo_root=repo)
        assert result["result"] == "FAIL"
        assert result["blocks_sprint"] is True
        assert len(result["items"]) == 1

    def test_format_prefixed_analytics_passes_when_deleted(self, tmp_path):
        """Sprint deleting abw_analytics.py (file gone) -> PASS."""
        repo = tmp_path / "repo"
        (repo / "src" / "python" / "abw").mkdir(parents=True)
        # File does NOT exist on disk (was deleted)
        decl = self._make_declaration(["src/python/abw/abw_analytics.py"])
        result = validate_forbidden_module_names(decl, repo_root=repo)
        assert result["result"] == "PASS"
        assert result["blocks_sprint"] is False

    def test_bare_analytics_blocks_when_exists(self, tmp_path):
        """Sprint creating bare analytics.py -> FAIL."""
        repo = tmp_path / "repo"
        (repo / "src" / "python" / "abw").mkdir(parents=True)
        (repo / "src" / "python" / "abw" / "analytics.py").write_text("x = 1\n")
        decl = self._make_declaration(["src/python/abw/analytics.py"])
        result = validate_forbidden_module_names(decl, repo_root=repo)
        assert result["result"] == "FAIL"
        assert result["blocks_sprint"] is True

    def test_analytics_extra_still_blocks(self, tmp_path):
        """*_analytics_extra.py -> FAIL (regression check)."""
        repo = tmp_path / "repo"
        (repo / "src" / "python" / "csv").mkdir(parents=True)
        (repo / "src" / "python" / "csv" / "csv_analytics_extra.py").write_text("x = 1\n")
        decl = self._make_declaration(["src/python/csv/csv_analytics_extra.py"])
        result = validate_forbidden_module_names(decl, repo_root=repo)
        assert result["result"] == "FAIL"
        assert result["blocks_sprint"] is True

    def test_extra_blocks(self, tmp_path):
        """*_extra.py -> FAIL."""
        repo = tmp_path / "repo"
        (repo / "src" / "python" / "csv").mkdir(parents=True)
        (repo / "src" / "python" / "csv" / "csv_extra.py").write_text("x = 1\n")
        decl = self._make_declaration(["src/python/csv/csv_extra.py"])
        result = validate_forbidden_module_names(decl, repo_root=repo)
        assert result["result"] == "FAIL"

    def test_misc_blocks(self, tmp_path):
        """*_misc.py -> FAIL."""
        repo = tmp_path / "repo"
        (repo / "src" / "python" / "csv").mkdir(parents=True)
        (repo / "src" / "python" / "csv" / "csv_misc.py").write_text("x = 1\n")
        decl = self._make_declaration(["src/python/csv/csv_misc.py"])
        result = validate_forbidden_module_names(decl, repo_root=repo)
        assert result["result"] == "FAIL"

    def test_spec_domain_module_passes(self, tmp_path):
        """Sprint creating word_document.py -> PASS."""
        repo = tmp_path / "repo"
        (repo / "src" / "python" / "abw").mkdir(parents=True)
        (repo / "src" / "python" / "abw" / "word_document.py").write_text("spec_qname = 'abw:document'\n")
        decl = self._make_declaration(["src/python/abw/word_document.py"])
        result = validate_forbidden_module_names(decl, repo_root=repo)
        assert result["result"] == "PASS"
        assert result["blocks_sprint"] is False

    def test_non_src_python_not_checked(self, tmp_path):
        """Files outside src/python/ are not checked."""
        repo = tmp_path / "repo"
        decl = self._make_declaration(["tools/supervisor/test_analytics.py"])
        result = validate_forbidden_module_names(decl, repo_root=repo)
        assert result["result"] == "PASS"

    def test_empty_declaration_passes(self, tmp_path):
        """Empty changed_files -> PASS."""
        repo = tmp_path / "repo"
        decl = self._make_declaration([])
        result = validate_forbidden_module_names(decl, repo_root=repo)
        assert result["result"] == "PASS"
