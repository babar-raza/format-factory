"""
tests/python/pbm/test_r282_pbm_workflow.py

Sprint: ff-sprint-s282-pbm-installed-workflow-20260626
Authority: PBM bitmap image format (Netpbm)

Tests for pbm_installed_workflow() in pbm_workflow.py.
"""
from __future__ import annotations

from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
_SAMPLE = _REPO / "samples" / "by-format" / "pbm" / "valid" / "1x1-black.pbm"
_2x2 = _REPO / "samples" / "by-format" / "pbm" / "valid" / "2x2-checker.pbm"


class TestPbmInstalledWorkflowImport:
    def test_importable_from_pbm_workflow(self):
        from pbm.pbm_workflow import pbm_installed_workflow
        assert callable(pbm_installed_workflow)

    def test_importable_from_package(self):
        import pbm
        assert hasattr(pbm, "pbm_installed_workflow")


class TestPbmInstalledWorkflowOutput:
    def test_returns_dict(self):
        from pbm.pbm_workflow import pbm_installed_workflow
        assert isinstance(pbm_installed_workflow(str(_SAMPLE)), dict)

    def test_format_field(self):
        from pbm.pbm_workflow import pbm_installed_workflow
        assert pbm_installed_workflow(str(_SAMPLE))["format"] == "pbm"

    def test_loaded_true(self):
        from pbm.pbm_workflow import pbm_installed_workflow
        assert pbm_installed_workflow(str(_SAMPLE))["loaded"] is True

    def test_width_integer(self):
        from pbm.pbm_workflow import pbm_installed_workflow
        assert isinstance(pbm_installed_workflow(str(_SAMPLE))["width"], int)

    def test_height_integer(self):
        from pbm.pbm_workflow import pbm_installed_workflow
        assert isinstance(pbm_installed_workflow(str(_SAMPLE))["height"], int)

    def test_has_required_keys(self):
        from pbm.pbm_workflow import pbm_installed_workflow
        r = pbm_installed_workflow(str(_SAMPLE))
        assert {"format", "loaded", "width", "height", "pixel_count"}.issubset(r.keys())

    def test_1x1_dimensions(self):
        from pbm.pbm_workflow import pbm_installed_workflow
        r = pbm_installed_workflow(str(_SAMPLE))
        assert r["width"] == 1 and r["height"] == 1

    def test_2x2_image(self):
        from pbm.pbm_workflow import pbm_installed_workflow
        r = pbm_installed_workflow(str(_2x2))
        assert r["loaded"] is True and r["pixel_count"] >= 4

    def test_consistent(self):
        from pbm.pbm_workflow import pbm_installed_workflow
        r1 = pbm_installed_workflow(str(_SAMPLE))
        r2 = pbm_installed_workflow(str(_SAMPLE))
        assert r1["pixel_count"] == r2["pixel_count"]
