"""Tests for V64 (py.typed), V65 (__all__), V66 (multi-responsibility) governance validators.

TC-GOV-MACH-002: Add Missing Governance Validators.
"""
import os
import sys
import tempfile
from pathlib import Path

import pytest

# Ensure tools/supervisor is importable
_REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO / "tools" / "supervisor"))

from governance_validators import (
    validate_all_exports_declared,
    validate_multi_responsibility_file,
    validate_py_typed_marker,
)


# ---------------------------------------------------------------------------
# V64: validate_py_typed_marker
# ---------------------------------------------------------------------------

class TestV64PyTypedMarker:
    """V64: Python packages must have py.typed marker."""

    def test_pass_when_py_typed_exists(self, tmp_path):
        pkg = tmp_path / "src" / "python" / "fmtpkg"
        pkg.mkdir(parents=True)
        (pkg / "py.typed").write_text("")
        (pkg / "__init__.py").write_text("")
        decl = {"changed_files": ["src/python/fmtpkg/parser.py"]}
        result = validate_py_typed_marker(decl, repo_root=tmp_path)
        assert result["result"] == "PASS"
        assert "V64" in result["summary"]

    def test_warn_when_py_typed_missing(self, tmp_path):
        pkg = tmp_path / "src" / "python" / "fmtpkg"
        pkg.mkdir(parents=True)
        # No py.typed file
        decl = {"changed_files": ["src/python/fmtpkg/parser.py"]}
        result = validate_py_typed_marker(decl, repo_root=tmp_path)
        assert result["result"] == "WARN"
        assert result["blocks_sprint"] is False
        assert "V64" in result["summary"]
        assert any(i["package"] == "fmtpkg" for i in result["items"])

    def test_pass_when_no_python_changes(self, tmp_path):
        decl = {"changed_files": ["tools/supervisor/cycle.py"]}
        result = validate_py_typed_marker(decl, repo_root=tmp_path)
        assert result["result"] == "PASS"

    def test_pass_when_empty_changed_files(self, tmp_path):
        decl = {"changed_files": []}
        result = validate_py_typed_marker(decl, repo_root=tmp_path)
        assert result["result"] == "PASS"


# ---------------------------------------------------------------------------
# V65: validate_all_exports_declared
# ---------------------------------------------------------------------------

class TestV65AllExportsDeclared:
    """V65: Python packages must declare __all__ in __init__.py."""

    def test_pass_when_all_present(self, tmp_path):
        pkg = tmp_path / "src" / "python" / "fmtpkg"
        pkg.mkdir(parents=True)
        (pkg / "__init__.py").write_text("__all__ = ['parse']")
        decl = {"changed_files": ["src/python/fmtpkg/parser.py"]}
        result = validate_all_exports_declared(decl, repo_root=tmp_path)
        assert result["result"] == "PASS"
        assert "V65" in result["summary"]

    def test_warn_when_all_missing(self, tmp_path):
        pkg = tmp_path / "src" / "python" / "fmtpkg"
        pkg.mkdir(parents=True)
        (pkg / "__init__.py").write_text("from .parser import parse")
        decl = {"changed_files": ["src/python/fmtpkg/parser.py"]}
        result = validate_all_exports_declared(decl, repo_root=tmp_path)
        assert result["result"] == "WARN"
        assert result["blocks_sprint"] is False
        assert "V65" in result["summary"]
        assert any(i["package"] == "fmtpkg" for i in result["items"])

    def test_pass_when_no_init(self, tmp_path):
        pkg = tmp_path / "src" / "python" / "fmtpkg"
        pkg.mkdir(parents=True)
        # No __init__.py at all
        decl = {"changed_files": ["src/python/fmtpkg/parser.py"]}
        result = validate_all_exports_declared(decl, repo_root=tmp_path)
        assert result["result"] == "PASS"

    def test_pass_when_empty_changed_files(self, tmp_path):
        decl = {"changed_files": []}
        result = validate_all_exports_declared(decl, repo_root=tmp_path)
        assert result["result"] == "PASS"


# ---------------------------------------------------------------------------
# V66: validate_multi_responsibility_file
# ---------------------------------------------------------------------------

class TestV66MultiResponsibilityFile:
    """V66: Single Python file should not mix parser+model+serializer."""

    def test_pass_single_role(self, tmp_path):
        pkg = tmp_path / "src" / "python" / "fmtpkg"
        pkg.mkdir(parents=True)
        (pkg / "parser.py").write_text(
            "def parse_header(data): pass\ndef parse_body(data): pass\n"
        )
        decl = {"changed_files": ["src/python/fmtpkg/parser.py"]}
        result = validate_multi_responsibility_file(decl, repo_root=tmp_path)
        assert result["result"] == "PASS"
        assert "V66" in result["summary"]

    def test_fail_three_roles(self, tmp_path):
        pkg = tmp_path / "src" / "python" / "fmtpkg"
        pkg.mkdir(parents=True)
        code = (
            "class Doc:\n"
            "    spec_qname = 'test:doc'\n"
            "    namespace_uri = 'urn:test'\n"
            "    def __init__(self): pass\n"
            "def parse_file(path): pass\n"
            "def load_data(path): pass\n"
            "def write_output(data, path): pass\n"
            "def serialize(data): pass\n"
        )
        (pkg / "codec.py").write_text(code)
        decl = {"changed_files": ["src/python/fmtpkg/codec.py"]}
        result = validate_multi_responsibility_file(decl, repo_root=tmp_path)
        assert result["result"] == "FAIL"
        assert "V66" in result["summary"]
        assert len(result["items"]) == 1
        assert set(result["items"][0]["roles"]) == {"parser", "model", "serializer"}

    def test_pass_two_roles(self, tmp_path):
        pkg = tmp_path / "src" / "python" / "fmtpkg"
        pkg.mkdir(parents=True)
        code = "def parse_file(path): pass\ndef load_data(path): pass\n"
        (pkg / "codec.py").write_text(code)
        decl = {"changed_files": ["src/python/fmtpkg/codec.py"]}
        result = validate_multi_responsibility_file(decl, repo_root=tmp_path)
        assert result["result"] == "PASS"

    def test_skip_analytics_files(self, tmp_path):
        pkg = tmp_path / "src" / "python" / "fmtpkg"
        pkg.mkdir(parents=True)
        code = (
            "class Doc:\n    spec_qname = 'x'\n    namespace_uri = 'y'\n    def __init__(self): pass\n"
            "def parse_file(p): pass\ndef write_output(d, p): pass\n"
        )
        (pkg / "fmtpkg_analytics.py").write_text(code)
        decl = {"changed_files": ["src/python/fmtpkg/fmtpkg_analytics.py"]}
        result = validate_multi_responsibility_file(decl, repo_root=tmp_path)
        assert result["result"] == "PASS"

    def test_skip_init_files(self, tmp_path):
        pkg = tmp_path / "src" / "python" / "fmtpkg"
        pkg.mkdir(parents=True)
        decl = {"changed_files": ["src/python/fmtpkg/__init__.py"]}
        result = validate_multi_responsibility_file(decl, repo_root=tmp_path)
        assert result["result"] == "PASS"

    def test_skip_non_python_changes(self, tmp_path):
        decl = {"changed_files": ["tools/supervisor/cycle.py"]}
        result = validate_multi_responsibility_file(decl, repo_root=tmp_path)
        assert result["result"] == "PASS"

    def test_pass_empty_changed_files(self, tmp_path):
        decl = {"changed_files": []}
        result = validate_multi_responsibility_file(decl, repo_root=tmp_path)
        assert result["result"] == "PASS"
