"""
tests/python/pgm/test_r283_pgm_workflow.py

Sprint: ff-sprint-s283-pgm-installed-workflow-20260626
Authority: PGM grayscale image format (Netpbm)

Tests for pgm_installed_workflow() in pgm_workflow.py.
"""
from __future__ import annotations

from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
_SAMPLE = _REPO / "samples" / "by-format" / "pgm" / "valid" / "1x1-white.pgm"
_2x2 = _REPO / "samples" / "by-format" / "pgm" / "valid" / "2x2-gradient.pgm"


class TestPgmInstalledWorkflowImport:
    def test_importable_from_pgm_workflow(self):
        from pgm.pgm_workflow import pgm_installed_workflow
        assert callable(pgm_installed_workflow)

    def test_importable_from_package(self):
        import pgm
        assert hasattr(pgm, "pgm_installed_workflow")


class TestPgmInstalledWorkflowOutput:
    def test_returns_dict(self):
        from pgm.pgm_workflow import pgm_installed_workflow
        assert isinstance(pgm_installed_workflow(str(_SAMPLE)), dict)

    def test_format_field(self):
        from pgm.pgm_workflow import pgm_installed_workflow
        assert pgm_installed_workflow(str(_SAMPLE))["format"] == "pgm"

    def test_loaded_true(self):
        from pgm.pgm_workflow import pgm_installed_workflow
        assert pgm_installed_workflow(str(_SAMPLE))["loaded"] is True

    def test_width_integer(self):
        from pgm.pgm_workflow import pgm_installed_workflow
        assert isinstance(pgm_installed_workflow(str(_SAMPLE))["width"], int)

    def test_height_integer(self):
        from pgm.pgm_workflow import pgm_installed_workflow
        assert isinstance(pgm_installed_workflow(str(_SAMPLE))["height"], int)

    def test_has_required_keys(self):
        from pgm.pgm_workflow import pgm_installed_workflow
        r = pgm_installed_workflow(str(_SAMPLE))
        assert {"format", "loaded", "width", "height", "pixel_count"}.issubset(r.keys())

    def test_1x1_dimensions(self):
        from pgm.pgm_workflow import pgm_installed_workflow
        r = pgm_installed_workflow(str(_SAMPLE))
        assert r["width"] == 1 and r["height"] == 1

    def test_2x2_image(self):
        from pgm.pgm_workflow import pgm_installed_workflow
        r = pgm_installed_workflow(str(_2x2))
        assert r["loaded"] is True and r["pixel_count"] >= 4

    def test_consistent(self):
        from pgm.pgm_workflow import pgm_installed_workflow
        r1 = pgm_installed_workflow(str(_SAMPLE))
        r2 = pgm_installed_workflow(str(_SAMPLE))
        assert r1["pixel_count"] == r2["pixel_count"]
