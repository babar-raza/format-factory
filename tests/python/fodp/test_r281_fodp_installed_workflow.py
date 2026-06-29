"""
tests/python/fodp/test_r281_fodp_installed_workflow.py

Sprint: ff-sprint-s281-fodp-installed-workflow-20260626
Authority: ODF FODP presentation format

Tests for fodp_installed_workflow() in fodp_workflow.py.
"""
from __future__ import annotations

from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_SAMPLE = _REPO / "samples" / "by-format" / "fodp" / "minimal-presentation.fodp"
_TWO_SLIDES = _REPO / "samples" / "by-format" / "fodp" / "two-slides-basic.fodp"


class TestFodpInstalledWorkflowImport:
    """fodp_installed_workflow is importable and callable."""

    def test_importable_from_fodp_workflow(self):
        from fodp.fodp_workflow import fodp_installed_workflow
        assert callable(fodp_installed_workflow)

    def test_importable_from_package(self):
        import fodp
        assert hasattr(fodp, "fodp_installed_workflow")


class TestFodpInstalledWorkflowOutput:
    """fodp_installed_workflow returns correct output structure."""

    def test_returns_dict(self):
        from fodp.fodp_workflow import fodp_installed_workflow
        result = fodp_installed_workflow(str(_SAMPLE))
        assert isinstance(result, dict)

    def test_format_field_is_fodp(self):
        from fodp.fodp_workflow import fodp_installed_workflow
        result = fodp_installed_workflow(str(_SAMPLE))
        assert result["format"] == "fodp"

    def test_loaded_field_is_true(self):
        from fodp.fodp_workflow import fodp_installed_workflow
        result = fodp_installed_workflow(str(_SAMPLE))
        assert result["loaded"] is True

    def test_page_count_is_integer(self):
        from fodp.fodp_workflow import fodp_installed_workflow
        result = fodp_installed_workflow(str(_SAMPLE))
        assert isinstance(result["page_count"], int)

    def test_slide_count_is_integer(self):
        from fodp.fodp_workflow import fodp_installed_workflow
        result = fodp_installed_workflow(str(_SAMPLE))
        assert isinstance(result["slide_count"], int)

    def test_has_all_required_keys(self):
        from fodp.fodp_workflow import fodp_installed_workflow
        result = fodp_installed_workflow(str(_SAMPLE))
        assert {"format", "loaded", "page_count", "slide_count"}.issubset(result.keys())

    def test_page_count_positive(self):
        from fodp.fodp_workflow import fodp_installed_workflow
        result = fodp_installed_workflow(str(_SAMPLE))
        assert result["page_count"] >= 1

    def test_consistent_across_calls(self):
        from fodp.fodp_workflow import fodp_installed_workflow
        r1 = fodp_installed_workflow(str(_SAMPLE))
        r2 = fodp_installed_workflow(str(_SAMPLE))
        assert r1["page_count"] == r2["page_count"]

    def test_two_slides_doc(self):
        from fodp.fodp_workflow import fodp_installed_workflow
        result = fodp_installed_workflow(str(_TWO_SLIDES))
        assert result["loaded"] is True
        assert result["page_count"] >= 2
