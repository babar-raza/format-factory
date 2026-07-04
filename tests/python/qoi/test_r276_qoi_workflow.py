"""
tests/python/qoi/test_r276_qoi_workflow.py

Sprint: ff-sprint-s276-qoi-installed-workflow-20260626
Authority: QOI image format

Tests for qoi_installed_workflow() in qoi_workflow.py.
"""
from __future__ import annotations

from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_SAMPLE = _REPO / "samples" / "by-format" / "qoi" / "valid" / "1x1-red.qoi"
_2x2 = _REPO / "samples" / "by-format" / "qoi" / "valid" / "2x2-black.qoi"


class TestQoiInstalledWorkflowImport:
    """qoi_installed_workflow is importable and callable."""

    def test_importable_from_qoi_workflow(self):
        from qoi.qoi_workflow import qoi_installed_workflow
        assert callable(qoi_installed_workflow)

    def test_importable_from_package(self):
        import qoi
        assert hasattr(qoi, "qoi_installed_workflow")


class TestQoiInstalledWorkflowOutput:
    """qoi_installed_workflow returns correct output structure."""

    def test_returns_dict(self):
        from qoi.qoi_workflow import qoi_installed_workflow
        result = qoi_installed_workflow(str(_SAMPLE))
        assert isinstance(result, dict)

    def test_format_field_is_qoi(self):
        from qoi.qoi_workflow import qoi_installed_workflow
        result = qoi_installed_workflow(str(_SAMPLE))
        assert result["format"] == "qoi"

    def test_loaded_field_is_true(self):
        from qoi.qoi_workflow import qoi_installed_workflow
        result = qoi_installed_workflow(str(_SAMPLE))
        assert result["loaded"] is True

    def test_width_is_integer(self):
        from qoi.qoi_workflow import qoi_installed_workflow
        result = qoi_installed_workflow(str(_SAMPLE))
        assert isinstance(result["width"], int)

    def test_height_is_integer(self):
        from qoi.qoi_workflow import qoi_installed_workflow
        result = qoi_installed_workflow(str(_SAMPLE))
        assert isinstance(result["height"], int)

    def test_channels_is_integer(self):
        from qoi.qoi_workflow import qoi_installed_workflow
        result = qoi_installed_workflow(str(_SAMPLE))
        assert isinstance(result["channels"], int)

    def test_has_all_required_keys(self):
        from qoi.qoi_workflow import qoi_installed_workflow
        result = qoi_installed_workflow(str(_SAMPLE))
        assert {"format", "loaded", "width", "height", "channels", "pixel_count"}.issubset(result.keys())

    def test_1x1_dimensions(self):
        from qoi.qoi_workflow import qoi_installed_workflow
        result = qoi_installed_workflow(str(_SAMPLE))
        assert result["width"] == 1
        assert result["height"] == 1

    def test_2x2_image(self):
        from qoi.qoi_workflow import qoi_installed_workflow
        result = qoi_installed_workflow(str(_2x2))
        assert result["loaded"] is True
        assert result["pixel_count"] >= 4

    def test_consistent_across_calls(self):
        from qoi.qoi_workflow import qoi_installed_workflow
        r1 = qoi_installed_workflow(str(_SAMPLE))
        r2 = qoi_installed_workflow(str(_SAMPLE))
        assert r1["width"] == r2["width"]
        assert r1["pixel_count"] == r2["pixel_count"]
