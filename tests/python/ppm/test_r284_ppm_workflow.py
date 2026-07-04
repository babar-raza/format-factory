"""
tests/python/ppm/test_r284_ppm_workflow.py

Sprint: ff-sprint-s284-ppm-installed-workflow-20260626
Authority: PPM color image format (Netpbm)

Tests for ppm_installed_workflow() in ppm_workflow.py.
"""
from __future__ import annotations

from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
_SAMPLE = _REPO / "samples" / "by-format" / "ppm" / "valid" / "1x1-red.ppm"
_2x2 = _REPO / "samples" / "by-format" / "ppm" / "valid" / "2x2-rgbw.ppm"


class TestPpmInstalledWorkflowImport:
    def test_importable_from_ppm_workflow(self):
        from ppm.ppm_workflow import ppm_installed_workflow
        assert callable(ppm_installed_workflow)

    def test_importable_from_package(self):
        import ppm
        assert hasattr(ppm, "ppm_installed_workflow")


class TestPpmInstalledWorkflowOutput:
    def test_returns_dict(self):
        from ppm.ppm_workflow import ppm_installed_workflow
        assert isinstance(ppm_installed_workflow(str(_SAMPLE)), dict)

    def test_format_field(self):
        from ppm.ppm_workflow import ppm_installed_workflow
        assert ppm_installed_workflow(str(_SAMPLE))["format"] == "ppm"

    def test_loaded_true(self):
        from ppm.ppm_workflow import ppm_installed_workflow
        assert ppm_installed_workflow(str(_SAMPLE))["loaded"] is True

    def test_width_integer(self):
        from ppm.ppm_workflow import ppm_installed_workflow
        assert isinstance(ppm_installed_workflow(str(_SAMPLE))["width"], int)

    def test_height_integer(self):
        from ppm.ppm_workflow import ppm_installed_workflow
        assert isinstance(ppm_installed_workflow(str(_SAMPLE))["height"], int)

    def test_has_required_keys(self):
        from ppm.ppm_workflow import ppm_installed_workflow
        r = ppm_installed_workflow(str(_SAMPLE))
        assert {"format", "loaded", "width", "height", "pixel_count"}.issubset(r.keys())

    def test_1x1_dimensions(self):
        from ppm.ppm_workflow import ppm_installed_workflow
        r = ppm_installed_workflow(str(_SAMPLE))
        assert r["width"] == 1 and r["height"] == 1

    def test_2x2_image(self):
        from ppm.ppm_workflow import ppm_installed_workflow
        r = ppm_installed_workflow(str(_2x2))
        assert r["loaded"] is True and r["pixel_count"] >= 4

    def test_consistent(self):
        from ppm.ppm_workflow import ppm_installed_workflow
        r1 = ppm_installed_workflow(str(_SAMPLE))
        r2 = ppm_installed_workflow(str(_SAMPLE))
        assert r1["pixel_count"] == r2["pixel_count"]
