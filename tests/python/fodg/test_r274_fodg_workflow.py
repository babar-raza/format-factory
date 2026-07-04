"""
tests/python/fodg/test_r274_fodg_workflow.py

Sprint: ff-sprint-s274-fodg-installed-workflow-20260626
Authority: ODF FODG drawing format

Tests for fodg_installed_workflow() in fodg_workflow.py.
"""
from __future__ import annotations

from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_SAMPLE = _REPO / "samples" / "by-format" / "fodg" / "minimal-drawing.fodg"
_SHAPES = _REPO / "samples" / "by-format" / "fodg" / "shapes-basic.fodg"


class TestFodgInstalledWorkflowImport:
    """fodg_installed_workflow is importable and callable."""

    def test_importable_from_fodg_workflow(self):
        from fodg.fodg_workflow import fodg_installed_workflow
        assert callable(fodg_installed_workflow)

    def test_importable_from_package(self):
        import fodg
        assert hasattr(fodg, "fodg_installed_workflow")


class TestFodgInstalledWorkflowOutput:
    """fodg_installed_workflow returns correct output structure."""

    def test_returns_dict(self):
        from fodg.fodg_workflow import fodg_installed_workflow
        result = fodg_installed_workflow(str(_SAMPLE))
        assert isinstance(result, dict)

    def test_format_field_is_fodg(self):
        from fodg.fodg_workflow import fodg_installed_workflow
        result = fodg_installed_workflow(str(_SAMPLE))
        assert result["format"] == "fodg"

    def test_loaded_field_is_true(self):
        from fodg.fodg_workflow import fodg_installed_workflow
        result = fodg_installed_workflow(str(_SAMPLE))
        assert result["loaded"] is True

    def test_page_count_is_integer(self):
        from fodg.fodg_workflow import fodg_installed_workflow
        result = fodg_installed_workflow(str(_SAMPLE))
        assert isinstance(result["page_count"], int)

    def test_shape_count_is_integer(self):
        from fodg.fodg_workflow import fodg_installed_workflow
        result = fodg_installed_workflow(str(_SAMPLE))
        assert isinstance(result["shape_count"], int)

    def test_has_all_required_keys(self):
        from fodg.fodg_workflow import fodg_installed_workflow
        result = fodg_installed_workflow(str(_SAMPLE))
        assert {"format", "loaded", "page_count", "shape_count"}.issubset(result.keys())

    def test_page_count_positive(self):
        from fodg.fodg_workflow import fodg_installed_workflow
        result = fodg_installed_workflow(str(_SAMPLE))
        assert result["page_count"] >= 1

    def test_consistent_across_calls(self):
        from fodg.fodg_workflow import fodg_installed_workflow
        r1 = fodg_installed_workflow(str(_SAMPLE))
        r2 = fodg_installed_workflow(str(_SAMPLE))
        assert r1["page_count"] == r2["page_count"]
        assert r1["shape_count"] == r2["shape_count"]

    def test_shapes_basic_doc(self):
        from fodg.fodg_workflow import fodg_installed_workflow
        result = fodg_installed_workflow(str(_SHAPES))
        assert result["loaded"] is True
        assert result["shape_count"] >= 1
