"""
tests/python/xcf/test_r278_xcf_workflow.py

Sprint: ff-sprint-s278-xcf-installed-workflow-20260626
Authority: XCF GIMP image format

Tests for xcf_installed_workflow() in xcf_workflow.py.
"""
from __future__ import annotations

from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_SAMPLE = _REPO / "samples" / "by-format" / "xcf" / "valid" / "1x1-red-rgb.xcf"
_2x2 = _REPO / "samples" / "by-format" / "xcf" / "valid" / "2x2-gray.xcf"


class TestXcfInstalledWorkflowImport:
    """xcf_installed_workflow is importable and callable."""

    def test_importable_from_xcf_workflow(self):
        from xcf.xcf_workflow import xcf_installed_workflow
        assert callable(xcf_installed_workflow)

    def test_importable_from_package(self):
        import xcf
        assert hasattr(xcf, "xcf_installed_workflow")


class TestXcfInstalledWorkflowOutput:
    """xcf_installed_workflow returns correct output structure."""

    def test_returns_dict(self):
        from xcf.xcf_workflow import xcf_installed_workflow
        result = xcf_installed_workflow(str(_SAMPLE))
        assert isinstance(result, dict)

    def test_format_field_is_xcf(self):
        from xcf.xcf_workflow import xcf_installed_workflow
        result = xcf_installed_workflow(str(_SAMPLE))
        assert result["format"] == "xcf"

    def test_loaded_field_is_true(self):
        from xcf.xcf_workflow import xcf_installed_workflow
        result = xcf_installed_workflow(str(_SAMPLE))
        assert result["loaded"] is True

    def test_width_is_integer(self):
        from xcf.xcf_workflow import xcf_installed_workflow
        result = xcf_installed_workflow(str(_SAMPLE))
        assert isinstance(result["width"], int)

    def test_height_is_integer(self):
        from xcf.xcf_workflow import xcf_installed_workflow
        result = xcf_installed_workflow(str(_SAMPLE))
        assert isinstance(result["height"], int)

    def test_layer_count_is_integer(self):
        from xcf.xcf_workflow import xcf_installed_workflow
        result = xcf_installed_workflow(str(_SAMPLE))
        assert isinstance(result["layer_count"], int)

    def test_has_all_required_keys(self):
        from xcf.xcf_workflow import xcf_installed_workflow
        result = xcf_installed_workflow(str(_SAMPLE))
        assert {"format", "loaded", "width", "height", "layer_count"}.issubset(result.keys())

    def test_1x1_dimensions(self):
        from xcf.xcf_workflow import xcf_installed_workflow
        result = xcf_installed_workflow(str(_SAMPLE))
        assert result["width"] == 1
        assert result["height"] == 1

    def test_2x2_image(self):
        from xcf.xcf_workflow import xcf_installed_workflow
        result = xcf_installed_workflow(str(_2x2))
        assert result["loaded"] is True
        assert result["width"] == 2
        assert result["height"] == 2

    def test_consistent_across_calls(self):
        from xcf.xcf_workflow import xcf_installed_workflow
        r1 = xcf_installed_workflow(str(_SAMPLE))
        r2 = xcf_installed_workflow(str(_SAMPLE))
        assert r1["width"] == r2["width"]
        assert r1["layer_count"] == r2["layer_count"]
