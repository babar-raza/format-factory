"""
tests/python/abw/test_r287_abw_workflow.py

Sprint: ff-sprint-s287-abw-installed-workflow-20260626
Authority: AWML 1.0 AbiWord document format

Tests for abw_installed_workflow() in abw_workflow.py.
"""
from __future__ import annotations

from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
_SAMPLE = _REPO / "samples" / "by-format" / "abw" / "minimal-document.abw"
_TWO_PARA = _REPO / "samples" / "by-format" / "abw" / "two-paragraphs.abw"


class TestAbwInstalledWorkflowImport:
    def test_importable_from_abw_workflow(self):
        from abw.abw_workflow import abw_installed_workflow
        assert callable(abw_installed_workflow)

    def test_importable_from_package(self):
        import abw
        assert hasattr(abw, "abw_installed_workflow")


class TestAbwInstalledWorkflowOutput:
    def test_returns_dict(self):
        from abw.abw_workflow import abw_installed_workflow
        assert isinstance(abw_installed_workflow(str(_SAMPLE)), dict)

    def test_format_field(self):
        from abw.abw_workflow import abw_installed_workflow
        assert abw_installed_workflow(str(_SAMPLE))["format"] == "abw"

    def test_loaded_true(self):
        from abw.abw_workflow import abw_installed_workflow
        assert abw_installed_workflow(str(_SAMPLE))["loaded"] is True

    def test_paragraph_count_integer(self):
        from abw.abw_workflow import abw_installed_workflow
        assert isinstance(abw_installed_workflow(str(_SAMPLE))["paragraph_count"], int)

    def test_section_count_integer(self):
        from abw.abw_workflow import abw_installed_workflow
        assert isinstance(abw_installed_workflow(str(_SAMPLE))["section_count"], int)

    def test_has_required_keys(self):
        from abw.abw_workflow import abw_installed_workflow
        r = abw_installed_workflow(str(_SAMPLE))
        assert {"format", "loaded", "paragraph_count", "section_count"}.issubset(r.keys())

    def test_two_paragraph_doc(self):
        from abw.abw_workflow import abw_installed_workflow
        r = abw_installed_workflow(str(_TWO_PARA))
        assert r["loaded"] is True and r["paragraph_count"] >= 2

    def test_consistent(self):
        from abw.abw_workflow import abw_installed_workflow
        r1 = abw_installed_workflow(str(_SAMPLE))
        r2 = abw_installed_workflow(str(_SAMPLE))
        assert r1["paragraph_count"] == r2["paragraph_count"]
