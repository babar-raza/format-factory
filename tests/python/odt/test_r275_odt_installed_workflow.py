"""
tests/python/odt/test_r275_odt_installed_workflow.py

Sprint: ff-sprint-s275-odt-installed-workflow-20260626
Authority: ODF ODT text document format

Tests for odt_installed_workflow() in odt_workflow.py.
"""
from __future__ import annotations

from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_SAMPLE = _REPO / "samples" / "by-format" / "odt" / "valid" / "minimal-document.odt"
_TWO_PARA = _REPO / "samples" / "by-format" / "odt" / "valid" / "two-paragraphs.odt"


class TestOdtInstalledWorkflowImport:
    """odt_installed_workflow is importable and callable."""

    def test_importable_from_odt_workflow(self):
        from odt.odt_workflow import odt_installed_workflow
        assert callable(odt_installed_workflow)

    def test_importable_from_package(self):
        import odt
        assert hasattr(odt, "odt_installed_workflow")


class TestOdtInstalledWorkflowOutput:
    """odt_installed_workflow returns correct output structure."""

    def test_returns_dict(self):
        from odt.odt_workflow import odt_installed_workflow
        result = odt_installed_workflow(str(_SAMPLE))
        assert isinstance(result, dict)

    def test_format_field_is_odt(self):
        from odt.odt_workflow import odt_installed_workflow
        result = odt_installed_workflow(str(_SAMPLE))
        assert result["format"] == "odt"

    def test_loaded_field_is_true(self):
        from odt.odt_workflow import odt_installed_workflow
        result = odt_installed_workflow(str(_SAMPLE))
        assert result["loaded"] is True

    def test_paragraph_count_is_integer(self):
        from odt.odt_workflow import odt_installed_workflow
        result = odt_installed_workflow(str(_SAMPLE))
        assert isinstance(result["paragraph_count"], int)

    def test_heading_count_is_integer(self):
        from odt.odt_workflow import odt_installed_workflow
        result = odt_installed_workflow(str(_SAMPLE))
        assert isinstance(result["heading_count"], int)

    def test_has_all_required_keys(self):
        from odt.odt_workflow import odt_installed_workflow
        result = odt_installed_workflow(str(_SAMPLE))
        assert {"format", "loaded", "paragraph_count", "heading_count"}.issubset(result.keys())

    def test_paragraph_count_positive(self):
        from odt.odt_workflow import odt_installed_workflow
        result = odt_installed_workflow(str(_SAMPLE))
        assert result["paragraph_count"] >= 1

    def test_consistent_across_calls(self):
        from odt.odt_workflow import odt_installed_workflow
        r1 = odt_installed_workflow(str(_SAMPLE))
        r2 = odt_installed_workflow(str(_SAMPLE))
        assert r1["paragraph_count"] == r2["paragraph_count"]

    def test_two_paragraphs_doc(self):
        from odt.odt_workflow import odt_installed_workflow
        result = odt_installed_workflow(str(_TWO_PARA))
        assert result["loaded"] is True
        assert result["paragraph_count"] >= 2
