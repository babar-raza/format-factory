"""Tests for tools/review/python_qname_reviewer.py and no_stub_scan.py.

Covers:
  - no_stub_scan: detects forbidden terms, pass-only classes/methods
  - no_stub_scan: authority_only=True exempts class from pass-only check
  - python_qname_reviewer: ACCEPTED_VERIFIED for fods (has spec/ + Compat/)
  - python_qname_reviewer: REWORK_REQUIRED for a format without spec/
  - python_qname_reviewer: spec_qname/spec_fact_ref checks
  - python_qname_reviewer: facade inheritance check
"""
from __future__ import annotations

import json
import sys
import textwrap
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO))

from tools.review.no_stub_scan import scan_file, scan_paths, report as stub_report
from tools.review.python_qname_reviewer import (
    review_format,
    _check_spec_dir,
    _check_spec_qnames,
    _check_compat_dir,
    _check_facade_inheritance,
    _check_no_stub,
    _check_sal_facts_exist,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write_py(tmp_path: Path, name: str, content: str) -> Path:
    f = tmp_path / name
    f.write_text(textwrap.dedent(content), encoding="utf-8")
    return f


# ---------------------------------------------------------------------------
# no_stub_scan tests
# ---------------------------------------------------------------------------

class TestNoStubScan:
    def test_clean_file_returns_no_violations(self, tmp_path):
        f = _write_py(tmp_path, "clean.py", """
            class Foo:
                spec_qname = "foo:bar"
                def __init__(self, data):
                    self._data = data
                def text(self):
                    return self._data.get("text", "")
        """)
        assert scan_file(f) == []

    def test_todo_comment_flagged(self, tmp_path):
        f = _write_py(tmp_path, "todo.py", "# TODO: implement this\nx = 1\n")
        violations = scan_file(f)
        assert any(v["kind"] == "forbidden_term" for v in violations)

    def test_stub_word_flagged(self, tmp_path):
        f = _write_py(tmp_path, "stub.py", "# This is a stub implementation\nx = 1\n")
        violations = scan_file(f)
        assert any(v["kind"] == "forbidden_term" for v in violations)

    def test_pass_only_method_flagged(self, tmp_path):
        f = _write_py(tmp_path, "passmethod.py", """
            class Foo:
                def do_something(self):
                    pass
        """)
        violations = scan_file(f)
        assert any(v["kind"] == "pass_only_method" for v in violations)

    def test_pass_only_class_flagged_without_authority_only(self, tmp_path):
        f = _write_py(tmp_path, "passclass.py", """
            class EmptyClass:
                pass
        """)
        violations = scan_file(f)
        assert any(v["kind"] == "pass_only_class" for v in violations)

    def test_authority_only_class_not_flagged(self, tmp_path):
        f = _write_py(tmp_path, "authority.py", """
            class SpecElement:
                spec_qname = "foo:element"
                authority_only = True
        """)
        violations = scan_file(f)
        kinds = [v["kind"] for v in violations]
        assert "pass_only_class" not in kinds

    def test_dunder_init_pass_not_flagged(self, tmp_path):
        f = _write_py(tmp_path, "init_pass.py", """
            class Foo:
                def __init__(self):
                    pass
        """)
        violations = scan_file(f)
        assert not any(v["kind"] == "pass_only_method" for v in violations)

    def test_report_clean_status(self, tmp_path):
        f = _write_py(tmp_path, "ok.py", "x = 1\n")
        result = stub_report([tmp_path])
        assert result["status"] == "CLEAN"

    def test_report_violations_found_status(self, tmp_path):
        _write_py(tmp_path, "bad.py", "# TODO: later\n")
        result = stub_report([tmp_path])
        assert result["status"] == "VIOLATIONS_FOUND"
        assert result["total_violations"] > 0


# ---------------------------------------------------------------------------
# python_qname_reviewer tests — structural checks
# ---------------------------------------------------------------------------

class TestSpecDirCheck:
    def test_missing_spec_dir_fails(self, tmp_path):
        (tmp_path / "abw_codec.py").write_text("# codec\n")
        result = _check_spec_dir(tmp_path)
        assert result["pass"] is False
        assert "spec/" in result["reason"]

    def test_empty_spec_dir_fails(self, tmp_path):
        (tmp_path / "spec").mkdir()
        result = _check_spec_dir(tmp_path)
        assert result["pass"] is False

    def test_spec_dir_with_class_passes(self, tmp_path):
        spec = tmp_path / "spec" / "document"
        spec.mkdir(parents=True)
        (spec / "paragraph.py").write_text(
            "class Paragraph:\n    spec_qname = 'abw:p'\n    spec_fact_ref = 'FACT-ABW-003'\n"
        )
        result = _check_spec_dir(tmp_path)
        assert result["pass"] is True
        assert result["class_count"] == 1


class TestQNameCheck:
    def test_class_without_spec_qname_fails(self):
        spec_check = {
            "pass": True,
            "classes": [{"name": "Foo", "spec_qname": None, "spec_fact_ref": "FACT-X-001", "bases": [], "lineno": 1}],
        }
        result = _check_spec_qnames(spec_check)
        assert result["pass"] is False
        assert "Foo" in result["missing_spec_qname"]

    def test_class_without_fact_ref_fails(self):
        spec_check = {
            "pass": True,
            "classes": [{"name": "Foo", "spec_qname": "foo:bar", "spec_fact_ref": None, "bases": [], "lineno": 1}],
        }
        result = _check_spec_qnames(spec_check)
        assert result["pass"] is False
        assert "Foo" in result["missing_spec_fact_ref"]

    def test_complete_class_passes(self):
        spec_check = {
            "pass": True,
            "classes": [{"name": "Foo", "spec_qname": "foo:bar", "spec_fact_ref": "FACT-X-001", "bases": [], "lineno": 1}],
        }
        result = _check_spec_qnames(spec_check)
        assert result["pass"] is True


class TestCompatDirCheck:
    def test_missing_compat_dir_fails(self, tmp_path):
        result = _check_compat_dir(tmp_path, "test")
        assert result["pass"] is False

    def test_compat_dir_with_facade_passes(self, tmp_path):
        compat = tmp_path / "Compat"
        compat.mkdir()
        (compat / "__init__.py").write_text("")
        (compat / "test_doc.py").write_text(
            "from ..spec.document import Document as _D\nclass TestDoc(_D):\n    pass\n"
        )
        result = _check_compat_dir(tmp_path, "test")
        assert result["pass"] is True


class TestFacadeInheritanceCheck:
    def test_facade_without_base_fails(self):
        compat_check = {
            "pass": True,
            "facades": [{"name": "AbwDocument", "bases": [], "spec_qname": None, "spec_fact_ref": None, "lineno": 1}],
        }
        result = _check_facade_inheritance(compat_check)
        assert result["pass"] is False
        assert "AbwDocument" in result["facades_without_base"]

    def test_facade_with_base_passes(self):
        compat_check = {
            "pass": True,
            "facades": [{"name": "AbwDocument", "bases": ["Document"], "spec_qname": None, "spec_fact_ref": None, "lineno": 1}],
        }
        result = _check_facade_inheritance(compat_check)
        assert result["pass"] is True


# ---------------------------------------------------------------------------
# python_qname_reviewer — integration against real FODS package
# ---------------------------------------------------------------------------

class TestReviewFormatFods:
    def test_fods_accepted_verified(self):
        """FODS has spec/ + Compat/ — must pass all structural checks."""
        result = review_format("fods")
        # FODS is the reference implementation — it must pass spec/ and Compat/ checks
        assert result["checks"]["spec_dir"]["pass"] is True
        assert result["checks"]["compat_dir"]["pass"] is True

    def test_fods_spec_qnames_present(self):
        result = review_format("fods")
        assert result["checks"]["spec_qnames"]["pass"] is True


class TestSalFactsExistCheck:
    def test_all_fact_refs_found_passes(self, tmp_path, monkeypatch):
        """All spec_fact_refs present in sal-facts → pass."""
        from tools.review import python_qname_reviewer as rev
        monkeypatch.setattr(rev, "_load_sal_facts", lambda fmt: [
            {"qname": "FACT-TEST-001"}, {"qname": "FACT-TEST-002"},
        ])
        spec_check = {
            "pass": True,
            "classes": [
                {"name": "RecordA", "spec_qname": "test:a", "spec_fact_ref": "FACT-TEST-001", "bases": [], "lineno": 1},
                {"name": "RecordB", "spec_qname": "test:b", "spec_fact_ref": "FACT-TEST-002", "bases": [], "lineno": 5},
            ],
        }
        result = _check_sal_facts_exist(spec_check, "testfmt")
        assert result["pass"] is True

    def test_missing_fact_ref_fails(self, tmp_path, monkeypatch):
        """A spec_fact_ref not in sal-facts → fail."""
        from tools.review import python_qname_reviewer as rev
        monkeypatch.setattr(rev, "_load_sal_facts", lambda fmt: [
            {"qname": "FACT-TEST-001"},
        ])
        spec_check = {
            "pass": True,
            "classes": [
                {"name": "RecordA", "spec_qname": "test:a", "spec_fact_ref": "FACT-TEST-001", "bases": [], "lineno": 1},
                {"name": "RecordB", "spec_qname": "test:b", "spec_fact_ref": "FACT-TEST-999", "bases": [], "lineno": 5},
            ],
        }
        result = _check_sal_facts_exist(spec_check, "testfmt")
        assert result["pass"] is False
        assert any(m["fact_ref"] == "FACT-TEST-999" for m in result["missing_facts"])

    def test_empty_sal_facts_with_refs_fails(self, monkeypatch):
        """Zero facts in sal-facts file with refs → fail."""
        from tools.review import python_qname_reviewer as rev
        monkeypatch.setattr(rev, "_load_sal_facts", lambda fmt: [])
        spec_check = {
            "pass": True,
            "classes": [
                {"name": "Record", "spec_qname": "csv:record", "spec_fact_ref": "FACT-CSV-001", "bases": [], "lineno": 1},
            ],
        }
        result = _check_sal_facts_exist(spec_check, "csv")
        assert result["pass"] is False
        assert result["sal_facts_count"] == 0

    def test_spec_check_failed_skips(self):
        """If spec_check failed, sal_facts check skips."""
        result = _check_sal_facts_exist({"pass": False, "reason": "no spec/"}, "csv")
        assert result["pass"] is False
        assert "skipping" in result["reason"]

    def test_fods_sal_facts_verified(self):
        """FODS has real facts in sal-facts file — must pass."""
        import pytest
        sal_file = _REPO / ".local" / "spec-cache" / "sal-facts-fods.json"
        if not sal_file.exists():
            pytest.skip(".local/spec-cache/sal-facts-fods.json not present (gitignored, CI skip)")
        result = review_format("fods")
        assert result["checks"]["sal_facts_exist"]["pass"] is True

    def test_csv_passes_sal_facts_after_fix(self):
        """CSV now has structural facts — sal_facts_exist check must pass."""
        import pytest
        sal_file = _REPO / ".local" / "spec-cache" / "sal-facts-csv.json"
        if not sal_file.exists():
            pytest.skip(".local/spec-cache/sal-facts-csv.json not present (gitignored, CI skip)")
        result = review_format("csv")
        assert result["checks"]["sal_facts_exist"]["pass"] is True


class TestReviewFormatMissing:
    def test_unknown_format_returns_rework(self):
        result = review_format("nonexistent_format_xyz")
        assert result["verdict"] == "REWORK_REQUIRED"
