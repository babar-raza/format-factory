"""
tests/python/pgm/test_r307_pgm_iter_graymaps.py

Sprint: ff-sprint-s307-pgm-graymap-iterator-20260626
Authority: Netpbm format — PGM (Portable Graymap) pixel data

Tests for pgm_iter_graymaps() in pgm_graymap_iterator.py.
"""
from __future__ import annotations

from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
_VALID_DIR = _REPO / "samples" / "by-format" / "pgm" / "valid"
_MINIMAL = _VALID_DIR / "1x1-white.pgm"
_GRADIENT = _VALID_DIR / "2x2-gradient.pgm"


class TestPgmIterGraymapsImport:
    def test_importable_from_pgm_graymap_iterator(self):
        from pgm.pgm_graymap_iterator import pgm_iter_graymaps
        assert callable(pgm_iter_graymaps)

    def test_importable_from_package(self):
        import pgm
        assert hasattr(pgm, "pgm_iter_graymaps")


class TestPgmIterGraymapsOutput:
    def test_returns_iterator(self):
        from pgm.pgm_graymap_iterator import pgm_iter_graymaps
        result = pgm_iter_graymaps(str(_MINIMAL))
        assert hasattr(result, "__iter__") and hasattr(result, "__next__")

    def test_minimal_yields_one_graymap(self):
        from pgm.pgm_graymap_iterator import pgm_iter_graymaps
        gms = list(pgm_iter_graymaps(str(_MINIMAL)))
        assert len(gms) == 1

    def test_graymap_type_is_spec_graymap(self):
        from pgm.pgm_graymap_iterator import pgm_iter_graymaps
        from pgm.spec.graymap.graymap import Graymap
        gms = list(pgm_iter_graymaps(str(_MINIMAL)))
        assert all(isinstance(g, Graymap) for g in gms)

    def test_graymap_has_spec_qname(self):
        from pgm.pgm_graymap_iterator import pgm_iter_graymaps
        gms = list(pgm_iter_graymaps(str(_MINIMAL)))
        assert all(hasattr(g, "spec_qname") for g in gms)

    def test_graymap_qname_value(self):
        from pgm.pgm_graymap_iterator import pgm_iter_graymaps
        gms = list(pgm_iter_graymaps(str(_MINIMAL)))
        assert all(g.spec_qname == "pgm:graymap" for g in gms)

    def test_graymap_dimensions(self):
        from pgm.pgm_graymap_iterator import pgm_iter_graymaps
        gms = list(pgm_iter_graymaps(str(_MINIMAL)))
        g = gms[0]
        assert g.width == 1 and g.height == 1

    def test_gradient_dimensions(self):
        from pgm.pgm_graymap_iterator import pgm_iter_graymaps
        gms = list(pgm_iter_graymaps(str(_GRADIENT)))
        g = gms[0]
        assert g.width == 2 and g.height == 2

    def test_consistent(self):
        from pgm.pgm_graymap_iterator import pgm_iter_graymaps
        r1 = [(g.width, g.height) for g in pgm_iter_graymaps(str(_MINIMAL))]
        r2 = [(g.width, g.height) for g in pgm_iter_graymaps(str(_MINIMAL))]
        assert r1 == r2
