"""
tests/python/pbm/test_r306_pbm_iter_rasters.py

Sprint: ff-sprint-s306-pbm-raster-iterator-20260626
Authority: Netpbm format — PBM (Portable Bitmap) raster data

Tests for pbm_iter_rasters() in pbm_raster_iterator.py.
"""
from __future__ import annotations

from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
_VALID_DIR = _REPO / "samples" / "by-format" / "pbm" / "valid"
_MINIMAL = _VALID_DIR / "1x1-black.pbm"
_CHECKER = _VALID_DIR / "2x2-checker.pbm"


class TestPbmIterRastersImport:
    def test_importable_from_pbm_raster_iterator(self):
        from pbm.pbm_raster_iterator import pbm_iter_rasters
        assert callable(pbm_iter_rasters)

    def test_importable_from_package(self):
        import pbm
        assert hasattr(pbm, "pbm_iter_rasters")


class TestPbmIterRastersOutput:
    def test_returns_iterator(self):
        from pbm.pbm_raster_iterator import pbm_iter_rasters
        result = pbm_iter_rasters(str(_MINIMAL))
        assert hasattr(result, "__iter__") and hasattr(result, "__next__")

    def test_minimal_yields_one_raster(self):
        from pbm.pbm_raster_iterator import pbm_iter_rasters
        rasters = list(pbm_iter_rasters(str(_MINIMAL)))
        assert len(rasters) == 1

    def test_raster_type_is_spec_raster(self):
        from pbm.pbm_raster_iterator import pbm_iter_rasters
        from pbm.spec.bitmap.raster import Raster
        rasters = list(pbm_iter_rasters(str(_MINIMAL)))
        assert all(isinstance(r, Raster) for r in rasters)

    def test_raster_has_spec_qname(self):
        from pbm.pbm_raster_iterator import pbm_iter_rasters
        rasters = list(pbm_iter_rasters(str(_MINIMAL)))
        assert all(hasattr(r, "spec_qname") for r in rasters)

    def test_raster_qname_value(self):
        from pbm.pbm_raster_iterator import pbm_iter_rasters
        rasters = list(pbm_iter_rasters(str(_MINIMAL)))
        assert all(r.spec_qname == "pbm:raster" for r in rasters)

    def test_raster_dimensions(self):
        from pbm.pbm_raster_iterator import pbm_iter_rasters
        rasters = list(pbm_iter_rasters(str(_MINIMAL)))
        r = rasters[0]
        assert r.width == 1 and r.height == 1

    def test_raster_has_rows(self):
        from pbm.pbm_raster_iterator import pbm_iter_rasters
        rasters = list(pbm_iter_rasters(str(_MINIMAL)))
        r = rasters[0]
        assert isinstance(r.rows, list) and len(r.rows) == r.height

    def test_checker_dimensions(self):
        from pbm.pbm_raster_iterator import pbm_iter_rasters
        rasters = list(pbm_iter_rasters(str(_CHECKER)))
        r = rasters[0]
        assert r.width == 2 and r.height == 2

    def test_consistent(self):
        from pbm.pbm_raster_iterator import pbm_iter_rasters
        r1 = [(r.width, r.height) for r in pbm_iter_rasters(str(_MINIMAL))]
        r2 = [(r.width, r.height) for r in pbm_iter_rasters(str(_MINIMAL))]
        assert r1 == r2
